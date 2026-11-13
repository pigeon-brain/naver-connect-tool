"""Installer-style UI preview. No device backend is imported or executed."""
import tkinter as tk
from tkinter import ttk,filedialog
import subprocess
from locales.preview import TRANSLATIONS

LANGUAGES=('한국어','English','日本語')
SCENARIOS=('정상 진행','드라이버 누락','연결 끊김','백업 검증 실패')
_process_language='한국어'
def blocked(*args,**kwargs):
 message='미리보기: 기기 명령 실행 차단'
 raise RuntimeError(TRANSLATIONS.get(message,{}).get(_process_language,message))
class DisabledPopen(subprocess.Popen):
 def __init__(self,*args,**kwargs):blocked(*args,**kwargs)
subprocess.Popen=DisabledPopen
for name in ('run','call','check_call','check_output'):setattr(subprocess,name,blocked)

BG='#f5f6f8';WHITE='#ffffff';INK='#17202b';MUTED='#697586';LINE='#e3e7ed';GREEN='#00875a';PALE='#e9f6ef';NAVY='#172b3a'
class InstallerPreview:
 def __init__(self,root):
  self.root=root;root.geometry('1040x760');root.minsize(960,720);root.configure(bg=BG)
  style=ttk.Style(root);style.theme_use('clam')
  style.configure('.',font=('맑은 고딕',10),background=WHITE,foreground=INK)
  style.configure('TEntry',padding=9,fieldbackground=WHITE,bordercolor=LINE,lightcolor=LINE,darkcolor=LINE)
  style.configure('TCombobox',padding=7,fieldbackground=WHITE,bordercolor=LINE)
  style.configure('Horizontal.TProgressbar',background=GREEN,troughcolor='#e7ece9',borderwidth=0,thickness=9)
  root.option_add('*Font',('맑은 고딕',10))
  self.page=0;self.running=False;self.connected=False;self.checked=False;self.failed=False;self.delay=550;self.logs=[]
  self.task=tk.StringVar(value='apps');self.connection=tk.StringVar(value='wifi');self.scenario=tk.StringVar(value=SCENARIOS[0]);self.code=tk.StringVar();self.folder=tk.StringVar(value='');self.image=tk.StringVar();self.consent=tk.BooleanVar()
  self.language=tk.StringVar(value=LANGUAGES[0]);self.locale=LANGUAGES[0]
  self.scenario_display=tk.StringVar();self.notice_state=None;self.completed_steps=0;self.finished=False;self.log_window=None
  self.build()
 def tr(self,text):return TRANSLATIONS.get(text,{}).get(self.locale,text)
 def change_language(self,event=None):
  global _process_language
  if self.running:
   self.language.set(self.locale);return
  if self.language.get()==self.locale:return
  self.locale=self.language.get();_process_language=self.locale
  reopen_log=self.log_window is not None and self.log_window.winfo_exists()
  for child in self.root.winfo_children():child.destroy()
  notice=self.notice_state
  self.build()
  if notice:self.note(*notice)
  if reopen_log:self.show_logs()
 def build(self):
  root=self.root;root.title(self.tr('네이버 커넥트 도구 · 미리보기'))
  self.header=tk.Frame(root,bg=WHITE,height=75);self.header.pack(fill='x');self.header.pack_propagate(False)
  self.label(self.header,'CONNECT',18,bold=True).pack(side='left',padx=(28,12))
  self.label(self.header,'기기 설정 도구',11,color=MUTED).pack(side='left')
  self.language_picker=ttk.Combobox(self.header,textvariable=self.language,values=LANGUAGES,state='readonly',width=9)
  self.language_picker.pack(side='right',padx=(0,24))
  self.language_picker.bind('<<ComboboxSelected>>',self.change_language)
  self.label(self.header,'언어',9,color=MUTED).pack(side='right',padx=(0,8))
  self.label(self.header,'미리보기 · 기기 변경 없음',9,color=GREEN,bg=PALE,padx=12,pady=5).pack(side='right',padx=25)
  tk.Frame(root,bg=LINE,height=1).pack(fill='x')
  footer=tk.Frame(root,bg=WHITE,height=76);footer.pack(side='bottom',fill='x');footer.pack_propagate(False)
  self.footer_note=self.label(footer,'예시 데이터로 화면과 진행 과정을 확인합니다.',9,color=MUTED);self.footer_note.pack(side='left',padx=25)
  self.next_btn=self.button(footer,'다음',self.next,primary=True);self.next_btn.pack(side='right',padx=(8,26),pady=18)
  self.prev_btn=self.button(footer,'이전',self.prev);self.prev_btn.pack(side='right',pady=18)
  tk.Frame(root,bg=LINE,height=1).pack(side='bottom',fill='x')
  middle=tk.Frame(root,bg=BG);middle.pack(fill='both',expand=True)
  self.sidebar=tk.Frame(middle,bg=BG,width=216);self.sidebar.pack(side='left',fill='y');self.sidebar.pack_propagate(False)
  self.nav=[]
  self.label(self.sidebar,'설정 순서',9,color=MUTED,bg=BG).pack(anchor='w',padx=26,pady=(28,14))
  for i,title in enumerate(['작업 선택','기기 연결','준비 확인','작업 진행','완료']):
   b=tk.Button(self.sidebar,text=f'{i+1:02d}    {self.tr(title)}',anchor='w',bg=BG,fg=MUTED,relief='flat',bd=0,padx=18,pady=13,cursor='hand2',command=lambda n=i:self.go(n))
   b.pack(fill='x',padx=12,pady=3);self.nav.append(b)
  bottom=tk.Frame(self.sidebar,bg=BG);bottom.pack(side='bottom',fill='x',padx=22,pady=22)
  self.label(bottom,'예시 상황',9,color=MUTED,bg=BG).pack(anchor='w',pady=(0,6))
  self.scenario_display.set(self.tr(self.scenario.get()))
  self.scenario_picker=ttk.Combobox(bottom,textvariable=self.scenario_display,values=[self.tr(s) for s in SCENARIOS],state='readonly',width=16)
  self.scenario_picker.pack(fill='x');self.scenario_picker.bind('<<ComboboxSelected>>',self.change_scenario)
  self.button(bottom,'처음부터',self.reset).pack(fill='x',pady=(10,0))
  self.content=tk.Frame(middle,bg=WHITE);self.content.pack(side='right',fill='both',expand=True,padx=(0,20),pady=20)
  self.show()
 def change_scenario(self,event=None):
  index=self.scenario_picker.current()
  if index>=0 and not self.running:
   self.scenario.set(SCENARIOS[index]);self.show()
 def label(self,parent,text,size=10,color=INK,bg=WHITE,bold=False,**kw):return tk.Label(parent,text=self.tr(text),bg=bg,fg=color,font=('맑은 고딕',size,'bold' if bold else 'normal'),**kw)
 def button(self,parent,text,command,primary=False):return tk.Button(parent,text=self.tr(text),command=command,bg=GREEN if primary else WHITE,fg=WHITE if primary else INK,activebackground='#006b47' if primary else '#edf1f5',activeforeground=WHITE if primary else INK,relief='flat',bd=0,highlightthickness=0,padx=22,pady=9,cursor='hand2',font=('맑은 고딕',10,'bold' if primary else 'normal'))
 def title(self,title,description):
  self.label(self.body,title,23,bold=True).pack(anchor='w',pady=(0,8))
  self.label(self.body,description,10,color=MUTED,wraplength=680,justify='left').pack(anchor='w',pady=(0,25))
 def card(self):
  frame=tk.Frame(self.body,bg=WHITE,highlightbackground=LINE,highlightthickness=1);frame.pack(fill='x',pady=6);return frame
 def note(self,text,error=False):
  self.notice_state=(text,error)
  if hasattr(self,'notice') and self.notice.winfo_exists():self.notice.destroy()
  self.notice=self.label(self.body,text,10,color='#b54730' if error else GREEN,bg='#fff1ed' if error else PALE,wraplength=640,justify='left',padx=14,pady=12)
  self.notice.pack(fill='x',pady=(16,0))
 def go(self,page):
  if self.running:return
  self.page=page;self.show()
 def show(self):
  self.notice_state=None
  for w in self.content.winfo_children():w.destroy()
  self.body=tk.Frame(self.content,bg=WHITE);self.body.pack(fill='both',expand=True,padx=30,pady=28)
  for i,b in enumerate(self.nav):b.configure(bg=PALE if i==self.page else BG,fg=GREEN if i==self.page else MUTED,font=('맑은 고딕',10,'bold' if i==self.page else 'normal'))
  self.prev_btn.configure(state='disabled' if self.page==0 or self.running else 'normal')
  self.next_btn.configure(state='disabled' if self.running else 'normal',text=self.tr(['다음','다음','시작','다음','닫기'][self.page]))
  for picker in (self.language_picker,self.scenario_picker):picker.configure(state='disabled' if self.running else 'readonly')
  [self.task_page,self.connect_page,self.ready_page,self.progress_page,self.done_page][self.page]()
 def task_page(self):
  self.title('어떤 작업을 할까요?','기기의 현재 상태에 맞는 작업을 선택하세요.')
  options=[('apps','앱 설치 및 기본 설정','Android가 켜진 기기에 콘솔·진단 앱을 설치하고 소리를 끕니다.'),('backup','순정 백업 및 잠금 해제','원본을 보관한 뒤 잠금을 해제합니다. 연결 단계에서 필요한 조작을 안내합니다.'),('os','OS 설치까지 진행','순정 백업과 잠금 해제 후 LineageOS를 설치합니다. 사용자 데이터가 삭제됩니다.'),('verify','기존 백업 확인','보관한 백업의 누락 파일과 무결성을 확인합니다.')]
  for value,title,detail in options:
   card=self.card()
   tk.Radiobutton(card,variable=self.task,value=value,text=self.tr(title),bg=WHITE,fg=INK,selectcolor=PALE,activebackground=WHITE,font=('맑은 고딕',11,'bold'),anchor='w',command=self.task_changed).pack(fill='x',padx=14,pady=(11,3))
   self.label(card,detail,9,color=MUTED,wraplength=620,justify='left').pack(anchor='w',padx=40,pady=(0,12))
 def task_changed(self):self.checked=False
 def connect_page(self):
  self.title('커넥트를 연결하세요','연결 방법을 고른 뒤 기기를 검색합니다. 지금은 예시 기기를 표시합니다.')
  row=tk.Frame(self.body,bg=WHITE);row.pack(fill='x',pady=(0,14))
  for text,value in [('무선 디버깅','wifi'),('USB 연결','usb')]:tk.Radiobutton(row,text=self.tr(text),variable=self.connection,value=value,bg=WHITE,activebackground=WHITE,command=self.show).pack(side='left',padx=(0,24))
  card=self.card()
  instructions='1. PC와 같은 네트워크에 연결\n2. 개발자 옵션에서 무선 디버깅 켜기\n3. ‘페어링 코드로 기기 페어링’ 열기' if self.connection.get()=='wifi' else '1. PC와 커넥트를 USB 케이블로 연결\n2. Android에서는 USB 디버깅 켜기\n3. 기기에 뜨는 PC 연결 요청 허용'
  self.label(card,instructions,10,justify='left',anchor='w').pack(fill='x',padx=20,pady=18)
  row=tk.Frame(self.body,bg=WHITE);row.pack(fill='x',pady=(18,8))
  self.button(row,'기기 검색',self.search,True).pack(side='left')
  if self.connection.get()=='wifi':
   self.label(row,'페어링 코드',9,color=MUTED).pack(side='left',padx=(22,8));ttk.Entry(row,textvariable=self.code,width=10).pack(side='left');self.button(row,'연결',self.pair).pack(side='left',padx=8)
  self.device_card=self.card()
  self.label(self.device_card,'Npay Connect' if self.connected else '검색된 기기 없음',12,bold=True).pack(anchor='w',padx=20,pady=(16,4))
  self.label(self.device_card,'DEMO-CONNECT  ·  Android 15  ·  연결됨 (예시)' if self.connected else '기기 검색을 눌러 연결 상태를 확인하세요.',9,color=GREEN if self.connected else MUTED).pack(anchor='w',padx=20,pady=(0,16))
  if self.connected:self.note('기기가 연결되었습니다. 다음 단계에서 필요한 항목을 확인합니다.')
 def search(self):
  self.connected=True;self.code.set('123456');self.show()
 def pair(self):
  if len(self.code.get())!=6 or not self.code.get().isdigit():self.note('6자리 코드를 입력하세요. 미리보기 예시 코드는 123456입니다.',True);return
  self.connected=True;self.show()
 def path_row(self,label,variable,folder=False):
  self.label(self.body,label,9,color=MUTED).pack(anchor='w',pady=(10,4))
  row=tk.Frame(self.body,bg=WHITE);row.pack(fill='x')
  ttk.Entry(row,textvariable=variable).pack(side='left',fill='x',expand=True)
  def choose():
   options={'title':self.tr(label),'parent':self.root}
   value=filedialog.askdirectory(**options) if folder else filedialog.askopenfilename(**options,filetypes=[(self.tr('이미지 파일'),'*.img'),(self.tr('모든 파일'),'*')])
   if value:variable.set(value);self.checked=False
  self.button(row,'찾아보기',choose).pack(side='left',padx=(8,0))
 def ready_page(self):
  self.title('시작 전 준비 확인','누락된 항목이 있으면 해결 방법을 안내합니다.')
  if self.task.get() in ('backup','os','verify'):
   self.path_row('백업 폴더',self.folder,True)
   if self.task.get()=='os':self.path_row('LineageOS 이미지',self.image)
   self.button(self.body,'예시 경로 사용',self.sample_paths).pack(anchor='e',pady=5)
  else:self.label(self.body,'설치 대상   콘솔 0.4.3 · 진단 앱 0.1.1',10,bold=True).pack(anchor='w',pady=(0,12))
  self.check_area=tk.Frame(self.body,bg=WHITE);self.check_area.pack(fill='x',pady=8)
  rows=[('기기 연결',self.connected,'기기 연결 단계에서 검색하세요.'),('USB / ADB 드라이버',self.scenario.get()!='드라이버 누락','해당 USB 모드의 WinUSB 드라이버를 설치하세요.'),('파일 및 저장 공간',self.task.get()=='apps' or bool(self.folder.get()),'백업 폴더를 선택하세요.')]
  if self.task.get()=='os':rows.append(('OS 이미지',bool(self.image.get()),'설치할 이미지 파일을 선택하세요.'))
  self.checked=all(ok for _,ok,_ in rows)
  for label,ok,helptext in rows:
   row=tk.Frame(self.check_area,bg=WHITE);row.pack(fill='x',pady=7)
   self.label(row,'✓' if ok else '!',11,color=GREEN if ok else '#b54730',bold=True).pack(side='left',padx=(0,12))
   self.label(row,label,10).pack(side='left');self.label(row,'준비됨 (예시)' if ok else '확인 필요',9,color=GREEN if ok else '#b54730').pack(side='right')
   if not ok:self.label(self.check_area,helptext,9,color=MUTED,wraplength=610,justify='left').pack(anchor='w',padx=25)
  if self.task.get()=='os':tk.Checkbutton(self.body,text=self.tr('사용자 데이터가 삭제되는 작업임을 확인했습니다.'),variable=self.consent,bg=WHITE,activebackground=WHITE).pack(anchor='w',pady=10)
  self.note('준비가 끝났습니다. 시작을 누르면 진행 화면을 확인할 수 있습니다.' if self.checked else '확인 필요한 항목을 해결한 뒤 다시 진행하세요.',not self.checked)
 def sample_paths(self):self.folder.set(self.tr('예시 / 커넥트 백업'));self.image.set(self.tr('예시 / LineageOS.img'));self.show()
 def progress_page(self):
  self.title('작업 진행','예시 단계의 진행 상태를 표시합니다.')
  self.progress_title=self.label(self.body,'시작 대기',14,bold=True);self.progress_title.pack(anchor='w',pady=(14,12))
  self.percent=tk.DoubleVar(value=0);ttk.Progressbar(self.body,variable=self.percent,maximum=100).pack(fill='x',pady=(0,20))
  self.step_area=tk.Frame(self.body,bg=WHITE);self.step_area.pack(fill='both',expand=True)
  self.step_labels=[]
  steps={'apps':['기기 및 설치 파일 확인','소리 끄기','진단 앱 설치','콘솔 설치','실행 확인'],'backup':['기기 확인','순정 데이터 백업','백업 검증','잠금 해제','Fastboot 확인'],'os':['기기 확인','순정 백업 및 검증','잠금 해제','OS 설치','첫 부팅 확인'],'verify':['백업 파일 확인','파일 크기 확인','해시 검증']}[self.task.get()]
  self.steps=steps
  for index,text in enumerate(steps):
   done=index<self.completed_steps
   l=self.label(self.step_area,('✓   ' if done else '○   ')+self.tr(text),10,color=GREEN if done else MUTED);l.pack(anchor='w',pady=9);self.step_labels.append(l)
  self.percent.set(min(self.completed_steps,len(steps))/len(steps)*100)
  if self.failed:
   self.progress_title.configure(text=self.tr('작업 중단'),fg='#b54730');self.next_btn.configure(text=self.tr('준비 확인'))
  elif self.finished:
   self.progress_title.configure(text=self.tr('모든 단계 확인 완료'));self.next_btn.configure(text=self.tr('결과 보기'))
  self.button(self.body,'상세 기록 보기',self.show_logs).pack(anchor='w',pady=(15,0))
  if not self.running:self.button(self.body,'진행 예시 시작',self.begin,True).pack(anchor='e')
 def begin(self):
  if self.running:return
  self.running=True;self.failed=False;self.finished=False;self.completed_steps=0;self.logs=[];self.page=3;self.show();self.tick(0)
 def enable_navigation(self,next_text):
  self.next_btn.configure(state='normal',text=self.tr(next_text));self.prev_btn.configure(state='normal')
  for picker in (self.language_picker,self.scenario_picker):picker.configure(state='readonly')
 def tick(self,index):
  if not self.root.winfo_exists():return
  if index==1 and self.scenario.get() in ('연결 끊김','백업 검증 실패'):
   self.failed=True;self.running=False
   reason='기기 연결이 끊겼습니다. 연결을 확인한 뒤 다시 검사하세요.' if self.scenario.get()=='연결 끊김' else '백업 해시가 일치하지 않습니다. 원본을 보존하고 백업을 다시 확인하세요.'
   self.logs.append((reason,False));self.progress_title.configure(text=self.tr('작업 중단'),fg='#b54730');self.note(reason,True);self.enable_navigation('준비 확인');return
  if index>=len(self.step_labels):
   self.running=False;self.finished=True;self.progress_title.configure(text=self.tr('모든 단계 확인 완료'));self.enable_navigation('결과 보기');return
  item=self.step_labels[index];key=self.steps[index];text=self.tr(key);self.completed_steps=index+1
  item.configure(text='✓   '+text,fg=GREEN);self.progress_title.configure(text=text);self.percent.set(self.completed_steps/len(self.step_labels)*100);self.logs.append((key,True));self.root.after(self.delay,lambda:self.tick(index+1))
 def done_page(self):
  self.title('설정 과정이 끝났습니다','미리보기 결과입니다. 실제 기기와 파일은 변경하지 않았습니다.')
  self.label(self.body,'✓',42,color=GREEN).pack(anchor='w',pady=(15,10))
  names={'apps':'콘솔·진단 앱 설치 및 음소거','backup':'순정 백업 및 잠금 해제','os':'백업·잠금 해제·OS 설치','verify':'기존 백업 검증'}
  self.label(self.body,names[self.task.get()],15,bold=True).pack(anchor='w',pady=(0,12))
  self.label(self.body,'실제 설치에서는 기기 응답과 검증 결과를 확인한 단계만 완료로 표시합니다.',10,color=MUTED,wraplength=630,justify='left').pack(anchor='w')
  self.button(self.body,'상세 기록 보기',self.show_logs).pack(anchor='w',pady=22)
  self.button(self.body,'다른 작업 선택',self.reset).pack(anchor='w')
 def show_logs(self):
  if self.log_window is not None and self.log_window.winfo_exists():self.log_window.destroy()
  top=self.log_window=tk.Toplevel(self.root);top.title(self.tr('작업 기록 · 미리보기'));top.geometry('650x360');top.configure(bg=WHITE)
  lines=[self.tr('[예시] {step} 완료').format(step=self.tr(key)) if done else self.tr(key) for key,done in self.logs]
  text=tk.Text(top,bd=0,bg=BG,fg=INK,font=('맑은 고딕',10),padx=18,pady=18,wrap='word');text.pack(fill='both',expand=True,padx=15,pady=15);text.insert('end','\n'.join(lines) or self.tr('아직 진행한 단계가 없습니다.'));text.configure(state='disabled')
 def next(self):
  if self.running:return
  if self.page==4:self.root.destroy();return
  if self.page==1 and not self.connected:self.note('기기 검색으로 연결할 기기를 먼저 확인하세요.',True);return
  if self.page==2:
   if not self.checked:self.note('확인 필요한 항목이 남아 있습니다.',True);return
   if self.task.get()=='os' and not self.consent.get():self.note('데이터 삭제 안내를 확인해 주세요.',True);return
   self.begin();return
  if self.page==3 and self.failed:self.go(2);return
  self.go(self.page+1)
 def prev(self):
  if not self.running:self.go(max(0,self.page-1))
 def reset(self):
  if self.running:return
  self.connected=False;self.checked=False;self.failed=False;self.finished=False;self.completed_steps=0;self.logs=[];self.code.set('');self.consent.set(False);self.page=0;self.show()
if __name__=='__main__':
 root=tk.Tk();InstallerPreview(root);root.mainloop()
