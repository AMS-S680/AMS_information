from pathlib import Path
import json,hashlib,collections,re,csv
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'exam_deadlines'
inventory=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
pages=json.loads((OUT/'pages.json').read_text(encoding='utf-8'))
tasks=json.loads((OUT/'ocr_tasks.json').read_text(encoding='utf-8'))
ocr={(r['key'],r['page']):r for r in [json.loads(l) for l in (OUT/'ocr_pages.jsonl').read_text(encoding='utf-8').splitlines()]}
vision={(r['key'],r['page']):r for r in [json.loads(l) for l in (OUT/'vision_reviews.jsonl').read_text(encoding='utf-8').splitlines()]}
inv={i['key']:i for i in inventory}
pending=[(t[2],t[3]) for t in tasks if (t[2],t[3]) not in ocr]
failed=[r for r in ocr.values() if r.get('error')]
empty=[r for r in ocr.values() if r.get('empty')]
unresolved=[r for r in empty if not vision.get((r['key'],r['page']),{}).get('success')]
pat=re.compile(r'mid.?term|dead.?line|\bdue\s+(?:date|time|one|in|on|by)|\b(?:Sept(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s*\d|2026\s*年\s*\d+\s*月|2026[-/]\d{1,2}[-/]\d{1,2}|期中|截止(?:时间|日期)|提交.{0,20}(?:前|月|点)',re.I)
hits=[dict(source=inv[r['key']]['source'],**r) for r in ocr.values() if pat.search(r.get('text',''))]
(OUT/'ocr_date_candidates.json').write_text(json.dumps(hits,ensure_ascii=False,indent=2),encoding='utf-8')
changed=[i['source'] for i in inventory if hashlib.sha256((ROOT/i['source']).read_bytes()).hexdigest()!=i['sha256']]
events=json.loads((OUT/'events.json').read_text(encoding='utf-8'))
assert not changed,changed
assert all((ROOT/e['source']).exists() for e in events)
assert len({e['id'] for e in events})==len(events)
for e in events:
    if e['date'].startswith('2026-') and len(e['date'])==10:
        import datetime
        datetime.date.fromisoformat(e['date'])
class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a': self.links.extend(v for k,v in attrs if k=='href')
parser=Links(); parser.feed((OUT/'考试与DDL汇总.html').read_text(encoding='utf-8'))
bad_links=[url for url in parser.links if not (OUT/url.split('#')[0]).exists() and url!='识别检查报告.md']
assert not bad_links,bad_links
with (OUT/'考试与DDL汇总.csv').open(encoding='utf-8-sig',newline='') as f: assert len(list(csv.DictReader(f)))==len(events)
calls=[a for r in vision.values() for a in r.get('attempts',[])]
counts=collections.Counter(i['kind'] for i in inventory)
with (OUT/'源文件清单.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['source','kind','pages','bytes','sha256','key'],extrasaction='ignore')
    writer.writeheader(); writer.writerows(inventory)
report=[
'# 识别覆盖与检查报告','',
'本报告由当前文件与逐页记录生成。原文件未改动，全部SHA-256与扫描清单一致。','',
f'- 原文件：{len(inventory)}份；类型：{dict(counts)}。',
f'- PDF/PPTX共{counts[".pdf"]+counts[".pptx"]}份，共{sum(i.get("pages",0) for i in inventory if i["kind"] in [".pdf",".pptx"])}页/张；文字读取失败{sum("error" in i for i in inventory)}份。',
f'- 字节相同的重复文档按SHA-256去重进行OCR，对应关系见ocr_aliases.json。',
f'- 图像/OCR任务总数：{len(tasks)}；已返回：{len(ocr)}；未返回：{len(pending)}；最后一次仍报错：{len(failed)}；无OCR文字：{len(empty)}。',
f'- 无OCR文字且未取得有效图像模型复核结果：{len(unresolved)}。',
f'- 图像模型复核结果：{len(vision)}个页面/图片；有效输出：{sum(r.get("success",False) for r in vision.values())}；累计调用：{len(calls)}次。',
f'- 模型调用分布：{dict(collections.Counter(a["model"] for a in calls))}。',
f'- 图像模型返回空内容次数：{sum(a.get("empty",False) for a in calls)}；HTTP错误次数：{sum(a.get("status",200)!=200 for a in calls)}。',
f'- OCR日期候选：{len(hits)}页/图，见ocr_date_candidates.json。候选是检索线索，不自动作为正式DDL。',
f'- 汇总事项：{len(events)}条；HTML来源链接与CSV条数检查通过。','',
'## 各课程文档范围','',
'| 课程 | PDF | PPTX | PDF页数与PPT张数合计 |','| --- | --- | --- | --- |',
*[f'| {course} | {sum(i["kind"]==".pdf" and i["source"].startswith(course) for i in inventory)} | {sum(i["kind"]==".pptx" and i["source"].startswith(course) for i in inventory)} | {sum(i.get("pages",0) for i in inventory if i["source"].startswith(course) and i["kind"] in [".pdf",".pptx"])} |' for course in ['AMSC5710','AMSC5720','AMSC5730','AMSC5738']],
'','可在源文件清单.csv中查看全部文件路径、页数、大小与SHA-256。','',
'## 模型调用规则','',
'从API的/v1/models实际获得模型列表。先用当前配置模型gpt-6.1-sol；返回none、null、空内容或调用异常则按记录顺序尝试其余模型，直到得到有效输出或所有模型都已尝试。每个图片的尝试列表保存在vision_reviews.jsonl的attempts中。不强行把“图片没有日期”改成日期，也不把裁切/缺失内容当成可恢复文本。','',
'实际顺序：'+ ' → '.join(dict.fromkeys(['gpt-6.1-sol']+json.loads((OUT/'models.json').read_text())['models'])),'',
'OCR也是图像文字识别模型。其有文字输出的普通教学页使用OCR结果检索日期；关键日期页和独立照片另外用图像大模型复核，OCR无输出的页面也送入上述模型链。若第一个图像模型有有效输出，则该图片停止尝试后续模型。','',
'## 无法完整读取的源内容','',
'两份PPT无法由PowerPoint打开（已分别尝试原包与重新保存的副本）：','',
'- AMSC5730/2_Active_and_Passive_Hydrodynamic_Cloaks_Polished_Final.pptx：读取XML文字，并逐图OCR可提取的嵌入图片。','- AMSC5730/3_AI_Tuning_Poissons_Ratio_English_Polished.pptx：同上；第7页形状1、第22页形状6/7、第30页形状4/5，共5个图片引用没有可取得的嵌入图像。这里页码为1起算，形状索引为0起算。','',
'这5个引用没有可调用模型能够读取的源图，未计作已识别。其他源文件保留原样。两份PPT中提取图片的OCR page字段以“幻灯片号×1000+图片索引”编码：余数0–99为顶层形状索引，100–199为组合对象内的遍历索引加100，200及以上为XML补充图片索引加200；具体源图片见ocr_tasks.json。普通文档page字段为1起算物理页。','',
'OCR日期候选已区分课程考核安排、论文收稿/出版日期和课件引用日期；后两类不作为课程DDL。','',
'独立照片的主纸张已识别；遮挡/裁切的背景纸张不保证完整。单纯图示没有文字时，OCR为空属于正常情况，图像模型复核的内容说明见日志。','',
'## 重试日志说明','',
'OCR初次运行在输出置信度转换时发生类型错误，修正并重跑后保留历史行，最终统计采用每个(key,page)的最新行。旧错误不等于当前仍失败。没有将运行错误直接解释为源页面没有日期。','',
'## 最终待处理项','']
report+=['- 仍在运行的OCR任务：'+str(len(pending)),'- 尚无有效模型复核的OCR空结果：'+str(len(unresolved))] if pending or unresolved else ['- 所有计划的OCR任务均已返回；所有OCR空结果均已取得图像模型说明。']
if failed: report +=['- OCR失败：'+inv[r['key']]['source']+'，page='+str(r['page'])+'，'+str(r.get('error')) for r in failed]
(OUT/'识别检查报告.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
summary=dict(files=len(inventory),tasks=len(tasks),ocr_returned=len(ocr),pending=len(pending),errors=len(failed),empty=len(empty),unresolved_empty=len(unresolved),vision_pages=len(vision),model_calls=len(calls),ocr_date_candidates=len(hits),source_files_changed=changed,events=len(events))
(OUT/'audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
