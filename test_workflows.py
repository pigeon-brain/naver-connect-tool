import ast,contextlib,io,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import os_install
class GuardTests(unittest.TestCase):
 def test_sector_guard(self):
  source=Path(__file__).with_name('mtk_unlock.py').read_text(encoding='utf-8-sig')
  node=next(n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef) and n.name=='guarded_write')
  code=ast.get_source_segment(source,node)
  wrapper='def factory():\n    write_count=0\n'+''.join('    '+line+'\n' for line in code.splitlines())+'    return guarded_write\n'
  scope={'part':{'offset':4096},'candidate':bytes(512),'state':{},'save':lambda _:None,'write_original':lambda **kw:True}
  exec(wrapper,scope)
  valid=dict(addr=4096,length=512,filename='',parttype='user',wdata=bytes(512))
  guard=scope['factory']();self.assertTrue(guard(**valid))
  with self.assertRaises(RuntimeError):guard(**valid)
  for k,v in [('addr',0),('length',8388608),('parttype','rpmb'),('filename','bad.bin'),('wdata',b'bad')]:
   with self.subTest(k=k),self.assertRaises(RuntimeError):scope['factory']()(**dict(valid,**{k:v}))
 def install_case(self,fail=False,wrong_hash=False):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'user.bin').write_bytes(b'V'*512);(root/'vbmeta.bin').write_bytes(b'V'*512);(root/'system.img').write_bytes(b'S'*512)
   (root/'session-status.json').write_text(json.dumps({'partitions':[{'name':'vbmeta_a','sector':0,'sectors':1}]}))
   args=SimpleNamespace(backup_dir=root,image=root/'system.img',vbmeta=root/'vbmeta.bin',erase_userdata=True,serial='TEST',fastboot=None)
   calls=[];mode=['yes'];size=['0x641ae000']
   def variable(fb,serial,name):return {'unlocked':'yes','current-slot':'a','is-userspace':mode[0],'snapshot-update-status':'none','is-logical:system_a':'yes','partition-size:system_a':size[0],'partition-size:super':'0x240000000'}[name]
   def execute(cmd,**kwargs):
    action=cmd[3:];calls.append(action)
    if action[0]=='resize-logical-partition':size[0]=hex(512)
    if action==['reboot','bootloader']:mode[0]='no'
    failed=fail and 'system_a' in action and 'flash' in action
    return SimpleNamespace(returncode=1 if failed else 0,stdout='',stderr='FAIL' if failed else 'OKAY')
   with patch.object(os_install,'__file__',str(root/'os_install.py')),patch.object(os_install,'IMAGE_SIZE',512),patch.object(os_install,'sha',return_value='bad' if wrong_hash else os_install.IMAGE_HASH),patch.object(os_install,'load_stock_records',return_value={}),patch.object(os_install,'verify_entries'),patch.object(os_install,'fastboot_path',return_value='fastboot'),patch.object(os_install,'list_fastboot',return_value=['TEST']),patch.object(os_install,'getvar',side_effect=variable),patch.object(os_install.subprocess,'run',side_effect=execute),contextlib.redirect_stdout(io.StringIO()):
    if fail or wrong_hash:
     with self.assertRaises((RuntimeError,ValueError)):os_install.run_install(args)
    else:os_install.run_install(args)
   return calls
 def test_install_order(self):
  calls=self.install_case();self.assertEqual([c[0] for c in calls],['resize-logical-partition','-S','format:f2fs','reboot','--disable-verity','reboot'])
 def test_flash_failure_stops_format(self):self.assertFalse(any(c[0]=='format:f2fs' for c in self.install_case(fail=True)))
 def test_bad_hash_no_device_calls(self):self.assertEqual(self.install_case(wrong_hash=True),[])
if __name__=='__main__':unittest.main()
