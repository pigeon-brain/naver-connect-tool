"""Npay-owned device backup: RAM mode transition, then read-only eMMC dump.
No seccfg, flash-write, erase, format, or relock operations.
"""
import argparse
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import struct
import sys
import time
import zlib

BASE = Path(__file__).resolve().parent
REPO = Path(os.environ.get('CONNECT_MTK_REPO', str(BASE / 'vendor/mtkclient'))).resolve()
sys.path.insert(0, str(REPO))
from mtkclient.config.mtk_config import MtkConfig
from mtkclient.Library.mtk_class import Mtk
from mtkclient.Library.pltools import PLTools
from mtkclient.Library.Partitions.gpt import GptSettings
import usb.core


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def read_preloader(mtk):
    """Read only the header-declared, bounded RAM image; reject short reads."""
    def read(addr, count):
        values = mtk.preloader.read32(addr, count // 4)
        if not isinstance(values, (list, tuple)) or len(values) != count // 4:
            raise RuntimeError('Short RAM read')
        return b''.join(struct.pack('<I', value) for value in values)
    head = read(0x200000, 0x10000)
    offset = head.find(bytes.fromhex('4d4d4d0138000000'))
    if offset < 0 or offset + 0x24 > len(head):
        raise RuntimeError('RAM preloader header unavailable')
    length = struct.unpack_from('<I', head, offset + 0x20)[0]
    if not 1024 < length < 16 * 1024 * 1024:
        raise RuntimeError('Invalid RAM preloader declared length')
    data = bytearray()
    for position in range(0, length, 512):
        size = min(512, length - position)
        data.extend(read(0x200000 + offset + position, (size + 3) & ~3)[:size])
    return bytes(data)


def verify_gpt(raw):
    if raw[512:520]!=b'EFI PART':raise RuntimeError('GPT signature missing')
    header_size=struct.unpack_from('<I',raw,524)[0]
    if not 92<=header_size<=512:raise RuntimeError('GPT header size invalid')
    header=bytearray(raw[512:512+header_size]);expected=struct.unpack_from('<I',header,16)[0]
    header[16:20]=bytes(4)
    if zlib.crc32(header)&0xffffffff!=expected:raise RuntimeError('GPT header CRC mismatch')
    start=struct.unpack_from('<Q',raw,584)[0]*512
    count,size,crc=struct.unpack_from('<III',raw,592)
    if not 1<=count<=4096 or size<128 or size%8 or start+count*size>len(raw):raise RuntimeError('GPT entries bounds invalid')
    if zlib.crc32(raw[start:start+count*size])&0xffffffff!=crc:raise RuntimeError('GPT entries CRC mismatch')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run', action='store_true', required=True)
    ap.add_argument('--backup-dir', type=Path, required=True)
    args = ap.parse_args()
    stamp = time.strftime('%Y%m%d-%H%M%S')
    out = args.backup_dir.resolve()
    if out.exists():raise RuntimeError('Choose a new backup directory; overwrite forbidden')
    out.mkdir(parents=True)
    local = out / 'device-info'
    local.mkdir()
    loader = REPO / 'mtkclient/Loader/MTK_DA_V5.bin'
    if digest(loader) != 'aef234190ccb8145d2e3b8459741e9adb70f2caa8481aa216c1b25152afaca1f':raise RuntimeError('Unverified DA loader')
    if digest(REPO/'mtkclient/payloads/mt6768_payload.bin')!='1374139e112b7961abf6571582c8330d879d956ff33ed39bd51c882ddec8a6c5':raise RuntimeError('Unverified RAM payload')
    os.chdir(REPO)
    print('BACKUP DIRECTORY:', out, flush=True)
    def config(pid):
        c = MtkConfig(loglevel=logging.INFO)
        c.vid, c.pid = 0x0e8d, pid
        c.skipwdt = True
        c.stock = True
        c.loader = str(REPO / 'mtkclient/Loader/MTK_DA_V5.bin')
        c.gpt_settings = GptSettings(0,0,0)
        c.hwparam_path = str(local)
        return c
    active = None
    status = {'stage':'waiting', 'complete':False, 'files':[],
              'coverage':['emmc boot1','emmc boot2','emmc user'],
              'not_backed_up':['RPMB','GP partitions','external secure element','server-side registration'],
              'restoration_tested':False}
    def save():
        (out/'session-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    save()
    try:
        # Both IDs must have WinUSB staged before starting this session.
        brom = Mtk(config(3))
        def brom_present():
            return usb.core.find(idVendor=0x0e8d, idProduct=3,
                                 backend=brom.port.cdc.backend) is not None
        if not brom_present():
            active = Mtk(config(0x2000))
            from preloader_handshake import install
            install(active.port)
            if not active.preloader.init(directory=str(local)):
                raise RuntimeError('Preloader handshake failed')
            if active.config.hwcode != 0x707:
                raise RuntimeError('Unexpected hardware code; stopped')
            status['stage']='brom-transition'; save()
            PLTools(active).crash(0)
            active.port.close()
            end = time.monotonic()+20
            while time.monotonic()<end:
                if brom_present():
                    break
                time.sleep(.03)
        if not brom_present():
            raise RuntimeError('BROM USB did not appear')
        status['stage']='brom-usb-discovered'; save()
        print('BROM USB discovered; verifying handshake', flush=True)
        active = brom
        if not active.preloader.init(directory=str(local)) or not active.config.is_brom:
            raise RuntimeError('BROM handshake not confirmed')
        if active.config.hwcode != 0x707:
            raise RuntimeError('Unexpected BROM hardware')
        status.update(stage='brom-connected', hwcode=active.config.hwcode,
                      target_config=active.config.target_config)
        save()
        if any(active.config.target_config.get(k) for k in ('memread','memwrite','sbc','sla','daa')):
            status['stage']='ram-access-session'; save()
            # mtkclient's existing MT6768 RAM-only access path. No flash patching.
            active = active.bypass_security()
            if not active.daloader.patch:
                raise RuntimeError('RAM access session not established')
        addr,value=active.config.get_watchdog_addr()
        if (addr,value)!=(0x10007000,0x22000064):raise RuntimeError('Unexpected watchdog configuration')
        before=active.preloader.read32(addr)
        if not isinstance(before,int):raise RuntimeError('Unreadable watchdog')
        if before & 1:
            if not active.preloader.setreg_disablewatchdogtimer(active.config.hwcode,active.config.hwver):raise RuntimeError('Watchdog setup failed')
            after=active.preloader.read32(addr)
            if not isinstance(after,int) or after & 1:raise RuntimeError('Watchdog verification failed')
        status['stage']='ram-preloader'; save()
        preloader = read_preloader(active)
        if not preloader or not (1024<len(preloader)<16*1024*1024):
            raise RuntimeError('No valid same-device RAM preloader')
        (local/'preloader-ram.bin').write_bytes(preloader)
        (out/'preloader-ram.bin').write_bytes(preloader)
        active.config.preloader=preloader
        # Keep the original DA bytes; only the current RAM session was adjusted.
        active.daloader.patch=False
        status['stage']='stock-da'; save()
        if not active.daloader.upload_da(preloader=preloader):
            raise RuntimeError('Stock DA rejected')
        raw, table = active.daloader.get_gpt()
        if not raw or table is None or not getattr(table,'partentries',None):
            raise RuntimeError('GPT unavailable')
        entries_start=struct.unpack_from('<Q',raw,584)[0]*512
        entry_count,entry_size=struct.unpack_from('<II',raw,592)
        total=entries_start+entry_count*entry_size
        if not 1024<=total<=1024*1024:raise RuntimeError('GPT read bounds invalid')
        full=active.daloader.readflash(addr=0,length=(total+511)//512*512,filename='',parttype='user',display=False)
        if not isinstance(full,(bytes,bytearray)) or not bytes(full).startswith(raw):raise RuntimeError('GPT reread differs')
        raw=bytes(full);verify_gpt(raw)
        (out/'gpt-read.bin').write_bytes(raw)
        entries=[{'name':p.name,'sector':p.sector,'sectors':p.sectors} for p in table.partentries]
        storage=active.daloader.daconfig.storage
        if storage.flashtype!='emmc':
            raise RuntimeError('Unexpected storage type')
        sizes={'boot1':storage.emmc.boot1_size,'boot2':storage.emmc.boot2_size,'user':storage.emmc.user_size}
        if any(not isinstance(v,int) or v<=0 for v in sizes.values()):
            raise RuntimeError('Invalid storage sizes')
        status.update(stage='gpt-parsed',sizes=sizes,partitions=entries, cid=storage.emmc.cid.hex(),gpt_crc_verified=True, artifacts=[{'path':name,'bytes':(out/name).stat().st_size,'sha256':digest(out/name)} for name in ('preloader-ram.bin','gpt-read.bin')])
        save()
        if shutil.disk_usage(out).free < sum(sizes.values())+1024**3:
            raise RuntimeError('Insufficient NAS space')
        for region,length in sizes.items():
            status['stage']='reading-'+region; save()
            path=out/(region+'.bin.partial')
            ok=active.daloader.readflash(addr=0,length=length,filename=str(path),parttype=region,display=True)
            if not ok or not path.is_file() or path.stat().st_size!=length:
                raise RuntimeError('Incomplete dump: '+region)
            first=digest(path)
            if digest(path)!=first:
                raise RuntimeError('NAS readback mismatch')
            final=out/(region+'.bin')
            path.rename(final)
            status['files'].append({'path':final.name,'bytes':length,'sha256':first})
            save()
        status.update(stage='dump-files-verified',complete=True)
        save()
        print('Dump files verified; restoration itself remains untested.',flush=True)
    except BaseException as exc:
        status.update(error=str(exc),complete=False)
        save()
        raise
    finally:
        if active:
            active.port.close()


if __name__=='__main__':
    main()
