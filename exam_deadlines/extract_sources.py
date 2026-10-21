from pathlib import Path
import fitz, json, hashlib, re, zipfile, posixpath
from lxml import etree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'exam_deadlines'
(OUT/'texts').mkdir(parents=True,exist_ok=True)
(OUT/'images').mkdir(exist_ok=True)
records=[]; inventory=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or '.git' in p.parts or OUT in p.parents: continue
    ext=p.suffix.lower()
    if ext not in ['.pdf','.pptx','.ppt','.txt','.docx','.jpg','.jpeg','.png','.heic']: continue
    rel=p.relative_to(ROOT).as_posix(); key=hashlib.sha256(rel.encode()).hexdigest()[:12]
    item=dict(source=rel,key=key,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),kind=ext)
    try:
        if ext=='.pdf':
            doc=fitz.open(p); item['pages']=len(doc)
            for n,page in enumerate(doc,1):
                annotations='\n'.join(a.info.get('content','') for a in (page.annots() or []))
                records.append(dict(source=rel,key=key,page=n,text=page.get_text()+ ('\n[Annotations]\n'+annotations if annotations else ''),images=len(page.get_images())))
        elif ext in ['.pptx','.docx']:
            with zipfile.ZipFile(p) as z:
                names=sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)],key=lambda n:int(re.search(r'slide(\d+)',n).group(1))) if ext=='.pptx' else ['word/document.xml']
                item['pages']=len(names)
                for n,name in enumerate(names,1):
                    xml=etree.fromstring(z.read(name)); text='\n'.join(xml.xpath('//*[local-name()="t"]/text()'))
                    if ext=='.pptx':
                        relname=f'ppt/slides/_rels/slide{n}.xml.rels'
                        note=''
                        if relname in z.namelist():
                            rels=etree.fromstring(z.read(relname))
                            links=[e.get('Target') for e in rels if e.get('Type','').endswith('/notesSlide')]
                            if links: note=posixpath.normpath(posixpath.join('ppt/slides',links[0]))
                        if note and note in z.namelist():
                            nt='\n'.join(etree.fromstring(z.read(note)).xpath('//*[local-name()="t"]/text()'))
                            if nt.strip(): text+='\n[Speaker notes]\n'+nt
                    records.append(dict(source=rel,key=key,page=n,text=text,images=len(xml.xpath('//*[local-name()="pic"]'))))
        elif ext=='.txt':
            records.append(dict(source=rel,key=key,page=1,text=p.read_text(encoding='utf-8-sig'),images=0))
        else: item['pages']=1
    except Exception as e: item['error']=str(e)
    inventory.append(item)
for item in inventory:
    rows=[r for r in records if r['source']==item['source']]
    (OUT/'texts'/f"{item['key']}.txt").write_text('\n\n'.join(f"=== PAGE {r['page']} ===\n{r['text']}" for r in rows),encoding='utf-8')
(OUT/'inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'pages.json').write_text(json.dumps(records,ensure_ascii=False),encoding='utf-8')
pat=re.compile(r'mid.?term|dead\s?line|\bdue\b|\bsubmit|\bsubmission|\bquiz|\bexam|\bproject|\bpresentation|期中|截止|提交|测验|考核|考試|考试|小组|分组',re.I)
hits=[r for r in records if pat.search(r['text'])]
(OUT/'candidates.json').write_text(json.dumps(hits,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(files=len(inventory),pdf=sum(i['kind']=='.pdf' for i in inventory),pptx=sum(i['kind']=='.pptx' for i in inventory),pages=len(records),candidates=len(hits),errors=[i for i in inventory if 'error'in i]),ensure_ascii=False))
