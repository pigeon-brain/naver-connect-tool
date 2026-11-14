"""Audit reviewed source files, the Git index, and release archives; no device access."""
from pathlib import Path, PurePosixPath
import argparse, re, subprocess, zipfile, hashlib
ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','__pycache__','.venv','vendor','build'}
FORBIDDEN={'.bin','.img','.apk','.log','.pem','.key','.p12','.pfx','.jks','.7z','.zip','.partial','.otf','.ttf','.woff','.woff2','.dex','.jar','.class','.pyc'}
PATTERNS=[
 re.compile(r'\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b'),
 re.compile(r'[A-Za-z]:[\\/]+Users[\\/]+[^\s\\/]+',re.I),
 re.compile(r'\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b',re.I),
 re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
 re.compile(r'\bCHS\d[A-Z0-9]{8,}\b'),
 re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|sk-[A-Za-z0-9_-]{30,})'),
]
def inspect(name,data):
 p=PurePosixPath(name)
 if p.suffix.lower() in FORBIDDEN or any(x in {'logs','backups','build'} for x in p.parts):return 'Excluded asset: '+name
 if len(data)>2*1024*1024:return 'Unexpected large file: '+name
 # This exact screenshot was visually reviewed for private information.
 if name == 'docs/screenshot.png' and hashlib.sha256(data).hexdigest() == '2465fd6cc4e7e2cedd47a0c9cd70e9d0835927fe6a8ae40bd632ad9b1a1fecbb':return None
 try:text=data.decode('utf-8-sig')
 except UnicodeError:return 'Unexpected binary: '+name
 if '\x00' in text:return 'Unexpected binary: '+name
 if any(pattern.search(text) for pattern in PATTERNS):return 'Potential private data: '+name

def audit(archive=None,staged=False):
 names=(ROOT/'PUBLIC_FILES.txt').read_text(encoding='utf-8').splitlines()
 if len(names)!=len(set(names)):raise ValueError('Duplicate allowlist entry')
 for name in names:
  p=PurePosixPath(name)
  if not name or p.is_absolute() or '..' in p.parts or ':' in name or '\\' in name:raise ValueError('Invalid allowlist path')
 expected=set(names); records={}; errors=[]
 if archive:
  with zipfile.ZipFile(archive) as bundle:
   for item in bundle.infolist():
    if item.is_dir():continue
    prefix=ROOT.name+'/'
    if not item.filename.startswith(prefix):errors.append('Unexpected archive root');continue
    name=item.filename[len(prefix):]
    if name in records:errors.append('Duplicate archive entry: '+name)
    records[name]=bundle.read(item)
 elif staged:
  names=subprocess.check_output(['git','-C',str(ROOT),'ls-files','-z']).decode().split('\0')
  for name in filter(None,names):records[name]=subprocess.check_output(['git','-C',str(ROOT),'show',':'+name])
 else:
  for p in ROOT.rglob('*'):
   rel=p.relative_to(ROOT)
   if any(x in SKIP for x in rel.parts):continue
   if p.is_symlink():errors.append('Linked path: '+rel.as_posix())
   elif p.is_file():records[rel.as_posix()]=p.read_bytes()
 for name in sorted(expected-records.keys()):errors.append('Missing public file: '+name)
 for name in sorted(records.keys()-expected):errors.append('Unreviewed file: '+name)
 for name,data in records.items():
  error=inspect(name,data)
  if error:errors.append(error)
  if (archive or staged) and name in expected:
   reviewed=(ROOT/name).read_bytes()
   # Git normalizes text line endings in the index; ZIP bytes must match exactly.
   actual=data.replace(b'\r\n',b'\n') if staged else data
   reviewed=reviewed.replace(b'\r\n',b'\n') if staged else reviewed
   if actual!=reviewed:errors.append('Content differs from reviewed tree: '+name)
 return errors,len(records)
def main():
 p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--archive',type=Path);g.add_argument('--staged',action='store_true');a=p.parse_args()
 try:errors,count=audit(a.archive,a.staged)
 except (OSError,ValueError,subprocess.CalledProcessError,zipfile.BadZipFile) as e:print('Audit failed: '+str(e));return 1
 if errors:print('\n'.join(errors));return 1
 print(f'Public source scan passed: {count} files (not a guarantee of complete secret detection).');return 0
if __name__=='__main__':raise SystemExit(main())