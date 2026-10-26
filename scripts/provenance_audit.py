"""Read-only source comparison. Report locations/hashes, not copied source excerpts."""
import argparse,ast,collections,hashlib,json,re,subprocess
from pathlib import Path


def corpus(root):
    names=set(subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=root).decode().split('\0'))-{''}
    out=[]
    for name in sorted(names):
        path=root/name
        if path.is_file() and not path.is_symlink():out.append((name,path.read_bytes()))
    return out


def audit(local,reference):
    ours=corpus(local);theirs=corpus(reference);texts=[];hashes=collections.defaultdict(list)
    for name,data in theirs:
        hashes[hashlib.sha256(data).hexdigest()].append(name)
        if b'\0' not in data:
            try:texts.append((name,data.decode('utf-8')))
            except UnicodeError:pass
    exact=[{'local':name,'source':hashes[hashlib.sha256(data).hexdigest()][:8]} for name,data in ours if hashlib.sha256(data).hexdigest() in hashes]
    def lines(text):return [(i+1,re.sub(r'\s+',' ',line).strip()) for i,line in enumerate(text.splitlines()) if line.strip()]
    windows=collections.defaultdict(list);literals={}
    for name,data in ours:
        try:text=data.decode('utf-8')
        except UnicodeError:continue
        rows=lines(text)
        for i in range(len(rows)-4):
            block='\n'.join(line for _,line in rows[i:i+5])
            if len(block)>=150:windows[hashlib.sha256(block.encode()).digest()].append((name,rows[i][0]))
        if name.endswith('.py'):
            try:tree=ast.parse(text)
            except (SyntaxError,ValueError):continue
            for node in ast.walk(tree):
                if isinstance(node,ast.Constant) and isinstance(node.value,str) and len(node.value)>=20:
                    literals.setdefault(node.value,[]).append({'path':name,'line':node.lineno})
    blocks={}
    for name,text in texts:
        rows=lines(text)
        for i in range(len(rows)-4):
            block='\n'.join(line for _,line in rows[i:i+5])
            if len(block)<150:continue
            for path,line in windows.get(hashlib.sha256(block.encode()).digest(),[]):blocks.setdefault((path,name),[]).append((line,rows[i][0]))
    strings=[]
    for value,locations in literals.items():
        found=[]
        for name,text in texts:
            offset=text.find(value)
            if offset>=0:found.append({'path':name,'line':text.count('\n',0,offset)+1})
        if found:strings.append({'local':locations,'source':found[:8],'text_sha256':hashlib.sha256(value.encode()).hexdigest(),'length':len(value)})
    return {'reference_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=reference,text=True).strip(),
            'local_base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=local,text=True).strip(),
            'local_files':len(ours),'reference_files':len(theirs),'reference_text_files':len(texts),
            'corpus_sha256':hashlib.sha256(''.join(n+' '+hashlib.sha256(b).hexdigest()+'\n' for n,b in theirs).encode()).hexdigest(),
            'exact_files':exact,'five_line_matches':[{'local':a,'source':b,'windows':len(rows),'first_locations':rows[:3]} for (a,b),rows in blocks.items()],
            'python_literal_matches':strings}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--reference',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    report=audit(Path(__file__).resolve().parents[1],args.reference.expanduser());args.out.write_text(json.dumps(report,indent=2)+'\n')
    print('Compared',report['local_files'],'local files with',report['reference_files'],'reference files; report:',args.out)
