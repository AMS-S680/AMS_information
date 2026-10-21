from pathlib import Path
import json,base64,requests,tomllib,time,re,io,sys,threading
import pymupdf as fitz
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'exam_deadlines'; register_heif_opener()
HOME=Path.home()/'.codex'
C=tomllib.loads((HOME/'config.toml').read_text(encoding='utf-8'))
BASE=C['model_providers'][C['model_provider']]['base_url'].rstrip('/')
AUTH=json.loads((HOME/'auth.json').read_text(encoding='utf-8'))['OPENAI_API_KEY']
models=json.loads((OUT/'models.json').read_text())['models']
models=list(dict.fromkeys([C['model']]+models))
lock=threading.Lock()
PROMPT='''Read this course-material image carefully. Return a JSON object with keys readable (boolean), summary (Chinese), dates (array of objects with event, date_as_printed, time_as_printed, evidence), issues (array). Extract ALL visible course assessment dates: midterm, final exam, quizzes, project grouping, topic selection, presentation, essay, homework deadlines. Preserve exact printed dates, ambiguity and rescheduling. Do not infer a specific date from a date range. If no assessment dates appear, return a nonempty JSON with dates: [] and a brief description of the visible content. Do not answer just null/none. State unreadable content clearly. For timetables transcribe the relevant rows faithfully. A meaningful no-date finding is a valid result.'''
def content_text(data):
    parts=[]
    if isinstance(data.get('output_text'),str): parts.append(data['output_text'])
    for item in data.get('output',[]):
        for c in item.get('content',[]):
            if isinstance(c.get('text'),str): parts.append(c['text'])
    for choice in data.get('choices',[]):
        t=choice.get('message',{}).get('content')
        if isinstance(t,str): parts.append(t)
    return '\n'.join(parts).strip()
def review(task):
    source,key,page,path=task
    try:
        if str(path).lower().endswith('.pdf'):
            with fitz.open(path) as doc:
                pg=doc[page-1]; s=min(2.2,2000/max(pg.rect.width,pg.rect.height)); pix=pg.get_pixmap(matrix=fitz.Matrix(s,s),alpha=False); im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        else:
            if str(path).lower().endswith('.wmf') and Path(str(path)+'.png').exists(): path=str(path)+'.png'
            im=ImageOps.exif_transpose(Image.open(path)).convert('RGB'); im.thumbnail((2200,2200))
        buf=io.BytesIO(); im.save(buf,format='JPEG',quality=90)
        (OUT/'images'/f'{key}_p{page}.jpg').write_bytes(buf.getvalue())
        url='data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode()
        attempts=[]
        for model in models:
            begin=time.time()
            try:
                payload={'model':model,'input':[{'role':'user','content':[{'type':'input_text','text':PROMPT},{'type':'input_image','image_url':url}]}],'max_output_tokens':3500}
                r=requests.post(BASE+'/v1/responses',headers={'Authorization':'Bearer '+AUTH},json=payload,timeout=(20,110))
                if r.status_code!=200:
                    attempts.append(dict(model=model,status=r.status_code,reason='HTTP error',seconds=round(time.time()-begin,1))); continue
                try: data=r.json()
                except ValueError:
                    data={}
                    for line in r.text.splitlines():
                        if line.startswith('data: '):
                            try:
                                obj=json.loads(line[6:])
                                if obj.get('response'): data=obj['response']
                            except ValueError: pass
                text=content_text(data)
                empty=text.strip().lower() in ['', 'none','null','nil','undefined','no output','无','没有输出']
                attempts.append(dict(model=model,status=r.status_code,empty=empty,seconds=round(time.time()-begin,1)))
                if empty: continue
                result=dict(source=source,key=key,page=page,model=model,text=text,attempts=attempts,success=True)
                break
            except Exception as e: attempts.append(dict(model=model,reason=type(e).__name__,seconds=round(time.time()-begin,1)))
        else: result=dict(source=source,key=key,page=page,success=False,attempts=attempts,text='')
    except Exception as e: result=dict(source=source,key=key,page=page,success=False,error=str(e),attempts=[])
    with lock:
        with (OUT/'vision_reviews.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(result,ensure_ascii=False)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='text'},ensure_ascii=False),flush=True)
    return result
def main():
    inv=json.loads((OUT/'inventory.json').read_text(encoding='utf-8')); tasks=[]
    picks={'1.CourseIntroduction_5710(1).pptx':[3,4,11],'Week1_Introduction(1).pptx':[4,45],'AMS5720_Course Introduction_AY26-27.pdf':[4,5,7],'Notes for the course.pdf':[3,7],'Homework 1 Vacuum.pdf':[4],'Homework 2 Evaporation.pdf':[6],'Homework 3 Deposition.pdf':[5],'Materials_Science_Assignment_English.pdf':[1],'材料科学作业题目_中文版.pdf':[1],'Assignment 1 (XPS instrumentation).pdf':[1]}
    for item in inv:
        source=item['source']; key=item['key']; name=Path(source).name
        if item['kind'] in ['.jpg','.jpeg','.png','.heic']: tasks.append((source,key,1,str(ROOT/source)))
        elif name in picks and '/CN/' not in source:
            path=OUT/'rendered_ppt'/f'{key}.pdf' if item['kind']=='.pptx' else ROOT/source
            tasks.extend((source,key,n,str(path)) for n in picks[name])
    if '--empty-ocr' in sys.argv:
        tasks=[]
        raw={(r['key'],r['page']):r for r in [json.loads(l) for l in (OUT/'ocr_pages.jsonl').read_text(encoding='utf-8').splitlines()]}
        lookup={(t[2],t[3]):t for t in json.loads((OUT/'ocr_tasks.json').read_text(encoding='utf-8'))}
        for row in raw.values():
            if not row['empty']: continue
            task=lookup[(row['key'],row['page'])]; item=next(i for i in inv if i['key']==row['key'])
            tasks.append((item['source'],row['key'],row['page'],task[1]))
    done=set()
    if (OUT/'vision_reviews.jsonl').exists():
        done={(r['key'],r['page']) for r in [json.loads(l) for l in (OUT/'vision_reviews.jsonl').read_text(encoding='utf-8').splitlines()] if r.get('success')}
    tasks=[t for t in tasks if (t[1],t[2]) not in done]
    print('Tasks',len(tasks),'model order',models,flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(review,tasks))
if __name__=='__main__':main()
