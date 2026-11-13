"""Validate same-device seccfg, use upstream unlock, verify whole partition, then fastboot.
Only the verified 512-byte seccfg record is allowed to be written.
"""
from pathlib import Path
import argparse,json,logging,sys,time,hashlib,subprocess
from struct import pack
BASE=Path(__file__).resolve().parent
from mtk_backup import MtkConfig,Mtk,PLTools,GptSettings,read_preloader,usb
from preloader_handshake import install as install_preloader_handshake


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--wait-for-cycle',action='store_true');parser.add_argument('--backup-dir',type=Path,required=True);args=parser.parse_args()
 if not args.execute: print('No USB operation. --execute authorizes validated seccfg unlock and fastboot entry.');return
 BACKUP=args.backup_dir.resolve()
 from connect import load_stock_records,verify_entries
 from mtk_backup import REPO,digest,verify_gpt
 records=load_stock_records(BACKUP);verify_entries(BACKUP,records)
 backup=json.loads((BACKUP/'session-status.json').read_text(encoding='utf-8-sig'))
 if not backup.get('cid') or backup.get('hwcode')!=0x707:raise RuntimeError('Backup device identity missing')
 expected=backup['cid']
 expected_gpt={'partitions':[{'name':p['name'],'offset':p['sector']*512,'bytes':p['sectors']*512} for p in backup['partitions']]}
 part=next(p for p in expected_gpt['partitions'] if p['name']=='seccfg')
 if part['bytes']!=8388608 or part['offset']+part['bytes']>records['user.bin'][0]:raise RuntimeError('Unexpected seccfg bounds')
 with (BACKUP/'user.bin').open('rb') as handle:
  handle.seek(part['offset']);original=handle.read(part['bytes'])
 for artifact in backup.get('artifacts',[]):
  if artifact['path'] not in ('preloader-ram.bin','gpt-read.bin'):raise RuntimeError('Unexpected artifact')
  if digest(BACKUP/artifact['path'])!=artifact['sha256']:raise RuntimeError('Backup artifact hash mismatch')
 if {a['path'] for a in backup.get('artifacts',[])}!={'preloader-ram.bin','gpt-read.bin'}:raise RuntimeError('Backup artifacts missing')
 expected_preloader_digest=hashlib.sha256((BACKUP/'preloader-ram.bin').read_bytes()).digest()
 expected_gpt_raw=(BACKUP/'gpt-read.bin').read_bytes()
 verify_gpt(expected_gpt_raw)
 if digest(REPO/'mtkclient/payloads/mt6768_payload.bin')!='1374139e112b7961abf6571582c8330d879d956ff33ed39bd51c882ddec8a6c5':raise RuntimeError('Unverified RAM payload')
 extension=REPO/'mtkclient/payloads/da_x.bin'
 if digest(extension)!='b83ebbbff36e330713080e719856241065e51f732658f4b931399df0e17e00fd':raise RuntimeError('DA extension hash mismatch')
 loader=REPO/'mtkclient/Loader/MTK_DA_V5.bin'
 if digest(loader)!='aef234190ccb8145d2e3b8459741e9adb70f2caa8481aa216c1b25152afaca1f':raise RuntimeError('DA loader hash mismatch')
 out=BASE/'logs'/time.strftime('%Y%m%d-%H%M%S-unlock');out.mkdir(parents=True,exist_ok=False)
 state={'stage':'waiting','flash_write':False,'unlock':False,'log_directory':str(out)}
 def save(stage):
  state['stage']=stage;state['updated_at']=time.strftime('%Y-%m-%d %H:%M:%S');state['monotonic_seconds']=time.monotonic();(BASE/'active-unlock.json').write_text(json.dumps(state,indent=2));(out/'status.json').write_text(json.dumps(state,indent=2));print(stage,flush=True)
 def cfg(pid):
  c=MtkConfig(loglevel=logging.INFO);c.vid=0x0e8d;c.pid=pid;c.skipwdt=True;c.stock=False;c.generatekeys=False
  c.loader=str(loader);c.gpt_settings=GptSettings(0,0,0);c.hwparam_path=str(out);return c
 active=None
 try:
  brom=Mtk(cfg(3));present=lambda:usb.core.find(idVendor=0x0e8d,idProduct=3,backend=brom.port.cdc.backend) is not None
  save('waiting-for-power-cycle' if args.wait_for_cycle else 'waiting')
  if args.wait_for_cycle:
   while present() or usb.core.find(idVendor=0x0e8d,idProduct=0x2000,backend=brom.port.cdc.backend) is not None:time.sleep(.1)
   save('waiting')
  if not present():
   active=Mtk(cfg(0x2000));install_preloader_handshake(active.port)
   if not active.preloader.init(directory=str(out)) or active.config.hwcode!=0x707:raise RuntimeError('Preloader identity not confirmed')
   save('brom-transition');PLTools(active).crash(0);active.port.close()
   end=time.monotonic()+25
   while time.monotonic()<end and not present():time.sleep(.05)
  if not present():raise RuntimeError('BROM not enumerated')
  active=brom
  if not active.preloader.init(directory=str(out)) or not active.config.is_brom or active.config.hwcode!=0x707:raise RuntimeError('BROM identity not confirmed')
  save('ram-session')
  if any(active.config.target_config.get(k) for k in ('memread','memwrite','sbc','sla','daa')):
   active=active.bypass_security()
   if not active.daloader.patch:raise RuntimeError('RAM session unavailable')
  save('watchdog-check')
  addr,value=active.config.get_watchdog_addr()
  if addr!=0x10007000 or value!=0x22000064:raise RuntimeError('Unexpected watchdog configuration')
  before=active.preloader.read32(addr)
  if not isinstance(before,int):raise RuntimeError('Watchdog register unreadable')
  state['watchdog_before']=hex(before)
  if before & 1:
   if not active.preloader.setreg_disablewatchdogtimer(active.config.hwcode,active.config.hwver):raise RuntimeError('Watchdog disable not acknowledged')
   after=active.preloader.read32(addr)
   if not isinstance(after,int) or after & 1:raise RuntimeError('Watchdog disable readback failed')
   state['watchdog_after']=hex(after);state['watchdog_register_updated']=True
  else:state['watchdog_register_updated']=False
  save('ram-preloader')
  preloader=read_preloader(active)
  if hashlib.sha256(preloader).digest()!=expected_preloader_digest:raise RuntimeError('RAM preloader differs from backup')
  active.config.preloader=preloader;active.daloader.patch=True;save('extended-da')
  from mtkclient.Library.DA.xflash.xflash_lib import DAXFlash
  original_send_emi=DAXFlash.send_emi
  def traced_send_emi(da,emi):
   state['emi_bytes']=len(emi);state['emi_sha256']=hashlib.sha256(emi).hexdigest();save('sending-emi')
   ok=original_send_emi(da,emi);state['emi_completed']=bool(ok);save('emi-response-returned');return ok
  DAXFlash.send_emi=traced_send_emi
  if not active.daloader.upload_da(preloader=preloader):raise RuntimeError('Extended DA failed')
  raw,gpt=active.daloader.get_gpt()
  if not raw or gpt is None or not expected_gpt_raw.startswith(raw):raise RuntimeError('Raw GPT differs or unavailable')
  full=active.daloader.readflash(addr=0,length=len(expected_gpt_raw),filename='',parttype='user',display=False)
  if full!=expected_gpt_raw:raise RuntimeError('Full GPT differs from backup')
  verify_gpt(full)
  actual=[{'name':p.name,'offset':p.sector*512,'bytes':p.sectors*512} for p in gpt.partentries]
  if actual!=expected_gpt['partitions']:raise RuntimeError('GPT differs from backup')
  emmc=active.daloader.daconfig.storage.emmc
  if emmc.cid.hex().lower()!=expected.lower():raise RuntimeError('eMMC identity differs')
  part=next(p for p in actual if p['name']=='seccfg')
  current=active.daloader.readflash(addr=part['offset'],length=part['bytes'],filename='',parttype='user',display=False)
  if current!=original:raise RuntimeError('Live seccfg differs from locked backup')
  (out/'seccfg-live.bin').write_bytes(current);state['identity_and_gpt_match']=True
  from mtkclient.Library.Hardware.seccfg import SecCfgV4
  da=active.daloader.da
  if not da.daext:raise RuntimeError('Required DA extension acknowledgement missing')
  if active.daloader.daconfig.pagesize!=512:raise RuntimeError('Unexpected sector size')
  ext=da.xft;hwc=ext.cryptosetup();record=SecCfgV4(hwc,active,ext.custom_sej_hw)
  save('validating-seccfg')
  if not record.parse(current):raise RuntimeError('Original seccfg cryptographic verification failed')
  if (record.seccfg_ver,record.seccfg_size,record.lock_state,record.dm_verity_state,record.sboot_runtime)!=(4,60,1,0,0):raise RuntimeError('Unexpected seccfg fields')
  state['seccfg_hwtype']=record.hwtype
  ok,candidate=record.create(lockflag='unlock',critical=False)
  if not ok or len(candidate)!=512:raise RuntimeError('Unsupported unlock record')
  candidate=bytes(candidate)
  expected_after=candidate+current[512:]
  verify=SecCfgV4(hwc,active,ext.custom_sej_hw)
  if not verify.parse(expected_after) or verify.lock_state!=3 or verify.dm_verity_state!=0:raise RuntimeError('Generated unlock record failed validation')
  if candidate[:12]!=current[:12] or candidate[16:28]!=current[16:28] or candidate[60:]!=current[60:512]:raise RuntimeError('Unexpected non-lock record change')
  (out/'seccfg-candidate-sector.bin').write_bytes(candidate)
  state['expected_seccfg_sha256']=hashlib.sha256(expected_after).hexdigest()
  state['original_seccfg_sha256']=hashlib.sha256(current).hexdigest()
  nasout=BACKUP/'unlock-sessions'/out.name;nasout.mkdir(parents=True,exist_ok=False)
  (nasout/'seccfg-before.bin').write_bytes(current)
  (nasout/'candidate-sector.bin').write_bytes(candidate)
  if (nasout/'seccfg-before.bin').read_bytes()!=current or (nasout/'candidate-sector.bin').read_bytes()!=candidate:raise RuntimeError('Pre-write NAS verification failed')
  write_original=da.writeflash;write_count=0
  def guarded_write(**kw):
   nonlocal write_count
   if write_count or kw.get('addr')!=part['offset'] or kw.get('length')!=512 or kw.get('parttype')!='user' or kw.get('filename')!='' or bytes(kw.get('wdata',b''))!=candidate:raise RuntimeError('Refusing out-of-scope flash write')
   write_count+=1;state['flash_write']=True;save('writing-verified-seccfg-sector')
   return write_original(**kw)
  da.writeflash=guarded_write
  save('unlock-validation-passed')
  ok,message=ext.seccfg('unlock',critical=False)
  da.writeflash=write_original
  state['unlock_command_message']=message
  if not ok:raise RuntimeError('Unlock command failed: '+str(message))
  save('verifying-seccfg-readback')
  after=active.daloader.readflash(addr=part['offset'],length=part['bytes'],filename='',parttype='user',display=False)
  if not isinstance(after,(bytes,bytearray)) or len(after)!=len(current):raise RuntimeError('Incomplete unlock readback; stop without reboot')
  (out/'seccfg-after.bin').write_bytes(after);(nasout/'seccfg-after.bin').write_bytes(after)
  if after!=expected_after:raise RuntimeError('Readback mismatch; stop without reboot')
  if not verify.parse(after) or verify.lock_state!=3:raise RuntimeError('Readback cryptographic verification failed')
  state['unlock']=True;state['readback_verified']=True;save('unlock-verified')
  (nasout/'result.json').write_text(json.dumps(state,indent=2))
  save('unlock-verified-awaiting-preloader-fastboot')
  print('Unlock readback verified. Close this session, prepare direct Fastboot entry, then power-cycle once. DA shutdown is not a verified Fastboot route on this device.',flush=True)
 except BaseException as e:state['error']=str(e);save('stopped');raise
 finally:
  if active:active.port.close()

if __name__=='__main__':main()
