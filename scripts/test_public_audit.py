"""Regression checks for public source packaging, without ADB or USB."""
from pathlib import Path
import tempfile,unittest,zipfile
import check_public_tree as audit
class PublicAuditTest(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.previous=audit.ROOT
  audit.ROOT=Path(self.temp.name)/'sample';audit.ROOT.mkdir()
  (audit.ROOT/'PUBLIC_FILES.txt').write_text('PUBLIC_FILES.txt\nmain.py\n',encoding='utf-8')
  (audit.ROOT/'main.py').write_text('print("ready")\n',encoding='utf-8')
 def tearDown(self):
  audit.ROOT=self.previous;self.temp.cleanup()
 def test_clean_tree(self):self.assertEqual(audit.audit()[0],[])
 def test_unreviewed_file(self):
  (audit.ROOT/'extra.txt').write_text('unexpected')
  self.assertIn('Unreviewed file: extra.txt',audit.audit()[0])
 def test_private_address(self):
  (audit.ROOT/'main.py').write_text('.'.join(map(str,[192,168,1,9])))
  self.assertIn('Potential private data: main.py',audit.audit()[0])
 def test_archive_cannot_substitute_content(self):
  archive=Path(self.temp.name)/'source.zip'
  with zipfile.ZipFile(archive,'w') as z:
   z.write(audit.ROOT/'PUBLIC_FILES.txt','sample/PUBLIC_FILES.txt')
   z.writestr('sample/main.py','different content')
  self.assertIn('Content differs from reviewed tree: main.py',audit.audit(archive)[0])
 def test_binary_key_excluded(self):
  self.assertEqual(audit.inspect('signing.jks',b'data'),'Excluded asset: signing.jks')
if __name__=='__main__':unittest.main()