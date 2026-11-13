import time,tkinter as tk,unittest
from installer_preview import InstallerPreview,LANGUAGES,blocked
from locales.preview import TRANSLATIONS
from workbench import Workbench
class LanguageTests(unittest.TestCase):
 def root(self):
  try:r=tk.Tk();r.withdraw();return r
  except tk.TclError as exc:self.skipTest(str(exc))
 def cleanup(self,r):
  for token in r.tk.call('after','info'):r.after_cancel(token)
  r.destroy()
 def test_preview_languages_and_inputs(self):
  r=self.root()
  try:
   app=InstallerPreview(r);app.folder.set('sample-backup');app.code.set('123456')
   for lang in LANGUAGES:
    app.language.set(lang);app.change_language();r.update_idletasks()
    self.assertEqual(app.folder.get(),'sample-backup');self.assertEqual(app.code.get(),'123456')
    self.assertEqual(app.next_btn.cget('text'),{'한국어':'다음','English':'Next','日本語':'次へ'}[lang])
    for page in range(5):app.go(page);r.update_idletasks()
    app.go(0)
   app.connected=True;app.task.set('apps');app.delay=1;app.begin()
   deadline=time.monotonic()+3
   while app.running and time.monotonic()<deadline:r.update();time.sleep(.005)
   self.assertFalse(app.running);self.assertTrue(app.finished)
  finally:self.cleanup(r)
 def test_advanced_inputs_and_busy_language_lock(self):
  r=self.root()
  try:
   app=Workbench(r);app.vars['backup'].set('sample-backup');app.android.variables['code'].set('123456')
   for index in range(3):
    app.language.selector.current(index);app.language.change();r.update_idletasks()
    self.assertEqual(app.language.index,index);self.assertEqual(app.vars['backup'].get(),'sample-backup');self.assertEqual(app.android.variables['code'].get(),'123456')
   app.busy=True;app.language.selector.current(0);app.language.change();self.assertEqual(app.language.index,2)
  finally:self.cleanup(r)
 def test_catalog_has_both_languages(self):
  for source,entry in TRANSLATIONS.items():
   self.assertTrue(entry['English'],source);self.assertTrue(entry['日本語'],source)
 def test_preview_blocks_external_processes(self):
  with self.assertRaises(RuntimeError):blocked('adb')
if __name__=='__main__':unittest.main()
