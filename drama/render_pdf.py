from pathlib import Path
import re,json,html,math
from collections import defaultdict
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,KeepTogether,Table,TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from build_drama import PROMPT,inventory,GROUPS
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'output/pdf/Tomorrow_Once_More_Opening_Hour.pdf';OUT.parent.mkdir(parents=True,exist_ok=True)
INK=colors.HexColor('#213747'); TEAL=colors.HexColor('#137C80'); GRAY=colors.HexColor('#596878'); PALE=colors.HexColor('#EDF5F4')
pdfmetrics.registerFont(TTFont('JP','C:/Windows/Fonts/meiryo.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('JPB','C:/Windows/Fonts/meiryob.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('JP',normal='JP',bold='JPB',italic='JP',boldItalic='JPB')
ST={
 'body':ParagraphStyle('body',fontName='JP',fontSize=9,leading=14,spaceAfter=6,textColor=INK,wordWrap='CJK'),
 'en':ParagraphStyle('en',fontName='JP',fontSize=8.1,leading=12,spaceAfter=7,textColor=GRAY),
 'jp':ParagraphStyle('jp',fontName='JP',fontSize=10.1,leading=17,spaceAfter=2,textColor=INK,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='JP',fontSize=7.6,leading=11,spaceAfter=5,textColor=GRAY,wordWrap='CJK'),
 'h1':ParagraphStyle('h1',fontName='JPB',fontSize=22,leading=31,spaceAfter=15,textColor=INK,wordWrap='CJK',keepWithNext=True),
 'h2':ParagraphStyle('h2',fontName='JPB',fontSize=14,leading=22,spaceAfter=9,textColor=TEAL,wordWrap='CJK',keepWithNext=True),
 'h3':ParagraphStyle('h3',fontName='JPB',fontSize=10.3,leading=16,spaceBefore=8,spaceAfter=5,textColor=TEAL,wordWrap='CJK',keepWithNext=True),
}
def p(s,style='body'):return Paragraph(html.escape(str(s)).replace('\n','<br/>'),ST[style])
def parse():
 scenes=[]
 for file in ('scenes.txt','inserts.txt'):
  for row in (ROOT/file).read_text(encoding='utf8').splitlines():
   if row.startswith('## '):
    k,en,jp,loc=[x.strip() for x in row[3:].split('|')]; cur=dict(key=k,en=en,jp=jp,location=loc,blocks=[],questions=[]);scenes.append(cur)
   elif row.startswith('@ '):
    en,jp=map(str.strip,row[2:].split('|',1));cur['blocks'].append(dict(type='action',en=en,jp=jp))
   elif row.startswith('? '):
    q,a=map(str.strip,row[2:].split('|',1));cur['questions'].append([q,a])
   elif row and not row.startswith('!'):
    speaker,jp,en=map(str.strip,row.split('|',2));cur['blocks'].append(dict(type='dialogue',speaker=speaker,jp=jp,en=en))
 scenes.sort(key=lambda x:x['key'])
 for i,s in enumerate(scenes,1):
  s['id']=f'S{i:02}';n=0
  for b in s['blocks']:
   if b['type']=='dialogue': n+=1;b['id']=f'{s["id"]}-L{n:03}'
  s['kana']=sum(len(re.findall('[ぁ-ゖァ-ヺー]',b['jp'])) for b in s['blocks'] if b['type']=='dialogue')
  s['lines']=n
 return scenes
SCENES=parse();ALL=[b for s in SCENES for b in s['blocks'] if b['type']=='dialogue']
# Count small kana separately, not as a claimed mora count. Turn gaps are distinct from spoken time.
KANA_RATE=270
speech=sum(s['kana'] for s in SCENES)/KANA_RATE*60
turns=len(ALL)*.45
action_budget=3600-speech-turns
assert action_budget>0
total_action_words=sum(len(b['en'].split()) for s in SCENES for b in s['blocks'] if b['type']=='action')
cursor=0
for s in SCENES:
 s['start']=cursor
 for b in s['blocks']:
  b['start']=cursor
  dur=(len(re.findall('[ぁ-ゖァ-ヺー]',b['jp']))/KANA_RATE*60+.45) if b['type']=='dialogue' else action_budget*len(b['en'].split())/total_action_words
  b['duration_estimate']=dur;cursor+=dur;b['end']=cursor
 s['end']=cursor
assert abs(cursor-3600)<.01
def tc(sec):
 sec=round(sec);return f'{sec//3600:02}:{sec//60%60:02}:{sec%60:02}'

CAST=[
('あおい','Aoi, 22','Protagonist. Observant and funny when relaxed; control is her response to fear. Shoulder-length dark hair, cream blouse, blue apron after breakfast. Her knowledge of the first timeline is fallible.'),
('みさき','Misaki, 46','Aoi and Haru\'s mother. Runs the cafe; generous, private, sometimes overprotective. Short dark bob, oatmeal cardigan, cream apron; owns a red scarf.'),
('はる','Haru, 10','Aoi\'s brother. A playful amateur photographer with his own pride and boundaries. Green sweatshirt; blue toy camera. He notices physical details without becoming an implausible detective.'),
('りな','Rina, 25','Part-time cafe helper and loyal family friend. Cheerful but unwilling to accept mistreatment. Dark ponytail, mustard blouse; red scarf left on the communal rack.'),
('れん','Ren, 24','Bicycle courier. Careful about what he actually witnessed. Navy work jacket and canvas bag. Romance develops later through mutual respect, not instant devotion.'),
('ゆい','Yui, 22','Aoi\'s friend and a student. Sets boundaries and brings the notebook used to collect the cafe\'s history. Beige coat, red notebook.'),
('さとう','Sato, 38','Property-company representative. Applies time pressure and retreats when challenged. Gray suit, black folder. The opening does not establish who ordered any forgery.'),
('なお','Nao, 72','Regular customer; her ordinary repayment helps Aoi stop treating every envelope as proof.'),
('こえ','Voice','Caller claims to be Aoi from tomorrow. Similar timbre, mild phone filtering. Identity remains unconfirmed in this opening.'),
]
CHAPTERS=[
('The day returns','もどった ひ','00:00-00:50','Identity, possession, questions, location and basic action. Aoi returns, tests memories, repairs a friendship and revises a false accusation.'),
('The missing mother','いない おかあさん','00:50-01:40','Time, counters, polite tense, destinations and means. Opening-hour cliffhanger occurs ten minutes into this chapter. Aoi follows the umbrella trail but learns Misaki left voluntarily.'),
('The price of certainty','たしかさの ねだん','01:40-02:30','Adjectives, comparisons, wants, invitations and reasons. Aoi accuses the wrong business partner, loses access to a witness, and must make a public apology.'),
('What the hands remember','ての きおく','02:30-03:20','Plain forms, て forms, sequence, requests, permission and noun modification. Reconstructing a baking lesson reveals why two blue cups exist.'),
('A promise from tomorrow','あしたの やくそく','03:20-04:10','Experience, intention, opinions, quotation and explanatory forms. The caller knows only one possible future. Aoi chooses a plan that sacrifices a predicted advantage to protect Ren.'),
('Preparing to lose','まける じゅんび','04:10-05:00','Ability, changes, preparation, completion, aspect and simultaneous action. The team builds independent evidence; a test of the phone fails and removes magical certainty.'),
('If we trust each other','しんじるなら','05:00-05:50','Conditionals, advice, obligations and giving/receiving. Each character risks something different. Rina refuses an unsafe shortcut, and Yui finds the original contract history.'),
('Who made the decision','だれの きめた こと','05:50-06:40','Passive, causative, social register, inference and perspective. Formal meetings expose how responsibility was shifted. Misaki acknowledges a past choice that harmed her sister.'),
('Our first tomorrow','はじめての あした','06:40-07:30','N4 contrasts and cumulative retrieval. The forged transaction is blocked through witnesses and records; the sisters reconcile imperfectly. The phone goes quiet. Aoi accepts an uncertain future and a cafe shared with the people she once tried to control.'),
]

# Actual anchors for a subset of core grammar. This is deliberately not an automatic claim of full coverage.
RULES=[
('G002','じゃありません','The noun before じゃありません is denied: “is not.” ではありません is a more formal alternative. Do not use this ending directly with an い adjective.'),
('G003','でした','でした marks a past noun or な-adjective predicate. It is not added to a verb in place of ました.'),
('G005','ですか','か closes a polite question. A question can also be a short fragment in a familiar conversation.'),
('G006','の ','の links nouns: the first narrows or owns the second. Context can let the second noun be omitted.'),
('G007','も ','も adds “also/too.” It often replaces は, が or を rather than following them.'),
('G008','これ','これ stands by itself as “this thing.” この needs a following noun.'),
('G009','この','この modifies a following noun: “this ...”. It cannot normally stand alone.'),
('G010','どこ','どこ asks where. A location answer can be a short place expression plus です.'),
('G016','いくら','いくら asks a price; いくつ asks a count. Keep the two questions distinct.'),
('G017','なんじ','なんじ asks clock time. Counters have irregular readings such as じゅっぷん.'),
('G019','まで','まで marks an endpoint. Later, compare deadline までに.'),
('G022','あります','あります is existence for things. Use います for people and animals.'),
('G022','います','います can express animate existence. A verb in て + います is a different construction.'),
('G024','なか','A position word can follow noun + の: かばんの なか, “inside the bag.”'),
('G026','ました','ました is a polite past verb ending. It differs from the noun ending でした.'),
('G025','ません','ません is a polite negative verb ending. In an invitation such as ませんか it has a different conversational use.'),
('G027','を ','を, pronounced o, marks the object of an action here. Japanese word order differs from English.'),
('G029','へ ','へ, pronounced e as a particle, points toward a destination. に also marks many destinations.'),
('G033','いつも','いつも means “always”; ときどき means “sometimes.” These do not themselves conjugate.'),
('G059','から','Clause + から can state a reason. Place/time + から instead marks a starting point.'),
]
ledger=inventory();byid={x['id']:x for x in ledger}
for row in ledger:row['actual_anchors']=[]
for s in SCENES:
 candidates=[]
 for gid,needle,note in RULES:
  def appropriate(b):
   if b['type']!='dialogue' or needle not in b['jp']:return False
   t=b['jp'].replace(' ','')
   if gid=='G003' and 'ませんでした' in t:return False
   if gid=='G022' and needle=='います' and ('ています' in t or 'でいます' in t or 'ちがいます' in t or 'おもいます' in t or 'いいます' in t or 'かいます' in t):return False
   if gid=='G007' and ('でも ' in b['jp'] or 'だれも ' in b['jp'] or 'なにも ' in b['jp']):return False
   return True
  hit=next((b for b in s['blocks'] if appropriate(b)),None)
  if hit:
   byid[gid]['actual_anchors'].append(hit['id'])
   candidates.append((gid,hit,note))
 # Rotate focus to avoid three identical notes on all twenty-four scenes.
 index=SCENES.index(s); s['notes']=(candidates[index%len(candidates):]+candidates[:index%len(candidates)])[:3]
for row in ledger:
 if row['actual_anchors']:row['status']='anchor candidates in opening; contextual examples, not exhaustive proof'

story=[]
def add(t,style='body'):story.append(p(t,style))
def head(t,key,level=0,new=True):
 if new:story.append(PageBreak())
 q=p(t,'h1' if level==0 else 'h2');q._toc=(level,t,key);story.append(q)
def table(rows,widths):
 tab=Table([[p(c,'small') for c in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
 tab.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),PALE),('LINEBELOW',(0,0),(-1,0),.6,TEAL),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F7F8FA')]),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(tab);story.append(Spacer(1,10))

add('もういちど、あした','h1');add('Tomorrow, Once More','h1')
add('A rebirth mystery for learning Japanese','h2')
add('OPENING-HOUR SCREENPLAY + COMPLETE PROJECT PROMPT','h3')
add('English and kana-only Japanese | Original fictional drama | 24 scenes')
story.append(Spacer(1,32))
add('She remembers losing everything.\nThis time, knowing the future is not enough.','h2')
add('Aoi wakes up above her mother\'s cafe one year before its ruin. She has a whole blue cup, a second chance, and a dangerously incomplete memory. The first person she suspects may be the first person she needs.')
story.append(Spacer(1,24))
add('Production target: 60:00 for this opening; 7:30:00 for the full nine-chapter film. Timings are estimated, not a measured recording. The full-film plan and syllabus are included; only the opening is scripted here.','small')
add('Prepared 8 September 2026. Kana-only presentation supports spoken-language learning; it is not a complete JLPT reading preparation course.','small')
head('Contents / もくじ','contents')
toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc0',fontName='JPB',fontSize=10,leading=17,spaceBefore=7,textColor=INK),ParagraphStyle('toc1',fontName='JP',fontSize=8,leading=13,leftIndent=10,textColor=GRAY)];story.append(toc)
head('How to use this script / つかいかた','use')
add('Read or listen to the Japanese first, then check the English line immediately below it. Speaker names, Japanese dialogue, action summaries and prop text contain no kanji. Small spaces separate phrases for early reading. English translations preserve intent; fragments remain fragments when English allows it.')
add('The dramatic audio is Japanese only. English and the study notes are a parallel learner track. Stage directions are not narration unless a future production explicitly adapts them. No audio or video is embedded in this PDF.')
add('Learning from scratch without freezing the story','h2')
add('The first scenes emphasize identity and possession, then location, quantities, action and past events. Natural dialogue also includes some short expressions before their formal lesson. These are preview chunks, not assumed mastered grammar. The study notes give anchors; the later chapters teach the full system. For a strictly controlled reader, replace preview expressions during a separate graded adaptation.')
table([['Preview chunk','Meaning / use'],['おはよう / こんにちは / ありがとう','Good morning / hello / thank you. Fixed greetings.'],['だいじょうぶ？ / どうぞ / おねがいします','All right? / here you are or go ahead / please. Context supplies the rest.'],['わかりました / しりません','Understood / I do not know. Learn as useful chunks before the verb lesson.'],['なくさないで ください','Please do not lose it. Preview of a negative request.'],['かもしれません / でしょう','Might / probably or a confirmation-seeking guess. The later syllabus explains uncertainty.'],['きて くれて ありがとう','Thank you for coming. A favor-expression preview.'],['われた カップ / なまえの ない カード','The broken cup / the card with no name. Noun-modifier previews.'],['だと おもいました / みたい','I thought it was ... / looks like ... . Later lessons explain quotation and resemblance.']],[195,310])
add('Reading and pronunciation','h2')
add('As particles, は is pronounced wa, へ is e, and を is o. Long vowels, small っ and small ゃ / ゅ / ょ matter. Kana characters are not the same as morae. Katakana writes words such as カップ and コーヒー. Japanese does not need an explicit “I” in every sentence. Misaki sometimes uses mock-formal speech with her children; the script plays this as gentle humor.')
add('Register note: the opening deliberately uses more polite speech than an ordinary family might. Familiar short replies and sentence fragments keep it conversational. The later film moves into sustained casual speech only after plain forms are taught.')
add('Essential plot vocabulary','h2')
table([['Kana','English'],['ふうとう / ひきだし / かぎ','envelope / drawer / key'],['しょるい / サイン / こうしん','documents / signature / renewal'],['かんりがいしゃ / はいたつ','management company / delivery'],['しゃしん / うら / かど / きず','photograph / reverse side / corner / scratch'],['かくにん / ひみつ / やくそく','checking / secret / promise'],['スカーフ / かさ / あと','scarf / umbrella / mark or trace (context-dependent)']],[195,310])
head('Story and characters / ものがたりと ひと','bible')
for jp,en,desc in CAST:add(jp+' / '+en,'h3');add(desc)
add('Time-travel rules and continuity','h2')
add('The remembered timeline ends with the cafe\'s ruin and Misaki absent; the opening does not prove exactly how she died or disappeared. Present-day Aoi has incomplete memories. A prevented accident changes later interactions. The future caller\'s identity and date are claims. There is no established ability to reset at will. Evidence must work without accepting the supernatural premise.')
add('Production geography: stairs and back room behind the counter; shared coat rack at the side entrance; front door for customers; bank cash in one locked drawer; receipts in a different drawer. The counter mirror can show the side door after the menu stand moves.')
head('Full-film arc / ぜんたいの はなし','arc')
for i,(en,jp,time_,desc) in enumerate(CHAPTERS,1):add(f'{i:02} | {time_} | {en}','h2');add(jp,'jp');add(desc)
add('Ending reserved for the full script: the second cup belonged to Misaki\'s estranged sister. Her disappearance from the opening-day story made later manipulation possible. The phone\'s ultimate mechanism remains a controlled supernatural ambiguity, but the financial scheme must resolve through ordinary evidence. Do not use an unexplained recording as sufficient proof.')
head('Timing and scene map / じかんと シーン','timing')
add(f'This draft contains {len(ALL):,} spoken turns and {sum(s["kana"] for s in SCENES):,} kana characters in dialogue. The target read uses {KANA_RATE} kana characters per minute, plus a mean 0.45 seconds between turns. That gives {speech/60:.2f} minutes of speech and {turns/60:.2f} minutes of conversational spacing. The remaining {action_budget/60:.2f} minutes are budgeted to the written actions, entrances, visual clues and transitions.')
add('These estimates use character counts, not forced alignment or measured speech. They are a production allocation, not proof that a performance lasts exactly an hour. At 240-300 kana characters per minute, the same action and turn budget gives approximately '+f'{(sum(s["kana"] for s in SCENES)/240+(turns+action_budget)/60):.1f}-{(sum(s["kana"] for s in SCENES)/300+(turns+action_budget)/60):.1f} minutes. Record a table read, then retime the edit. English translations, grammar notes, quizzes and repeated practice are excluded.')
table([['Scene','Target time','Title']]+[[s['id'],tc(s['start'])+' - '+tc(s['end']),s['en']+' / '+s['jp']] for s in SCENES],[42,145,318])
head('Opening screenplay / はじめの ものがたり','screenplay')
add('Scene timings below are estimates. A Japanese line and its English translation stay together. “Study break” material follows each scene and is outside film runtime.')
for s in SCENES:
 head(s['id']+' | '+s['en']+' / '+s['jp'],s['id'],1)
 add(tc(s['start'])+' - '+tc(s['end'])+' | '+s['location'],'small')
 add(f'{s["lines"]} dialogue turns | {s["kana"]} kana characters | target {(s["end"]-s["start"])/60:.2f} minutes','small')
 for b in s['blocks']:
  if b['type']=='action':
   story.append(KeepTogether([p('ACTION / うごき','h3'),p(b['en'],'en'),p(b['jp'],'small')]))
  else:
   story.append(KeepTogether([p(b['id']+'  '+b['speaker'],'small'),p(b['jp'],'jp'),p(b['en'],'en')]))
 add('Study break / ふくしゅう - outside film runtime','h2')
 for gid,b,note in s['notes']:
  add(gid+' | '+b['id'],'h3');add(b['jp'],'jp');add(note)
 for i,(q,a) in enumerate(s['questions'],1):add(f'{i}. {q}');add('Answer: '+a,'en')
 first=s['notes'][0][1];add('Optional speaking task: cover the English for '+first['id']+', say the Japanese aloud, then change one noun, place or number while preserving the sentence structure. Check that the new meaning fits the grammar.','small')
head('Grammar syllabus / ぶんぽうの よてい','grammar')
add(f'{len(ledger)} editorial teaching units across N5, N4 and marked bridge material. A unit can group related variants, so this number is not comparable to a site that counts every conjugation separately. The supplementary sections add discourse expressions and variants often separated in study lists; assign them to their stated chapter alongside its main units. Official JLPT specifications do not provide an exhaustive published grammar list. Level placement varies among study references. The scope is broad beginner-to-elementary spoken grammar, not a guarantee of all future exam items.')
add('The full plan introduces a unit in its assigned chapter, reuses it in the next chapter and retrieves it in the final chapter. Chapter 9 items are reused in separate final-act scenes. These are planning slots, not completed-script coverage. Basic foundations recur throughout. Actual line anchors below are literal-match candidates and must be read in context; they do not prove that every use of a particle has been taught.')
for group,ch,_ in GROUPS:
 add(f'Chapter {ch} | '+group,'h2')
 for row in [r for r in ledger if r['group']==group]:
  add(row['id']+' | '+row['pattern'],'h3');add(row['explanation'])
  anchors=row['actual_anchors'][:4]
  add(('Opening anchor candidates: '+', '.join(anchors)) if anchors else 'Formal teaching planned for the full-film chapter; no audited opening anchor assigned.','small')
head('Clue ledger / ヒントの ノート','clues')
table([['Clue','Known by the opening\'s end','Not yet established'],['Blue cup','The present cup is intact; the old photo shows two.','Which cup appears in the remembered loss.'],['Red scarves','Rina and Misaki own matching scarves. Rina leaves hers accessible.','Identity of the remembered scarf wearer.'],['White envelopes','Bank money is intact; other ordinary envelopes exist.','Contents/direction of the photographed exchange.'],['Camera clock','Seven minutes fast; original images retained.','Hidden face or unreadable signature.'],['Sato\'s documents','Misaki denies a signature; she declines to sign the replacement.','Who made the mark and who authorized it.'],['Future call','Caller knows the cup and claims tomorrow\'s date.','Identity, mechanism and truth of the claim.']],[98,200,207])
head('Reusable full-project prompt / つぎの プロンプト','prompt')
for block in PROMPT.strip().split('\n\n'):add(block)
head('Production / せいさく','sources')
add('This PDF is an original screenplay drafted here, not a MiniMax text-generation result. The requested H3 model is for video generation. The separate Modal benchmark uses available open weights and a Turbo adapter; any actual generated media and measured cost belong in the accompanying run report. Do not treat a model deployment as a completed film.')
add('For generated shots: keep a reference sheet for each adult actor, use the same wardrobe and props, split dialogue into short shots, verify every spoken Japanese word, then add kana and English subtitles in the editor. Do not rely on a video model to draw correct captions. Re-record or correct garbled speech before using it to teach.')
add('Research references, accessed 8 September 2026','h2')
for title,url in [
 ('Official JLPT FAQ: no published exhaustive test-content inventory','https://www.jlpt.jp/e/faq/'),
 ('N5 comparison list; original examples not reproduced','https://jlptsensei.com/jlpt-n5-grammar-list/'),
 ('N4 comparison list; original examples not reproduced','https://jlptsensei.com/jlpt-n4-grammar-list/'),
 ('MiniMax hosted model pricing','https://platform.minimax.io/docs/guides/pricing-paygo'),
 ('Official H3 model card and weights','https://huggingface.co/MiniMaxAI/MiniMax-H3'),
 ('H3 Turbo Space implementation','https://huggingface.co/spaces/MiniMaxAI/MiniMax-H3-Turbo-Lora'),
 ('Modal resource pricing','https://modal.com/pricing')]:
 add(title,'h3');add(url,'small')
add('Quality status: automated no-kanji and bilingual-pair checks; editorial review of story continuity and representative grammar; PDF page rendering and layout inspection. No native-speaker review or measured full-hour performance has been performed. Further learner testing should specifically review the preview chunks and naturalness of the deliberately polite family exchanges.','small')

class Doc(BaseDocTemplate):
 def afterFlowable(self,flow):
  if hasattr(flow,'_toc'):
   level,title,key=flow._toc;self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,level=level,closed=False);self.notify('TOCEntry',(level,title,self.page,key))
def page(c,d):
 c.setStrokeColor(TEAL);c.setLineWidth(.5);c.line(45,800,550,800)
 c.setFont('JP',7);c.setFillColor(GRAY);c.drawString(45,812,'TOMORROW, ONCE MORE | もういちど、あした');c.drawRightString(550,27,str(d.page))
 c.drawString(45,27,'Opening-hour draft | English + kana | Estimated runtime')
doc=Doc(str(OUT),pagesize=(595.28,841.89),leftMargin=45,rightMargin=45,topMargin=52,bottomMargin=45,title='Tomorrow, Once More - Opening Hour',author='Original screenplay prepared with Codex')
doc.addPageTemplates(PageTemplate(id='main',frames=[Frame(45,45,505.28,745,id='main')],onPage=page))
doc.multiBuild(story)
# Only Japanese fields are checked, and then the whole original manuscript is checked as a second guard.
for s in SCENES:
 for b in s['blocks']:
  assert not re.search('[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]',b['jp']),b
  if b['type']=='dialogue':assert b['en'] and b['speaker']
(ROOT/'master_prompt.txt').write_text(PROMPT,encoding='utf8')
(ROOT/'grammar_inventory.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf8')
# Strip internal note objects from the editable screenplay export.
export=[{k:v for k,v in s.items() if k!='notes'} for s in SCENES]
(ROOT/'screenplay.json').write_text(json.dumps(export,ensure_ascii=False,indent=2),encoding='utf8')
(ROOT/'timing_report.json').write_text(json.dumps(dict(scenes=len(SCENES),dialogue_lines=len(ALL),kana_characters=sum(s['kana'] for s in SCENES),kana_rate=KANA_RATE,speech_seconds=speech,turn_spacing_seconds=turns,action_seconds=action_budget,total_estimated_seconds=cursor,measured=False),indent=2),encoding='utf8')
print(OUT)
print(json.dumps(dict(scenes=len(SCENES),lines=len(ALL),kana=sum(s['kana'] for s in SCENES),estimated_seconds=cursor)))
