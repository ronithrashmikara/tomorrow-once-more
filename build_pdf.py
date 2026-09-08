from pathlib import Path
import json, math, re, html
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle, CondPageBreak
from reportlab.platypus.tableofcontents import TableOfContents

ROOT=Path(__file__).parent
OUT=ROOT/'output/pdf/JLPT_N3_Complete_Study_Course.pdf'
W,H=595.28,841.89
M=43
CW=W-M*2
INK=colors.HexColor('#17334A'); TEAL=colors.HexColor('#007C83'); MUTED=colors.HexColor('#516274'); PALE=colors.HexColor('#EAF4F4'); LIGHT=colors.HexColor('#F2F5F7')
pdfmetrics.registerFont(TTFont('JP','C:/Windows/Fonts/meiryo.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('JPB','C:/Windows/Fonts/meiryob.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('JP',normal='JP',bold='JPB',italic='JP',boldItalic='JPB')
styles={
 'body':ParagraphStyle('body',fontName='JP',fontSize=9.1,leading=14.2,spaceAfter=6,textColor=INK),
 'small':ParagraphStyle('small',fontName='JP',fontSize=7.8,leading=11.7,spaceAfter=4,textColor=MUTED),
 'jp':ParagraphStyle('jp',fontName='JP',fontSize=10.5,leading=17,wordWrap='CJK',spaceAfter=4,textColor=INK),
 'reading':ParagraphStyle('reading',fontName='JP',fontSize=8.2,leading=13,wordWrap='CJK',spaceAfter=4,textColor=MUTED),
 'h1':ParagraphStyle('h1',fontName='JPB',fontSize=25,leading=34,spaceAfter=18,textColor=INK),
 'h2':ParagraphStyle('h2',fontName='JPB',fontSize=17,leading=24,spaceAfter=12,textColor=TEAL,keepWithNext=True),
 'h3':ParagraphStyle('h3',fontName='JPB',fontSize=11.8,leading=18,spaceBefore=9,spaceAfter=5,textColor=TEAL,wordWrap='CJK',keepWithNext=True),
 'card':ParagraphStyle('card',fontName='JPB',fontSize=13,leading=20,spaceAfter=5,textColor=INK,wordWrap='CJK',keepWithNext=True),
 'cell':ParagraphStyle('cell',fontName='JP',fontSize=8,leading=12,wordWrap='CJK',textColor=INK),
}
def esc(t):return html.escape(str(t)).replace('\n','<br/>')
def para(t,style='body',raw=False):return Paragraph(t if raw else esc(t),styles[style])
def labeled(label,t,style='body'):return para('<b>'+esc(label)+'</b> '+esc(t),style,True)
def load(n):return json.loads((ROOT/'content'/'final'/f'{n}.json').read_text(encoding='utf-8-sig'))
V,K,G,R,C=[load(n) for n in ['vocabulary','kanji','grammar','readings','reviews']]
counts={n:sum(len(l['items']) for l in d['lessons']) for n,d in [('v',V),('k',K),('g',G)]}
story=[]; keys=[]; anchors=set()
def add(t,style='body'):story.append(para(t,style))
def heading(t,key,level=0,new=True):
    if new:story.append(PageBreak())
    p=para(t,'h1' if level==0 else 'h2'); p._toc=(level,t,key); story.append(p); anchors.add(key)
def link(t,key):return '<link href="#'+key+'" color="#007C83">'+esc(t)+'</link>'
def table(rows,widths=None,header=True):
    data=[[para(c,'cell') for c in row] for row in rows]
    t=Table(data,colWidths=widths or [CW/len(rows[0])]*len(rows[0]),repeatRows=1 if header else 0,hAlign='LEFT')
    ts=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),0.6,TEAL),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT])]
    if header:ts += [('BACKGROUND',(0,0),(-1,0),PALE)]
    t.setStyle(TableStyle(ts)); story.append(t); story.append(Spacer(1,9))
def box(title,text):
    t=Table([[para(title,'h3')],[para(text)]],colWidths=[CW]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('BOX',(0,0),(-1,-1),0.5,TEAL),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,-1),(-1,-1),9)]));story.append(t);story.append(Spacer(1,12))
def question(q,number):
    prompt=q.get('question',q.get('prompt',''))
    parts=[labeled(str(number)+'.',prompt,'jp' if re.search('[一-龯ぁ-ヿ]',prompt) else 'body')]
    if q.get('options'):
        for i,o in enumerate(q['options']):parts.append(para(f'{chr(65+i)}. {o}','reading'))
    parts.append(Spacer(1,6));story.append(KeepTogether(parts))
def practice(qs,key,title='Practice | Close the lesson notes'):
    story.append(CondPageBreak(150)); add(title,'h3')
    story.append(para(link('Answers and explanations',key),'small',True))
    for i,q in enumerate(qs,1):question(q,i)
    keys.append((key,qs))

class Doc(BaseDocTemplate):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw); self.current='JLPT N3 | A course beyond N4'; self.locations={}
        self.addPageTemplates(PageTemplate(id='main',frames=Frame(M,48,CW,H-98,id='normal',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),onPage=self.page))
    def page(self,c,doc):
        c.saveState()
        if doc.page>1:
            c.setStrokeColor(TEAL);c.setLineWidth(.6);c.line(M,H-33,W-M,H-33)
            c.setFont('JP',7);c.setFillColor(MUTED);c.drawString(M,H-26,'N3 / '+self.current[:66]);c.drawRightString(W-M,27,str(doc.page))
            c.drawString(M,27,'Original lessons • English guidance • Japanese in context')
        c.restoreState()
    def afterFlowable(self,f):
        if hasattr(f,'_toc'):
            level,title,key=f._toc;self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,level=level,closed=level==0);self.notify('TOCEntry',(level,title,self.page,key));self.locations[key]=self.page
            if level==0:self.current=title

# Cover
story.append(Spacer(1,100));add('日本語能力試験','h2');add('JLPT N3','h1');add('A complete study course\nfor the learner beyond N4','h1')
story.append(Spacer(1,25))
box('32 LESSONS / ONE GUIDED ROUTE',f"{counts['v']:,} vocabulary entries • {counts['k']} kanji • {counts['g']} grammar points\n32 original readings • 8 cumulative checkpoints • separate explained answer keys")
add('Prepared for Ronit','h2');add('Study at your pace: 8, 12, or 16 weeks.','body');story.append(Spacer(1,30))
add('Research edition • 7 September 2026','small');add('An independent learning course. JLPT level assignments are study conventions, not an official exhaustive syllabus. The course assumes retention of core N5/N4 knowledge.','small')
heading('Contents','toc')
toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc0',fontName='JPB',fontSize=11,leading=17,spaceBefore=8,textColor=INK),ParagraphStyle('toc1',fontName='JP',fontSize=8.4,leading=13,leftIndent=13,textColor=MUTED)]
story.append(toc)
heading('How to use this course','how')
add('Start with Lesson 1 and follow the same numbered vocabulary (V), kanji (K), grammar (G), and reading (R) lessons. The parts are grouped for easy reference, but the route below tells you exactly what to study together. A lesson is a small unit spread over several sessions, not a promise that you can finish it in one sitting.')
table([['Within each lesson','Your task'],['1. Vocabulary V','Split the headwords into 3 or 4 small sets. Read the Japanese, retrieve the reading and meaning, then say the example.'],['2. Kanji K','Learn each character through its example words. Cover the readings and identify them in context.'],['3. Grammar G','Study one point at a time. Compare its formation and meaning with the neighbor it is easiest to confuse.'],['4. Practice','Answer V/K/G exercises without looking back. Record the reason for each error.'],['5. Integrated reading R','Read once for gist, answer questions, then consult the gloss and translation. Reread aloud.'],['6. Retrieval and listening','Recall yesterday’s material. Use the listening routine below for 15-25 minutes.']],[118,CW-118])
box('Read the Japanese first','Use romaji only to check a reading. The first four reading lessons include full kana and romaji; later passages switch to selective glosses. Vocabulary and grammar examples retain readings as a reference. Cover those lines on your first attempt. Kana spellings preserve Japanese orthography; romaji may use doubled vowels or macrons for long vowels.')
add('Vocabulary “word” is the normal written headword, including its kanji form where usual. Kana-only spellings are intentional where common; a kanji spelling is not invented for every expression. Verbs should be learned with their particle frame. Kanji on-readings are shown in katakana and kun-readings in hiragana; a dash or note means no useful reading is taught in that category, not that none has ever existed.')
add('Components and memory hints are learning aids, not claims about historical character origins. This PDF teaches recognition and useful readings; writing-from-memory drills are supplementary practice, not a separate JLPT handwriting section.')
add('Coverage and limits','h3')
add(f"The course contains {counts['v']:,} explicitly taught vocabulary entries, {counts['k']} kanji, and {counts['g']} grammar entries. These are course counts, not official requirements or a guarantee that every word on a future paper is included. Common N3 lists differ, and some foundational or neighboring-level items are retained for useful contrasts. Continue learning new words from the passages and listening; an N4 background remains part of the working vocabulary. [S1, S2]")
add('Symbols and formation shorthand','h3')
table([['Label','Meaning / example'],['V dictionary','Plain nonpast affirmative: 行く, 食べる, する.'],['Vない / Vた / Vて','行かない / 行った / 行って. Read the full pattern: it may replace part of this form.'],['V stem','ます stem: 行き, 食べ, し. It is not the dictionary form.'],['Plain clause','Verb/adjective plain forms; noun and な-adjective linking rules vary and must be checked in that entry.'],['N / い-adj / な-adj','Noun / い-adjective / な-adjective. Keep な or の only when the formation requires it.'],['Bridge','A useful refresher or adjacent-level contrast. Level boundaries vary among references.']],[108,CW-108])
heading('Study schedules and progress','schedule')
add('Choose the longest plan you can sustain. The 8-week route is intensive. Weekly counts below are approximate averages from the actual course inventory, and the final weeks still require review. A slower pace is appropriate if next-day recall is weak. Spread each week across six study days, with one lighter catch-up day.')
for weeks in [8,12,16]:
    add(f'{weeks}-week plan','h3')
    rows=[['Week','Lesson route','New words / kanji / grammar','Review checkpoint']]
    for w in range(1,weeks+1):
        start=(w-1)*32//weeks+1;end=w*32//weeks
        nc=[sum(len(d['lessons'][j-1]['items']) for j in range(start,end+1)) for d in [V,K,G]]
        checks=[str(n) for n in range(start,end+1) if n%4==0]
        rows.append([str(w),f'{start:02d}-{end:02d}',f'{nc[0]} / {nc[1]} / {nc[2]}','After '+', '.join(checks) if checks else 'Cumulative recall'])
    table(rows,[40,83,180,CW-303])
    add(f"Each week: 6 short spaced-retrieval sessions, 5-6 listening sessions, one mixed review; complete any checkpoint listed above. Average new load: about {math.ceil(counts['v']/weeks)} words, {math.ceil(counts['k']/weeks)} kanji, and {math.ceil(counts['g']/weeks)} grammar points. Adjust daily time to actual recall rather than racing a timer.",'small')
add('Suggested daily session','h3')
add('Begin with 10-15 minutes of closed-book recall. Spend 20-30 minutes on new vocabulary/kanji, 20-30 on grammar and exercises, 15-25 on listening, and 15-25 on reading or correction. The intensive plan may need two such blocks or longer weekends. These are planning suggestions, not research-based hour requirements.')
add('A practical spaced-review system','h3')
table([['When','What to retrieve'],['Day 0','Study, hide the answer, recall once; write one original sentence.'],['Day 1','Recall the reading and meaning, then use the word/pattern without copying.'],['Day 3','Mix with the next lesson. Confuse it deliberately with a close neighbor, then explain the distinction.'],['Day 7','Do a short mixed test and reread the earlier passage without support.'],['Day 14 and Day 30','Retrieve missed items plus a random sample of correct ones. Use them in a new context.']],[95,CW-95])
add('If you miss an item, reread its explanation and return it to next-day review. If you retrieve it accurately in context on two separate dates, lengthen the interval. These intervals are a workable schedule rather than a universally optimal formula. Avoid rereading alone: the attempt to recall is the core action.')
add('Progress rule','h3')
add('Use 80% on each course checkpoint as a study target, and aim to explain your choices. This is an editorial mastery rule, not a JLPT passing-score conversion. Below 80%, review the weakest skill for two sessions and retest missed ideas with fresh examples. Above 80%, continue while keeping missed items in the queue. The JLPT uses scaled scores, so do not convert these raw practice percentages into official scores.')
add('Lesson route and completion log','h3')
rows=[['Lesson','Theme','Read in this order','Recall dates / score']]
for l in V['lessons']:
    i=l['id']; rows.append([f'{i:02d}',l['title'],f'V{i:02d} → K{i:02d} → G{i:02d} → R{i:02d}','____ / ____ / ____'])
table(rows,[43,170,160,CW-373])
add('After 4, 8, 12, 16, 20, 24, 28, and 32, complete the corresponding checkpoint before starting the next lesson. Lessons 8, 16, 24, and 32 are the four major course milestones. The contents and PDF bookmarks provide direct navigation.')

heading('Part 1 | Vocabulary course','vocab')
add('Learn each item as a word in a sentence. Recall both Japanese-to-English meaning and English-to-Japanese production; if a word has several senses, the example teaches the one selected here. Revisit the same item when it appears in kanji words and reading passages.')
for l in V['lessons']:
    i=l['id'];heading(f'V{i:02d} | {l["title"]}',f'v{i}',1);add(l.get('overview',''))
    for j,x in enumerate(l['items'],1):
        ps=[para(f'{i:02d}.{j:02d}  {x["word"]}','card'),para(f'{x["reading"]}  |  {x["romaji"]}','reading'),labeled(x['meaning']+' |',x['pos']),labeled('Use:',x['usage'],'small'),para(x['example'],'jp'),para(x['example_reading'],'reading'),para(x['example_romaji'],'small'),para(x['translation']),labeled('Notice:',x['nuance'],'small'),Spacer(1,8)]
        story.append(KeepTogether(ps))
    practice(l['exercises'],f'av{i}')
    story.append(para(link(f'Next: K{i:02d}',f'k{i}')+' • '+link(f'G{i:02d}',f'g{i}')+' • '+link(f'R{i:02d}',f'r{i}'),'small',True))

heading('Part 2 | Kanji course','kanji')
add('Recognize the whole word before selecting a reading. Readings are not interchangeable: learn the specific reading attached to each example word. Recognition writing drills ask you to choose or recall the correct character. You do not need rare name readings for these lessons.')
for l in K['lessons']:
    i=l['id'];heading(f'K{i:02d} | {l["title"]}',f'k{i}',1);add(l.get('overview','Study the characters through the words below; then hide the readings and test yourself.'))
    for j,x in enumerate(l['items'],1):
        ps=[para(f'{i:02d}.{j:02d}  {x["kanji"]}  |  {x["meaning"]}','card'),labeled('On:',x['onyomi'],'reading'),labeled('Kun:',x['kunyomi'],'reading'),labeled('Romaji:',x['romaji'],'small')]
        for w in x['words']:ps.append(para(f'{w["word"]}（{w["reading"]}） - {w["meaning"]}','reading'))
        ps += [para(x['example'],'jp'),para(x['example_reading'],'reading'),para(x['translation']),labeled('Shape:',x['components'],'small'),labeled('Memory:',x['mnemonic'],'small'),labeled('Watch:',x['warning'],'small'),Spacer(1,8)]
        story.append(KeepTogether(ps))
    practice(l['exercises'],f'ak{i}')

heading('Part 3 | Grammar course','grammar')
add('Do not memorize English glosses alone. First identify the form immediately before the pattern, then what relationship the speaker intends, and finally the register. Some English translations overlap even when the Japanese grammar differs. Each point includes a short question; solutions are in the answer-key part.')
for l in G['lessons']:
    i=l['id'];heading(f'G{i:02d} | {l["title"]}',f'g{i}',1);add(l.get('overview',''))
    qs=[]
    for j,x in enumerate(l['items'],1):
        ps=[para(f'{i:02d}.{j:02d}  ～{x["pattern"].lstrip("～")}', 'card'),labeled('Meaning:',x['meaning']),labeled('Formation:',x['formation']),labeled('Use:',x['usage']),labeled('Register:',x['register'],'small'),labeled('Nuance:',x['nuance'])]
        for n,e in enumerate(x['examples'],1):ps.extend([para(str(n)+'. '+e['jp'],'jp'),para(e['reading'],'reading'),para(e['romaji'],'small'),para(e['en'])])
        ps += [labeled('Avoid:',x['mistake'],'small'),labeled('Compare:',x['comparison'],'small')]
        # Keep the heading with formation; the examples may continue naturally.
        story.append(KeepTogether(ps[:6]));story.extend(ps[6:]);story.append(Spacer(1,8))
        q=x['question']; question(q,f'G{i:02d}.{j}');qs.append(q)
    keys.append((f'agpoint{i}',qs))
    story.append(para(link('Grammar point question answers',f'agpoint{i}'),'small',True))
    practice(l['exercises'],f'ag{i}')

heading('Part 4 | Integrated reading','reading')
add('Do a first pass with the support and translation covered. Identify who is doing what, the time sequence, and the writer’s main point. Answer the questions before checking the translation. During a second pass, underline evidence for each answer. Learning passages are original and gradually become longer; they are not reproduced official exam items.')
for l in R['lessons']:
    i=l['id'];heading(f'R{i:02d} | {l["title"]}',f'r{i}',1)
    add('First pass: read for meaning, then answer.','small');add(l['jp'],'jp')
    for n,q in enumerate(l['questions'],1):question(q,n)
    add('Reading support | Consult after trying','h3');add(l['support'],'reading')
    if l.get('romaji'):add(l['romaji'],'small')
    add('Grammar and vocabulary connections','h3')
    for n in l['notes']:add(n)
    add('English translation','h3');add(l['translation']);keys.append((f'ar{i}',l['questions']))
    story.append(para(link('Answers and evidence',f'ar{i}'),'small',True))
    if i%4==0:story.append(para(link(f'Now complete checkpoint {i//4}',f'c{i}'),'body',True))
    add('Retrieval task: close this page and summarize the passage in two Japanese sentences. Then compare your meaning with the original; wording may differ.','small')

heading('Part 5 | Cumulative reviews','reviews')
add('Use closed notes. Give yourself one point per requested vocabulary meaning, kanji answer, grammar item, or reading question. For open translation tasks, accept a natural equivalent that preserves participants, time, polarity, and the target grammar relationship. These practice sets are diagnostic checkpoints, not calibrated mock exams. Record errors by skill rather than relying on one total.')
for c in C['reviews']:
    n=c['after'];heading(c['title'],f'c{n}',1);add(f'Coverage: Lessons 1-{n}. Suggested time: '+('55-70 minutes.' if n==32 else '25-40 minutes.'))
    qs=[]
    # Spread retrieval across earlier material instead of testing only the last lesson.
    idx=sorted(set([0,max(0,n//4-1),max(0,n//2-1),n-2,n-1]))
    add('A | Vocabulary recall','h3')
    for j,k in enumerate(idx):
        x=V['lessons'][k]['items'][(j*3+2)%len(V['lessons'][k]['items'])]
        q={'question':f'Give the reading and meaning of {x["word"]}. Then say its common usage aloud.','answer':f'{x["reading"]} - {x["meaning"]}. Usage: {x["usage"]}','explanation':f'Revisit V{k+1:02d}; production need not reproduce the example word for word.'};qs.append(q);question(q,len(qs))
    add('B | Kanji recognition','h3')
    for j,k in enumerate(idx):
        x=K['lessons'][k]['items'][(j*2+1)%len(K['lessons'][k]['items'])];w=x['words'][0]
        q={'question':f'Write or select the kanji word for {w["reading"]} meaning “{w["meaning"]}”.','answer':w['word'],'explanation':f'{x["kanji"]} carries the meaning {x["meaning"]}. See K{k+1:02d}.'};qs.append(q);question(q,len(qs))
    add('C | Grammar and translation','h3')
    for q in c['drills']:qs.append(q);question(q,len(qs))
    add('D | Reading','h3');add(c['jp'],'jp')
    for q in c['questions']:qs.append(q);question(q,len(qs))
    keys.append((f'ac{n}',qs));story.append(para(link('Answer key and explanations',f'ac{n}'),'small',True))
    add(f'Total: {len(qs)} tasks. Record V ____ / K ____ / G ____ / R ____. Revisit items after 1, 3, and 7 days.','small')

heading('Part 6 | Final rapid revision','revision')
add('Use these pages for retrieval after learning the full entries. The quick lists are intentionally compact. Cover the meaning column, answer aloud, then check the full lesson whenever you hesitate.')
heading('Vocabulary quick review','qv',1)
for l in V['lessons']:
    add(f'V{l["id"]:02d} | {l["title"]}','h3')
    table([['Word / reading','Meaning']] + [[x['word']+' / '+x['reading'],x['meaning']] for x in l['items']],[235,CW-235])
heading('Kanji quick review','qk',1)
for l in K['lessons']:
    add(f'K{l["id"]:02d}','h3')
    table([['Kanji','Major readings','Useful words']] + [[x['kanji'],str(x['onyomi'])+' / '+str(x['kunyomi']),'; '.join(w['word']+' ('+w['reading']+')' for w in x['words'])] for x in l['items']],[40,190,CW-230])
heading('Grammar cheat sheet','qg',1)
for l in G['lessons']:
    add(f'G{l["id"]:02d} | {l["title"]}','h3')
    table([['Pattern / meaning','Formation','Short example']]+[[x['pattern']+'\n'+x['meaning'],x['formation'],x['examples'][0]['jp']] for x in l['items']],[158,172,CW-330])
heading('Commonly confused grammar','gc',1)
for x in G.get('confusions',[]):
    add(str(x['a'])+' / '+str(x['b']),'h3');add(x['explanation'])
    for suf in ['a','b']:
        if x.get('example_'+suf):add(x['example_'+suf],'jp')
        if x.get('translation_'+suf):add(x['translation_'+suf])
heading('Commonly confused vocabulary','vc',1)
for x in V.get('confusions',[]):
    add(str(x['a'])+' / '+str(x['b']),'h3');add(x['explanation'])
    if x.get('example'):add(x['example'],'jp')
    if x.get('translation'):add(x['translation'])

heading('Part 7 | Prepare for the JLPT','exam')
add('N3 assesses understanding of everyday Japanese to an intermediate degree: reading concrete daily-life texts, grasping summary information, and following connected everyday conversations at close to natural speed. Language knowledge supports these tasks. There is no speaking interview or essay-writing section; speaking and writing exercises here are learning tools. [S2, S3]')
table([['Test section','Official allotted time'],['Vocabulary','30 minutes'],['Grammar and reading','70 minutes'],['Listening','40 minutes; the exact duration can vary with the recording.']],[330,CW-330])
add('The three scoring sections are language knowledge (vocabulary/grammar), reading, and listening, each scored from 0 to 60. N3 requires at least 95/180 overall and at least 19/60 in each scoring section. Missing a required test section results in failure. These are scaled scores, not raw percentages. Check the current official guidance and your local test instructions before test day. [S3, S4]')
add('Vocabulary and kanji strategy','h3');add('Learn reading, meaning, and one natural collocation together. For a context question, read the entire sentence before choosing. Check transitivity and the particle next to the blank. For paraphrase items, preserve degree and polarity: “not always” does not mean “never.” For kanji questions, identify the word, then check the whole compound’s reading. Keep a separate list of visually similar characters and words whose meanings you know but whose readings you cannot retrieve.')
add('Grammar strategy','h3');add('Check attachment first: stem, dictionary, ない, た, noun + の, or adjective + な. Then identify purpose, reason, contrast, time, or inference. In sentence ordering, build small fixed groups before arranging the whole sentence; read from the start afterward. In text grammar, use both the preceding and following sentences to decide the connector or reference.')
add('Reading strategy','h3');add('Scan notices for dates, prices, eligibility, exceptions, and required actions. Read the question so you know what information to retrieve, but support the answer from the passage. In opinions, track contrast markers and distinguish the writer’s view from a quoted view. Resolve それ, この, そのため, and つまり locally. A correct choice often paraphrases the evidence; shared vocabulary alone does not make a choice correct.')
add('Listening routine | 15-25 minutes most days','h3')
add('Use the official N3 workbook audio linked in the reference section. Day 1: listen to one task without reading the transcript, record your answer and confidence, and identify who must do what next. Replay once for the key details. Then read the official script, check missed sounds and words, and listen again without the script. On Day 3, replay the same task and summarize it aloud. Alternate familiar tasks with unseen ones so you do not only memorize answers. [S5]')
add('For task-based listening, note the final required action after any change of plan. For point comprehension, focus on the requested reason, choice, or detail. For summary comprehension, track the main point. For utterance expressions and quick response, identify the social purpose: accepting, declining, apologizing, asking, or confirming. Practice short shadowing after understanding the meaning, matching timing and phrase groups rather than reading romaji. The PDF provides a routine, not audio files; the linked official recordings are the listening component. [S3, S5]')
add('An original listening rehearsal','h3')
add('Ask a tutor or study partner to read the following once at a natural, clear pace while you cover the text. If studying alone, use a Japanese text-to-speech reader and verify pronunciation; synthetic speech is supplementary. Answer: What should the woman do first?')
box('Cover this script during the first listen','男：会議の資料、もう印刷しましたか。\n女：これから印刷するところです。\n男：すみません、最後のページに変更があります。先に新しいファイルを送るので、それを確認してから印刷してください。\n女：分かりました。会議室の準備は後でも大丈夫ですか。\n男：ええ、まず資料をお願いします。')
practice([{'question':'What should the woman do first? A print the old file; B check the new file when received; C prepare the meeting room; D cancel the meeting.','answer':'B - check the new file when it arrives, then print.','explanation':'先に and 確認してから establish the order. Room preparation can wait. The initial plan to print is revised.'}], 'alistening','Listening rehearsal question')
add('Time management','h3');add('During untimed practice, find your weakest item type. Then rehearse under the official section limits using official sample material. As an initial personal pacing experiment, try about 20-25 minutes for grammar and 45-50 for reading within the 70-minute combined section; adjust from actual results. This split is a study suggestion, not an official allocation. Leave time for checking answer alignment. If stuck, eliminate what you can, mark an answer, and move on. In listening, release a missed question so you can follow the next recording.')
add('Final week','h3');add('Reduce the new-item load. Revisit the error log, do mixed retrieval, read new short texts, and complete an official sample session with its recording. Diagnose weak sections independently. Check the venue, arrival instructions, identification requirements, and permitted materials from the local organizer. Keep your normal sleep routine. The aim is reliable retrieval and comprehension, not a last-minute count of memorized entries.')

heading('Part 8 | Answer keys','answers')
add('Answers are separated from practice to protect retrieval. A translation may have several natural correct versions; preserve the meaning and the grammar relationship. Use explanations to identify why an alternative fails, then write a new sentence that avoids the same error.')
for key,qs in keys:
    labels={'av':'Vocabulary','ak':'Kanji','agpoint':'Grammar point questions','ag':'Grammar lesson practice','ar':'Reading','ac':'Checkpoint'}
    prefix=next((p for p in sorted(labels,key=len,reverse=True) if key.startswith(p)),None)
    title=(labels[prefix]+' '+key[len(prefix):]) if prefix else 'Listening rehearsal'
    heading(title,key,1,new=False)
    for j,q in enumerate(qs,1):
        ps=[labeled(f'{j}.',q['answer']),labeled('Why:',q.get('explanation',''),'small')];story.append(KeepTogether(ps))
    if key.startswith('ac'):
        c=next(c for c in C['reviews'] if c['after']==int(key[2:]));add('Reading support','h3');add(c['support'],'reading');add(c['translation'])
    story.append(Spacer(1,16))

heading('Part 9 | References and source notes','sources')
add('Official facts were checked on 7 September 2026. The teaching explanations, examples, readings, and exercises are original. The resources below inform scope and verification; their explanations and copyrighted example collections have not been reproduced. A source being consulted does not make its level label official.')
sources=[('S1','JLPT FAQ: why test-content lists are no longer published','https://www.jlpt.jp/e/faq/','Official basis for the absence of a definitive vocabulary, kanji, or grammar inventory.'),('S2','JLPT N1-N5 competence summary','https://www.jlpt.jp/sp/e/about/levelsummary.html','Official N3 reading and listening objectives.'),('S3','JLPT test sections and item types','https://www.jlpt.jp/sp/e/guideline/testsections.html','Official section lengths, task types, and variation in recording time.'),('S4','JLPT scoring and pass/fail','https://www.jlpt.jp/e/guideline/results.html','Official scoring sections and thresholds.'),('S5','JLPT Official Practice Workbook and audio','https://www.jlpt.jp/e/samples/sampleindex.html','Use the N3 listening links, scripts, and answers for the external listening routine.'),('S6','JLPT N3 purposes of test items','https://www.jlpt.jp/e/guideline/pdf/n3_e.pdf','Official description of vocabulary, grammar, reading, and listening task goals.')]
seen={s[2] for s in sources}
for d in [V,K,G]:
    for s in d.get('sources',[]):
        if s['url'] not in seen:sources.append((f'S{len(sources)+1}',s['title'],s['url'],s.get('note','Study reference.')));seen.add(s['url'])
for sid,title,url,note in sources:
    add(f'[{sid}] {title}','h3');story.append(para('<link href="'+html.escape(url,quote=True)+'" color="#007C83">'+esc(url)+'</link>','small',True));add(note)
add('How to treat conflicting lists','h3');add('JLPT Sensei and Tanos are unofficial study lists; Bunpro organizes grammar for learning, and dictionaries establish readings and usage without fixing an exam syllabus. An item may be assigned to different levels across those resources. Retain common words and constructions needed for comprehension, and prioritize the official communicative objectives over any single list. Exact course inventory and validation notes appear below.')
if (ROOT/'content/quality_notes.txt').exists():add((ROOT/'content/quality_notes.txt').read_text(encoding='utf-8'))
else:add('This edition combines independent section drafting, editorial review, duplicate and field checks, Japanese glyph checks, and PDF layout review. Machine validation cannot certify every nuance; dictionary and contextual checks are used when resolving uncertainties.')
add('Your next step','h3');add('After the final review, use an unseen official practice set with the official audio. Continue the error log and target the weakest skill. Return to the exact lesson behind each error instead of restarting the whole course.')
doc=Doc(str(OUT),pagesize=(W,H),leftMargin=M,rightMargin=M,topMargin=50,bottomMargin=48,title='JLPT N3 - Complete Study Course',author='Prepared for Ronit',subject='Vocabulary, kanji, grammar, reading, reviews, and JLPT preparation')
doc.multiBuild(story)
(ROOT/'tmp/pdfs/page_map.json').write_text(json.dumps(doc.locations,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(OUT)); print('Pages:',doc.page,'Counts:',counts)
