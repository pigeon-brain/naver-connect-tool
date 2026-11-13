"""Verified Connect GSI installation; explicit userdata-erasure consent required."""
import argparse,hashlib,json,re,subprocess,time
from pathlib import Path
from connect import fastboot_path,load_stock_records,verify_entries,getvar,list_fastboot
IMAGE_HASH='ad4d00d5b865c35964033c7ac8aaf e74c67a1921b7fcd3f9491df643ac17fd8f'.replace(' ','')
IMAGE_SIZE=2623557632

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()

def run_install(args):
 backup=args.backup_dir.resolve();image=args.image.resolve();vbmeta=args.vbmeta.resolve()
 if not args.erase_userdata:raise ValueError('Userdata erasure authorization required')
 if not re.fullmatch(r'[A-Za-z0-9_.:-]{1,128}',args.serial):raise ValueError('Invalid serial')
 if image.stat().st_size!=IMAGE_SIZE or sha(image)!=IMAGE_HASH:raise ValueError('Unverified GSI image')
 records=load_stock_records(backup);verify_entries(backup,records)
 status=json.loads((backup/'session-status.json').read_text(encoding='utf-8-sig'))
 part=next(p for p in status['partitions'] if p['name']=='vbmeta_a')
 with (backup/'user.bin').open('rb') as f:
  f.seek(part['sector']*512);original=f.read(part['sectors']*512)
 if not original or vbmeta.read_bytes()!=original:raise ValueError('vbmeta does not match selected stock backup')
 fb=fastboot_path(args.fastboot)
 out=Path(__file__).resolve().parent/'logs'/time.strftime('%Y%m%d-%H%M%S-install');out.mkdir(parents=True,exist_ok=False)
 state={'serial':args.serial,'stage':'preflight','android_boot_confirmed':False}
 def save(stage):
  state['stage']=stage;(out/'status.json').write_text(json.dumps(state,indent=2),encoding='utf-8');print(stage,flush=True)
 def run(*cmd,timeout=30):
  proc=subprocess.run([str(fb),'-s',args.serial,*cmd],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
  with (out/'commands.log').open('a',encoding='utf-8') as f:f.write(json.dumps(list(cmd))+'\n'+proc.stdout+proc.stderr+'\n')
  print(proc.stdout+proc.stderr,flush=True)
  if proc.returncode:raise RuntimeError('Fastboot command failed; subsequent writes stopped')
 def require(name,value):
  actual=getvar(fb,args.serial,name)
  if actual!=value:raise ValueError(f'{name}: expected {value}, got {actual}')
 def connected():
  if list_fastboot(fb)!=[args.serial]:raise ValueError('Expected exactly the selected device')
 def wait_mode(userspace):
  deadline=time.monotonic()+120
  while time.monotonic()<deadline:
   if list_fastboot(fb)==[args.serial] and getvar(fb,args.serial,'is-userspace')==userspace:return
   time.sleep(1)
  raise TimeoutError('USB transition timeout; check mode-specific driver')
 try:
  connected();require('unlocked','yes');require('current-slot','a')
  mode=getvar(fb,args.serial,'is-userspace')
  if mode=='no':
   save('entering-fastbootd');run('reboot','fastboot',timeout=120);wait_mode('yes')
  elif mode!='yes':raise ValueError('Unknown boot mode')
  connected();require('unlocked','yes');require('current-slot','a');require('is-userspace','yes');require('snapshot-update-status','none');require('is-logical:system_a','yes')
  if int(getvar(fb,args.serial,'partition-size:system_a'),16)!=1679482880:raise ValueError('Not the verified original system_a size; automatic resume forbidden')
  if int(getvar(fb,args.serial,'partition-size:super'),16)!=9663676416:raise ValueError('Unexpected super size')
  save('resizing-system');run('resize-logical-partition','system_a',str(IMAGE_SIZE))
  if int(getvar(fb,args.serial,'partition-size:system_a'),16)!=IMAGE_SIZE:raise RuntimeError('Resize readback mismatch')
  save('flashing-system');run('-S','128M','flash','system_a',str(image),timeout=1800)
  save('formatting-userdata');run('format:f2fs','userdata',timeout=180)
  save('entering-bootloader');run('reboot','bootloader',timeout=120);wait_mode('no')
  connected();require('unlocked','yes');require('current-slot','a');require('is-userspace','no')
  save('flashing-vbmeta');run('--disable-verity','--disable-verification','flash','vbmeta_a',str(vbmeta),timeout=120)
  save('rebooting');run('reboot');save('first-boot-awaiting-user-confirmation')
 except BaseException as exc:
  state['error']=str(exc);save('stopped');raise

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--serial',required=True);p.add_argument('--backup-dir',type=Path,required=True)
 p.add_argument('--image',type=Path,required=True);p.add_argument('--vbmeta',type=Path,required=True)
 p.add_argument('--fastboot',type=Path);p.add_argument('--erase-userdata',action='store_true',required=True)
 run_install(p.parse_args())
if __name__=='__main__':main()
