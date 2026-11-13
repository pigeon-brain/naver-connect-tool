"""Build a source-only archive from the reviewed allowlist."""
from pathlib import Path
import argparse,zipfile
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 from check_public_tree import audit
 errors,_=audit()
 if errors:raise SystemExit('\n'.join(errors))
 names=(ROOT/'PUBLIC_FILES.txt').read_text(encoding='utf-8').splitlines()
 if args.output.exists():raise SystemExit('Output already exists; choose a new archive path.')
 sources=[]
 for name in names:
  relative=Path(name)
  if relative.is_absolute() or '..' in relative.parts:raise SystemExit('Invalid allowlist path')
  source=ROOT/relative
  if not source.is_file() or source.is_symlink():raise SystemExit('Missing or linked source: '+name)
  sources.append((source,name))
 with zipfile.ZipFile(args.output,'x',zipfile.ZIP_DEFLATED) as archive:
  for source,name in sources:archive.write(source,ROOT.name+'/'+name)
 print(f'{len(sources)} source files: {args.output}')
if __name__=='__main__':main()
