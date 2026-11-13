"""Read-only environment and input checks before a Connect workflow starts."""
import hashlib,importlib.util,json,os,re,shutil,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
class Check:
 def __init__(self,label,ok,detail,blocking=True):self.label,self.ok,self.detail,self.blocking=label,ok,detail,blocking
 def as_dict(self):return vars(self)
 def text(self):return ('[정상] ' if self.ok else '[필요] ' if self.blocking else '[안내] ')+self.label+' — '+self.detail

def inspect(data,action,install_os=False):
 checks=[]
 def add(label,ok,detail,blocking=True):checks.append(Check(label,bool(ok),detail,blocking))
 try:
  from connect import fastboot_path
  fb=fastboot_path(None)
  if action!='verify':add('Fastboot',True,fb)
 except (OSError,ValueError) as exc:
  fb=None
  if action!='verify':add('Fastboot',False,'Android Platform-Tools를 설치하고 PATH 또는 .android_sdk/platform-tools에 두세요.')
 path=data.get('backup','').strip()
 if action!='fastboot':
  if not path:add('백업 폴더',False,'백업 폴더를 선택하세요.')
  else:
   folder=Path(path)
   if action=='all':
    add('새 백업 폴더',not folder.exists(),'아직 없는 폴더 이름을 입력하세요. 기존 백업은 덮어쓰지 않습니다.' if folder.exists() else str(folder))
    parent=folder.parent
    while not parent.exists() and parent!=parent.parent:parent=parent.parent
    try:
     free=shutil.disk_usage(parent).free
     add('백업 저장 공간',free>=35*1024**3,f'여유 {free/1024**3:.1f}GB. 35GB 이상이 필요합니다.')
     add('백업 쓰기 권한',os.access(parent,os.W_OK),'NAS라면 탐색기에서 공유 폴더에 먼저 로그인하세요.')
    except OSError:add('백업 저장소',False,'드라이브/공유 경로를 열 수 없습니다. NAS 로그인과 연결을 확인하세요.')
   else:
    try:
     status=json.loads((folder/'session-status.json').read_text(encoding='utf-8-sig'))
     add('백업 완료 기록',status.get('complete') is True,'session-status.json의 완료 상태를 확인합니다.')
     files=status.get('files',[])
     ok=len(files)==3 and all((folder/f['path']).is_file() and (folder/f['path']).stat().st_size==f['bytes'] for f in files)
     add('USER·BOOT 백업 파일',ok,'파일 존재·크기 검사입니다. 실제 실행 전 SHA-256도 대조합니다.')
     if action=='unlock':add('백업 기기 식별 정보',bool(status.get('cid')) and bool(status.get('artifacts')),'CID·GPT·Preloader 기록이 필요합니다. 없으면 이 버전의 언락은 실행하지 않습니다.')
    except (OSError,ValueError,KeyError,TypeError):add('순정 백업',False,'완료된 백업 폴더와 session-status.json을 선택하세요.')
 if action in ('all','unlock','fastboot','os'):
  add('대상 시리얼',bool(re.fullmatch(r'[A-Za-z0-9_.:-]{1,128}',data.get('serial',''))),'기기 라벨 또는 실제 Fastboot에서 확인한 시리얼을 입력하세요.')
 if action in ('all','unlock','fastboot'):
  add('PyUSB',importlib.util.find_spec('usb') is not None,'기존 mtk-venv로 실행하거나 PyUSB를 설치하세요.')
 if action in ('all','unlock'):
  repo=Path(os.environ.get('CONNECT_MTK_REPO',str(BASE/'vendor/mtkclient')))
  add('mtkclient', (repo/'mtkclient/Library/mtk_class.py').is_file(),'검증된 mtkclient를 준비하거나 CONNECT_MTK_REPO 경로를 지정하세요.')
  for name,expected in [('Loader/MTK_DA_V5.bin','aef234190ccb8145d2e3b8459741e9adb70f2caa8481aa216c1b25152afaca1f'),('payloads/mt6768_payload.bin','1374139e112b7961abf6571582c8330d879d956ff33ed39bd51c882ddec8a6c5'),('payloads/da_x.bin','b83ebbbff36e330713080e719856241065e51f732658f4b931399df0e17e00fd')]:
   p=repo/'mtkclient'/name
   try:ok=hashlib.sha256(p.read_bytes()).hexdigest()==expected
   except OSError:ok=False
   add(name,ok,'검증한 버전과 해시가 일치해야 합니다.')
 if action=='os' and fb:
  try:
   from connect import list_fastboot
   add('현재 Fastboot 연결',list_fastboot(fb)==[data.get('serial')],'선택한 기기 한 대를 Fastboot로 연결하세요. Android 앱 설치는 연결 · 앱 설치 탭을 사용하세요.')
  except (OSError,RuntimeError,subprocess.TimeoutExpired):add('현재 Fastboot 연결',False,'Fastboot 조회에 실패했습니다. USB와 해당 모드 드라이버를 확인하세요.')
 if action=='os' or install_os:
  image=Path(data.get('image',''));vbmeta=Path(data.get('vbmeta',''))
  add('GSI 이미지',image.is_file() and image.stat().st_size==2623557632,'검증된 LineageOS-22.2-20260105-VANILLA-EXT4-GSI.img를 선택하세요. 실행 전 SHA-256을 확인합니다.')
  add('순정 vbmeta_a',vbmeta.is_file() and vbmeta.stat().st_size==8388608,'같은 기기에서 백업한 8MiB vbmeta_a를 선택하세요.')
 if action in ('all','unlock','fastboot','os') and sys.platform=='win32':
  script="Get-PnpDevice | Where-Object InstanceId -Match 'VID_0E8D&PID_(2000|0003|201C)|VID_18D1&PID_4EE0' | ForEach-Object { $s=Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName DEVPKEY_Device_Service -ErrorAction SilentlyContinue; [pscustomobject]@{id=$_.InstanceId;service=$s.Data} } | ConvertTo-Json -Compress"
  try:
   r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',script],capture_output=True,text=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
   rows=json.loads(r.stdout) if r.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
   needed=['0E8D&PID_2000','0E8D&PID_201C'] if action=='fastboot' else ['0E8D&PID_201C','18D1&PID_4EE0'] if action=='os' else ['0E8D&PID_2000','0E8D&PID_0003','0E8D&PID_201C']
   if install_os and '18D1&PID_4EE0' not in needed:needed.append('18D1&PID_4EE0')
   for token in needed:
    ok=any(token in x.get('id','').upper() and x.get('service','').lower()=='winusb' for x in rows)
    add('USB '+token.replace('&PID_',':'),ok,'WinUSB 등록을 확인했습니다.' if ok else '해당 모드의 WinUSB 드라이버를 먼저 설치하세요. 연결 이력이 없으면 확인되지 않을 수 있습니다.')
  except (OSError,ValueError,subprocess.TimeoutExpired):add('USB 드라이버 조회',False,'Windows 장치 조회에 실패했습니다. 관리자 권한으로 다시 실행하세요.')
 return checks
