"""Single window for backup, unlock, Fastboot, GSI installation and Android setup."""
import json,queue,subprocess,sys,threading,tkinter as tk
from pathlib import Path
from tkinter import ttk,filedialog,messagebox
from advanced_i18n import Language
from setup_gui import SetupWindow
BASE=Path(__file__).resolve().parent
class Workbench:
 def __init__(self,root):
  self.root=root;self.busy=False;self.messages=queue.Queue();self.buttons=[]
  self.language=Language(root,lambda:self.busy or self.android.active)
  language=self.language
  tabs=ttk.Notebook(root);tabs.pack(fill='both',expand=True)
  panel=ttk.Frame(tabs,padding=16);android=ttk.Frame(tabs)
  tabs.add(panel);tabs.add(android)
  language.bind(lambda:tabs.tab(panel,text=language.text('백업 · 언락 · OS')))
  language.bind(lambda:tabs.tab(android,text=language.text('연결 · 앱 설치')))
  self.tabs=tabs
  self.check_panel=ttk.Frame(tabs,padding=12);tabs.add(self.check_panel)
  language.bind(lambda:tabs.tab(self.check_panel,text=language.text('준비 상태')))
  self.check_tree=ttk.Treeview(self.check_panel,columns=('state','detail'),show='tree headings')
  for column,label in (('#0','항목'),('state','상태'),('detail','필요한 조치')):
   language.bind(lambda c=column,l=label:self.check_tree.heading(c,text=language.text(l)))
  self.check_tree.column('#0',width=205);self.check_tree.column('state',width=70);self.check_tree.column('detail',width=560)
  self.check_tree.pack(fill='both',expand=True)
  self.checks=[]
  self.check_detail=tk.StringVar()
  language.bind(self.translate_checks)
  ttk.Label(self.check_panel,textvariable=self.check_detail,wraplength=850).pack(fill='x',pady=8)
  self.check_tree.bind('<<TreeviewSelect>>',lambda event:self.update_check_detail())
  language.widget(ttk.Label(self.check_panel,wraplength=850),'검사 결과는 로그 폴더의 preflight-latest.json에 저장됩니다. 실패한 항목을 수정한 뒤 다시 검사하세요.').pack(anchor='w',pady=8)
  self.android=SetupWindow(root,android,language);root.geometry('920x740')
  language.bind(lambda:root.title(language.text('네이버 커넥트 도구')))
  panel.columnconfigure(1,weight=1);panel.rowconfigure(11,weight=1)
  self.vars={}
  for row,(key,label) in enumerate([('backup','백업 폴더'),('serial','기기 시리얼'),('image','LineageOS 이미지'),('vbmeta','순정 vbmeta_a')]):
   v=self.vars[key]=tk.StringVar();language.widget(ttk.Label(panel),label).grid(row=row,column=0,sticky='w',pady=5)
   ttk.Entry(panel,textvariable=v).grid(row=row,column=1,sticky='ew')
   if key!='serial':language.widget(ttk.Button(panel,command=lambda k=key:self.choose(k)),'선택').grid(row=row,column=2,padx=6)
  self.install_os=tk.BooleanVar(value=False)
  language.widget(ttk.Checkbutton(panel,variable=self.install_os),'언락 후 OS 설치 포함 — 사용자 데이터 삭제').grid(row=4,column=0,columnspan=2,sticky='w',pady=8)
  b=language.widget(ttk.Button(panel,command=lambda:self.check('all')),'설정 검사');b.grid(row=4,column=2);self.buttons.append(b)
  for row,label,action in [(5,'백업부터 순서대로 실행','all'),(6,'기존 백업 검증','verify'),(7,'기존 백업으로 언락부터 진행','unlock'),(8,'Fastboot 진입','fastboot'),(9,'현재 Fastboot에서 OS 설치','os')]:
   b=language.widget(ttk.Button(panel,command=lambda a=action:self.start(a)),label);b.grid(row=row,column=0,columnspan=3,sticky='ew',pady=3);self.buttons.append(b)
  self.status=tk.StringVar()
  self.status_message=('대기 중',{})
  language.bind(self.translate_status)
  ttk.Label(panel,textvariable=self.status,wraplength=840).grid(row=10,column=0,columnspan=3,sticky='w',pady=8)
  self.output=tk.Text(panel,height=15,state='disabled',wrap='word');self.output.grid(row=11,column=0,columnspan=3,sticky='nsew')
  language.widget(ttk.Label(panel,wraplength=840),'MT6768/6769 커넥트 전용. 통합 백업·언락·OS 경로는 모의 검증 단계이며 실제 복원은 미검증.').grid(row=12,column=0,columnspan=3,sticky='w',pady=6)
  root.protocol('WM_DELETE_WINDOW',self.close);root.after(100,self.drain)
  # External APKs and their manifest must be selected explicitly.
 def set_status(self,source,**values):
  self.status_message=(source,values)
  self.translate_status()
 def translate_status(self):
  source,values=self.status_message
  if source=='[{state}] {label} — {detail}':
   values=dict(state=self.language.text(values['state']),label=self.language.text(values['label']),
               detail=self.language.check_detail(values['detail']))
  message=self.language.text(source,**values)
  self.status.set(message if values else message[-220:])
 def update_check_detail(self):
  selection=self.check_tree.selection()
  if selection:self.check_detail.set(self.check_tree.item(selection[0],'values')[1])
  else:self.check_detail.set(self.language.text('항목을 선택하면 필요한 조치가 표시됩니다.'))
 def translate_checks(self):
  for item,c in zip(self.check_tree.get_children(),self.checks):
   self.check_tree.item(item,text=self.language.text(c['label']),values=(
    self.language.text('정상' if c['ok'] else '필요'),self.language.check_detail(c['detail'])))
  self.update_check_detail()
 def choose(self,key):
  value=filedialog.askdirectory(parent=self.root,title=self.language.text('백업 폴더'),mustexist=False) if key=='backup' else filedialog.askopenfilename(parent=self.root,title=self.language.text('파일 선택'))
  if value:self.vars[key].set(value)
 def close(self):
  if self.busy or self.android.active:messagebox.showwarning(self.language.text('작업 진행 중'),self.language.text('현재 작업이 끝난 뒤 창을 닫아주세요.'),parent=self.root);return
  self.root.destroy()
 def show_checks(self,checks):
  self.messages.put(('checks',[c.as_dict() for c in checks]))
  for c in checks:self.messages.put(('check_message',c.as_dict()))
  logs=BASE/'logs';logs.mkdir(exist_ok=True)
  (logs/'preflight-latest.json').write_text(json.dumps([c.as_dict() for c in checks],ensure_ascii=False,indent=2),encoding='utf-8')
 def check(self,action):
  if self.busy or self.android.active:return
  data={k:v.get().strip() for k,v in self.vars.items()};install=self.install_os.get()
  self.busy=True
  self.language.sync()
  self.set_status('작업 진행 중')
  for b in self.buttons+self.android.buttons:b.state(['disabled'])
  def worker():
   try:
    from preflight import inspect
    self.show_checks(inspect(data,action,install))
   except Exception as exc:self.messages.put(('message','검사 실패: {detail}',{'detail':str(exc)}))
   finally:self.messages.put(None)
  threading.Thread(target=worker,daemon=True).start()
 def start(self,action):
  if self.busy or self.android.active:return
  data={k:v.get().strip() for k,v in self.vars.items()};install=self.install_os.get()
  if action!='fastboot' and not data['backup']:self.check(action);return
  if action in ('all','unlock','fastboot','os') and not data['serial']:self.check(action);return
  if (action=='os' or install) and not all(data[k] for k in ('image','vbmeta')):self.check(action);return
  if action=='all' and Path(data['backup']).exists():messagebox.showerror(self.language.text('백업 폴더'),self.language.text('덮어쓰지 않도록 새 폴더를 지정하세요.'),parent=self.root);return
  if action in ('all','unlock','os'):
   msg=self.language.text('본인 소유의 네이버 커넥트 한 대만 연결했는지 확인하세요. 백업 검증 실패 시 쓰기는 중지됩니다.')
   if action=='os' or install:msg+='\n'+self.language.text('OS 설치는 사용자 데이터를 삭제합니다. 선택한 백업이 이 기기의 순정 백업이어야 합니다.')
   if not messagebox.askokcancel(self.language.text('작업 확인'),msg,parent=self.root):return
  self.busy=True
  self.language.sync()
  self.set_status('작업 진행 중')
  for b in self.buttons+self.android.buttons:b.state(['disabled'])
  def worker():
   try:
    from preflight import inspect
    checks=inspect(data,action,install);self.show_checks(checks)
    if any(not c.ok and c.blocking for c in checks):raise RuntimeError('준비 상태 탭의 필요한 항목을 해결한 뒤 다시 실행하세요. 기기 작업은 시작하지 않았습니다.')
    jobs=[]
    if action=='verify':jobs.append(('connect.py',['verify',data['backup']]))
    if action=='all':jobs.append(('mtk_backup.py',['--run','--backup-dir',data['backup']]))
    if action in ('all','unlock'):jobs.append(('mtk_unlock.py',['--execute','--wait-for-cycle','--backup-dir',data['backup']]))
    if action in ('all','unlock','fastboot'):jobs.append(('connect.py',['enter-fastboot','--serial',data['serial'],'--timeout','43200']))
    if action=='os' or (install and action in ('all','unlock')):jobs.append(('os_install.py',['--serial',data['serial'],'--backup-dir',data['backup'],'--image',data['image'],'--vbmeta',data['vbmeta'],'--erase-userdata']))
    logs=BASE/'logs';logs.mkdir(exist_ok=True)
    import datetime
    with (logs/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-workflow.log')).open('x',encoding='utf-8') as log:
     completed=[]
     for filename,args in jobs:
      checkpoint={'stage':filename,'status':'running','completed':completed}
      (logs/'workflow-state.json').write_text(json.dumps(checkpoint,indent=2),encoding='utf-8')
      self.messages.put(('message','실행: {filename}',{'filename':filename}))
      process=subprocess.Popen([sys.executable,'-X','utf8','-u',str(BASE/filename),*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',cwd=BASE,creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
      for line in process.stdout:
       log.write(line);log.flush();self.messages.put(line.rstrip())
      code=process.wait()
      if code!=0:
       checkpoint.update(status='failed',exit_code=code)
       (logs/'workflow-state.json').write_text(json.dumps(checkpoint,indent=2),encoding='utf-8')
       self.messages.put(('message','{filename} 실패. 후속 단계는 실행하지 않았습니다. 로그와 현재 기기 상태를 확인하세요. 부분 백업을 삭제하거나 무조건 다시 쓰지 마세요.',{'filename':filename}))
       return
      completed.append(filename)
      checkpoint.update(status='completed',completed=completed)
      (logs/'workflow-state.json').write_text(json.dumps(checkpoint,indent=2),encoding='utf-8')
    self.messages.put('요청한 단계 완료. OS를 설치했다면 초기 설정 완료 후 연결 · 앱 설치 탭을 사용하세요.')
   except Exception as exc:self.messages.put(str(exc))
   finally:self.messages.put(None)
  threading.Thread(target=worker,daemon=True).start()
 def drain(self):
  while not self.messages.empty():
   line=self.messages.get()
   if isinstance(line,tuple) and line[0]=='checks':
    self.check_tree.delete(*self.check_tree.get_children())
    self.checks=line[1]
    for c in self.checks:self.check_tree.insert('', 'end')
    self.translate_checks()
    if any(not c['ok'] for c in line[1]):self.tabs.select(self.check_panel)
    continue
   if line is None:
    self.busy=False
    self.language.sync()
    for b in self.buttons+self.android.buttons:b.state(['!disabled'])
    continue
   if isinstance(line,tuple) and line[0]=='message':
    _,source,values=line
    self.set_status(source,**values)
    line=self.language.text(source,**values)
   elif isinstance(line,tuple) and line[0]=='check_message':
    c=line[1]
    state='정상' if c['ok'] else '필요' if c['blocking'] else '안내'
    self.set_status('[{state}] {label} — {detail}',state=state,label=c['label'],detail=c['detail'])
    line=f"[{self.language.text(state)}] {self.language.text(c['label'])} — {self.language.check_detail(c['detail'])}"
   elif 'waiting-for-power-cycle' in line or 'Preloader 연결 대기' in line or 'Waiting for PreLoader' in line:
    self.set_status('연결 도구 대기 중. USB와 전원을 분리한 뒤 USB → 전원 순서로 연결하세요.')
   else:
    self.set_status(line)
    line=self.language.text(line)
   self.output.configure(state='normal');self.output.insert('end',line+'\n');self.output.see('end');self.output.configure(state='disabled')
  self.root.after(100,self.drain)
if __name__=='__main__':
 root=tk.Tk();Workbench(root);root.mainloop()
