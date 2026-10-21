from pathlib import Path
import json,csv,html,datetime,re,collections
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'exam_deadlines'
inventory=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
def src(fragment):
    rows=[i for i in inventory if fragment in i['source']]
    assert len(rows)==1,(fragment,len(rows))
    return rows[0]['source']
I5710=src('/EN/1.CourseIntroduction_5710')
I5720=src('/EN/AMS5720_Course Introduction')
I5730=src('/EN/Week1_Introduction')
I5738=src('/EN/Notes for the course')
R5720=src('/9.22/晶体缺陷与断裂.txt')
events=[]
def add(course,item,date,time,kind,certainty,source,page,quote,notes='',end='',sort=''):
    events.append(dict(course=course,item=item,date=date,end_date=end,time=time,kind=kind,certainty=certainty,source=source,page=page,evidence=quote,notes=notes,sort=sort or date))
add('AMSC5738','Homework 1：Vacuum','2026-09-23','23:30','作业DDL','文件明确',src('/Homework/Homework 1 Vacuum.pdf'),4,'by 11:30 pm on 23 September 2026 (Wednesday)','Blackboard 提交；已过文件所列日期。')
add('AMSC5710','Quiz 1','2026-09-28','1小时；开始时刻未写','测验','试卷照片确认',src('/Quiz/1/IMG_0612.HEIC'),1,'Quiz 1 AMSC 5710 / (1hr) / Sept 28th, 2026','课程介绍第11页一致；范围：Vacuum、XPS、UPS、AES。')
add('AMSC5720','项目单人/双人分组决定','2026-10-05','未写具体时刻','项目DDL','录音转写；待通知核对',R5720,1,'email your decision to our TA by 5th of October','转写约 [2:30:44]，第2471行；未报则按单人处理。')
add('AMSC5720','公布最终分组','2026-10-06','课堂内','项目里程碑','录音转写；待通知核对',R5720,1,'6th October I will release the final grouping','第2483行；这是公布节点，不是提交DDL。')
add('AMSC5738','Homework 2：Evaporation','2026-10-07','23:30','作业DDL','文件明确',src('/Homework/Homework 2 Evaporation.pdf'),6,'by 11:30 pm on 7 October 2026 (Wednesday)','Blackboard 提交。')
add('AMSC5720','项目选题及展示时间抽签/选择','2026-10-13','课堂内；课表18:30–21:15','项目里程碑','录音转写并有后续转写支持',R5720,1,'13th of October ... selection of presentation title and time during the class','第2495行；10月6日Word转写再次说明下周课堂确定选题与时间。')
add('AMSC5720','材料科学作业：9题/50分','2026-10-22','23:59','作业DDL','本地中英文题面一致',src('/Homework/Materials_Science_Assignment_English.pdf'),1,'Due time: 11:59 pm, 22nd Oct, 2026.','手写后扫描合并为一个PDF上传Blackboard；仅允许提交一次。本地题面未标明Assignment编号。')
add('AMSC5738','期中考试','2026-10 下旬/月底','未写','期中考试','只有时间范围',I5738,7,'Mid-term (end of Oct. 2026; final: 7–10 Dec. 2026)','不能据此确定某一天、考试地点或开始时刻。',sort='2026-10-25')
add('AMSC5738','Homework 3：Deposition','2026-10-28','23:30','作业DDL','文件明确',src('/Homework/Homework 3 Deposition.pdf'),5,'by 11:30 pm on 28 October 2026 (Wednesday)','Blackboard 提交。')
add('AMSC5710','Project presentation：第1场','2026-11-16','课堂内；课程时段12:30–15:15','项目展示','课表安排',I5710,11,'Week 11 (Nov 16th) Project presentation (10 groups, 3-4 person/group, ~13 min each)','组别对应哪一场及PPT上传时间未在本地材料中确认；课程教室Wen Lan Tang LG204。')
add('AMSC5710','Project presentation：第2场','2026-11-23','课堂内；课程时段12:30–15:15','项目展示','课表安排',I5710,11,'Week 12 (Nov 23th) Project presentation (10 groups, 3-4 person/group, ~13 min each)','原课件序数后缀照录；单组具体时间、提交DDL未写。')
add('AMSC5720','Project Assessment：第1场','2026-11-24','课堂内；课程时段18:30–21:15','项目展示','暂定课表',I5720,5,'Nov 24 Project Assessment','原表标题 Detailed Schedule (tentative)；个人展示组次及幻灯片提交DDL未写。')
add('AMSC5730','Final presentation：第1场','2026-11-26','课堂内；课程时段18:30–21:15','项目展示','课表安排',I5730,45,'Week 12 (Nov 26th) Final presentation (LI)','课程一般教室Cheng Yu Tung Building 209A；该场无另列地点，组别/上传DDL待确认。')
add('AMSC5730','Final presentation：改期场','2026-11-28','10:30–13:00','项目展示','课表明确改期',I5730,45,'Dec 3th change to Nov 28th, 10:30-13:00, SC L4','地点SC L4；12月3日是原定汇报日，已改期，不重复列为另一场。')
add('AMSC5710','Quiz 2：Integrated test','2026-11-30','课堂内；具体考试时长未写','测验','课表安排',I5710,11,'Week 13 (Nov 30th) Tutorial(Homework Review)/Quiz 2 (Integrated test)','综合测试。课程考核写两次Quiz合计30%（10%+20%）；此处不将Quiz 2擅自改称期末统考。')
add('AMSC5720','Project Assessment / Revision：第2场','2026-12-01','课堂内；课程时段18:30–21:15','项目展示','暂定课表',I5720,5,'Dec 1 Project Assessment/Revision','并非每位学生两天都要展示；以组别排期为准。')
add('AMSC5738','Oral presentations','2026-12-01','未写个人时段','项目展示','只有时间范围',I5738,7,'Oral presentations (1–4 Dec. 2026)','每位学生的展示日期、选题/分组及文件上传DDL待确认。',end='2026-12-04')
add('AMSC5738','期末考试','2026-12-07','未写','期末考试','只有时间范围',I5738,7,'final: 7–10 Dec. 2026','是给定考试日期窗口，不表示连续四天考试。',end='2026-12-10')
add('AMSC5730','Group essay','待确认（若以12月3日为最后正式教学日，则推算12月10日）','未写','论文DDL','相对规则；具体日期待确认',I5730,4,'Due one week after the last official teaching day of the course (Dec. 3rd).','12月10日是按12月3日+7天推算，并非文件明确写出的Essay截止日期；汇报改至11月28日是否影响Essay规则，本地材料没有说明。不要将12月3日、12月5日或12月10日当作已确认DDL。',sort='2026-12-10')
add('AMSC5710','Homework：共4次；含Assignment 1/2','发布后一周','具体时刻未写','作业DDL','只有相对规则',I5710,4,'4 Assignments on Blackboard, due in one week after announcement','Assignment 1原题第1页也写One week after announcement；Assignment 2原题未列截止日期。缺少各次发布时间，不能换算日历日期。',sort='9999')
add('AMSC5720','第二份作业/其余作业节点','待确认','未写','作业DDL','未找到可靠具体日期',I5720,4,'Assignments (20%, 10% each) / Assignment 1 / Assignment 2','9月22日转写关于Assignment due/Assignment two的片段不清楚，不据此编造日期；10月22日那份题面未标编号，不能可靠分配到Assignment 1/2。',sort='9999')
add('AMSC5720','Final Exam','待RES通知','未写','期末考试','文件未给日期',I5720,4,'Centralized (RES will inform date/venue), cover all topics','未在当前考核方案中找到单列的期中考试；这不证明后续不会另发通知。',sort='9999')
add('AMSC5730','Presentation/Essay分组、选题','待确认','先到先得；未列日期','项目DDL','文件未给日期',I5730,4,'Presentation topics are provided (first come first serve) / Essay topics are provided (first come first serve)','Presentation：20组，每组3–4人，10分钟报告+3分钟问答；Essay：25组，每组2–3人，最多5页正文，单倍行距，12号字，说明个人贡献。',sort='9999')
add('AMSC5738','Homework 4/5；展示选题与提交','待确认','未写','作业/项目DDL','文件未给日期',I5738,3,'Homework assignments (5×) / Presentation (1×)','本地只找到Homework 1、2、3原题；未找到Homework 4/5截止日期或展示文件提交DDL。',sort='9999')
events.sort(key=lambda x:(x['sort'],x['course'],x['item']))
for n,e in enumerate(events,1): e['id']=f'E{n:02}'
(OUT/'events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
fields=['id','course','item','date','end_date','time','kind','certainty','source','page','evidence','notes']
with (OUT/'考试与DDL汇总.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(events)
def link(e):
    path='../'+e['source']; path+=f"#page={e['page']}" if e['source'].endswith('.pdf') else ''
    return f"[原文件，第{e['page']}页/张](<{path}>)"
md=['# 2026–2027 第一学期：考试、项目与作业DDL汇总','',
'整理基准日：2026-10-19。范围为当前本地项目文件；没有登录Blackboard查询后续公告。文件未明确写时区，以下保留课程材料的本地时间，安排日历时暂按香港时间（Asia/Hong_Kong，UTC+8）理解，不按电脑的America/Chicago时区换算。年份按2026–2027第一学期课程背景整理；只写月日的条目没有额外的年份证据。','',
'## 最近期要处理的事项','',
'- **10月22日23:59：AMSC5720材料科学作业。** 手写、扫描合并成一个PDF、Blackboard提交，题面注明仅允许提交一次。','- **10月底：AMSC5738期中考试。** 本地文件只有“end of Oct. 2026”，具体日期、时间和地点未找到。','- **10月28日23:30：AMSC5738 Homework 3（Deposition）。**','- **11月16日起进入项目汇报期。** 个人所属组次和PPT上传DDL仍需对照教师/TA通知。','',
'## 全部事项与原始证据','',
'“文件明确”表示项目文件写出了日期，并非已经核对最新公告。“课表安排”仍可能改动；“暂定课表”“时间范围”“推算”“转写”均保留相应限制。展示当天不自动等于PPT上传截止日。','',
'| 编号 | 课程 | 事项 | 日期/区间 | 时刻/时长 | 依据状态 |','| --- | --- | --- | --- | --- | --- |']
for e in events:
    date=e['date']+(' 至 '+e['end_date'] if e['end_date'] else '')
    md.append(f"| {e['id']} | {e['course']} | {e['item']} | {date} | {e['time']} | {e['certainty']} |")
md+=['','## 逐条来源与执行要求','']
for e in events:
    md +=[f"### {e['id']} · {e['course']} · {e['item']}",'',f"- 日期：{e['date']}"+(' 至 '+e['end_date'] if e['end_date'] else '')+f"；时间：{e['time']}。",f"- 证据状态：{e['certainty']}。",f"- 来源：{link(e)}；`{e['source']}`。",f"- 原文摘录：{e['evidence']}",f"- 说明：{e['notes']}",'']
md+=['## 需要向Blackboard或TA核实的关键信息','',
'1. AMSC5738期中考试的具体日期、开始时间和地点。当前材料只写10月底。','2. AMSC5730 Essay的正式截止日期。12月10日仅是按“12月3日后一周”的条件推算；11月28日汇报改期是否联动修改Essay DDL，没有证据。','3. AMSC5710四次作业的实际发布日期/截止日期，及各组11月16日或23日的展示分配。','4. AMSC5720各组11月24日或12月1日的展示排期、PPT上传截止时间、另一份作业的日期及RES期末考试通知。','5. AMSC5738 Homework 4/5的题面与日期，以及12月1–4日个人口头报告安排。','6. 所有课程项目的PPT/Essay上传入口及是否早于展示日截止。当前课表只能证明展示安排。','',
'## 材料中的冲突与识别限制','',
'- AMSC5730第45页明确将12月3日的Final presentation改至11月28日10:30–13:00、SC L4；不能继续按12月3日安排这场汇报。','- AMSC5738课程Notes第3页写测试60%、作业15%、展示25%；catalog第3页写测试55%、作业15%、展示30%。两份材料不一致，汇总不替教师判断最终版本。','- AMSC5738 Notes第7页假期行写“19 Sept. 2026, Chung Yeung Festival”，与另课课表中的10月19日假期存在可疑不一致。该行不用于推导任何考试或截止日期。','- AMSC5720录音转写含“Sunday 2nd of September”“midterm festival”等明显可疑识别；本报告只保留清楚的10月5日分组、10月13日选题等节点，并标记为转写来源，不将“midterm festival”误作期中考试。','- 两份PPT（Hydrodynamic Cloaks、AI Tuning Poissons Ratio）PowerPoint无法打开；已读取其XML文字及可提取嵌入图片。后一份第7、22、30页有共5个无法取得的图片引用，无法通过换模型恢复缺失源图；不能声称这些引用已识别。','- 独立照片中被遮挡或裁切的背景纸张不能完整识别；主试卷和可见内容已经核对。','- 所有日期事实均以本地课程材料为依据；未用网上别的学期或课程的安排填补空缺。','',
'## 文件清单与识别记录','',
'- `inventory.json`：90份纳入检索的源文件，含51份PDF、15份PPTX、14份TXT、2份DOCX、8张独立图片；每份有相对路径、大小和SHA-256。','- `pages.json`、`texts/`：全部PDF/PPTX文字层、可读取的讲者备注、PDF批注以及补充文本。','- `ocr_tasks.json`、`ocr_pages.jsonl`：包含图片的页面、文字稀少页面及关键日期页面的OCR记录；失败与重试均可追溯。','- `vision_reviews.jsonl`：关键日期页、独立照片及OCR无输出图片的模型识别结果和逐次模型调用记录。','- `models.json`：当前API实际列出的模型；识别请求先用当前配置模型，返回none、null、空内容或调用失败时顺序切换其余模型，直到有效输出或全部尝试完。返回“未发现日期”但包含清楚的图片内容说明，也属于有效输出。','- `识别检查报告.md`：本次最终覆盖数量、模型调用和不可读内容统计。','']
(OUT/'考试与DDL汇总.md').write_text('\n'.join(md),encoding='utf-8')
# A standalone readable HTML table, with filters and source links.
rows=[]
for e in events:
    date=e['date']+(' 至 '+e['end_date'] if e['end_date'] else '')
    url='../'+e['source']+(f"#page={e['page']}" if e['source'].endswith('.pdf') else '')
    cells=[e['course'],e['item'],date,e['time'],e['certainty']]
    rows.append('<tr data-course="'+e['course']+'">'+''.join('<td>'+html.escape(t)+'</td>' for t in cells)+'<td>'+html.escape(e['notes'])+'<br><a href="'+html.escape(url,quote=True)+'">来源，第'+str(e['page'])+'页/张</a><details><summary>原文</summary>'+html.escape(e['evidence'])+'</details></td></tr>')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>考试与DDL汇总</title><style>body{font:16px/1.65 system-ui,"Microsoft YaHei",sans-serif;max-width:1500px;margin:32px auto;padding:0 20px;color:#202d3b;background:#fafafa}h1{font-size:28px}p{max-width:1000px}a{color:#1356a0}table{border-collapse:collapse;width:100%;background:white}td,th{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #ddd}th{background:#e7edf4;position:sticky;top:0}td:nth-child(2){min-width:180px}td:last-child{min-width:280px}select,input{padding:9px;margin:8px 8px 20px 0;font:inherit}section{overflow:auto}small{color:#566}details{margin-top:5px}</style><h1>2026第一学期 · 考试与DDL</h1><p>来源：当前本地课程资料，整理于2026-10-19。未核对Blackboard后续公告。时间保留课程原文，暂按香港时间理解。展示日期与文件上传DDL分别核对。</p><p><strong>近期：10/22 23:59 AMSC5720作业；10月底 AMSC5738期中（具体日期待确认）；10/28 23:30 AMSC5738作业3。</strong></p><p>AMSC5730一场汇报已从12/3改到11/28 10:30–13:00，SC L4。Essay按12/3后一周推算为12/10，但未取得明确的最终截止日期。</p><label>课程 <select id="course"><option value="">全部</option><option>AMSC5710</option><option>AMSC5720</option><option>AMSC5730</option><option>AMSC5738</option></select></label><label>搜索 <input id="search" placeholder="期中、作业、展示……"></label><p><a href="考试与DDL汇总.md">完整说明与逐条证据</a> · <a href="考试与DDL汇总.csv">CSV表格</a> · <a href="识别检查报告.md">识别检查报告</a></p><section><table><thead><tr><th>课程</th><th>事项</th><th>日期/区间</th><th>时刻/时长</th><th>依据状态</th><th>说明与来源</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></section><script>function filter(){let c=document.querySelector('#course').value,q=document.querySelector('#search').value.toLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!!((c&&r.dataset.course!==c)||(q&&!r.textContent.toLowerCase().includes(q))))}document.querySelector('#course').addEventListener('change',filter);document.querySelector('#search').addEventListener('input',filter)</script></html>'''
(OUT/'考试与DDL汇总.html').write_text(page,encoding='utf-8')
print('Created MD/HTML/CSV with',len(events),'events')
