"""Presentation-only wrapper around the frozen public-evidence exporter."""
import argparse,hashlib,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from muse_guard.site import export_site
ROOT=Path(__file__).resolve().parents[1]
REPO='https://github.com/jeshwanthsingh/muse-guard'
def export(out):
 out=Path(out)
 if out.exists():raise ValueError('Choose a new output folder')
 export_site(sorted((ROOT/'demo/records').glob('*.json')),out)
 p=out/'index.html';page=p.read_text()
 # Titles are display labels only; evidence JSON and verdicts remain untouched.
 old='<h2>Refund policy</h2>'
 if page.count(old)!=2:raise ValueError('Expected exactly two refund cards')
 page=page.replace(old,'<h2>Refund policy - conflict</h2>',1).replace(old,'<h2>Refund policy - normal task</h2>',1)
 anchor='stop, decide, repair.</h1>'
 page=page.replace(anchor,anchor+'<p>muse-guard finds every conflicting action among the confirmed rules and declared inputs, then independently checks the fix against every input in the approved rule table.</p><ol class="demo-steps" aria-label="Recovery steps"><li>Attempt</li><li>Clash found</li><li>You decide</li><li>Checked</li></ol>')
 page=page.replace('</header>','<a class="github-link" href="'+REPO+'" rel="noreferrer">GitHub ↗</a></header>')
 page=page.replace('<div class="run-grid">','<p><a href="continuous/index.html">Open the continuous spec → decision → recheck demo (fake responses)</a></p><div class="run-grid">')
 p.write_text(page)
 from submission_tools.demo_boundary import panel
 for target in (out/'runs').glob('*.html'):
  target.write_text(target.read_text().replace('<main>','<main>'+panel(target.stem),1))
 css=out/'style.css';css.write_text(css.read_text()+'''\n.demo-steps{display:flex;gap:12px;list-style:none;padding:0;margin:12px 0 16px;counter-reset:step}.demo-steps li{font-size:14px;background:#e9edf4;padding:7px 12px;border-radius:5px}.demo-steps li+li:before{content:"→ ";color:#52647d}.github-link{font-size:15px;color:#2454bb}.site-intro p{margin:10px 0;font-size:16px}.run-card{min-height:120px;padding:12px 20px}.run-card h2{font-size:20px;margin:6px 0}.run-card p{font-size:14px;margin:6px 0}.site-intro h1{font-size:30px;line-height:1.1}.site-intro p:last-child{font-size:14px}.site-intro{margin-bottom:16px}.site-footer{font-size:12px;margin-top:16px}@media(max-width:700px){.demo-steps{flex-wrap:wrap}}\n''')
 import shutil
 source=ROOT/'demo/continuous/recorded'
 if source.exists():shutil.copytree(source,out/'continuous')
 from muse_guard.site import scan_text
 for target in out.rglob('*'):
  if target.is_file():scan_text(target.read_text().replace(REPO,''))
 files={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json'}
 (out/'manifest.json').write_text(json.dumps({'schema':1,'kind':'submission recorded demo','presentation_only':True,'allowed_external_link':REPO,'files':files},indent=2)+'\n')
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(export(a.out))
