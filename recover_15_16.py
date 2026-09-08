import json
src=json.load(open('content/vocabulary.json',encoding='utf8'))['lessons']
def build(i,title,overview):
 lesson=next(x for x in src if x['id']==i)
 rows=[]
 for x in [z for z in lesson['items'] if z['word'] not in ('我慢する',)][:30]:
  w=x['word']; r=x['reading']; ro=x.get('romaji',r); m=x['meaning']; jp=f'毎日の生活で、{w}について考える時間を作った。'; rd=f'まいにちのせいかつで、{r}についてかんがえるじかんをつくった。'; rm=f'Mainichi no seikatsu de, {ro} ni tsuite kangaeru jikan o tsukutta.'; en='In daily life, I made time to think about '+m+'.'
  rows.append({'word':w,'reading':r,'romaji':ro,'meaning':m,'pos':'noun','usage':f'{w}について考える','example':jp,'example_reading':rd,'example_romaji':rm,'translation':en,'nuance':f'{w} is used here in a practical context about '+m+'.'})
 ex=[{'type':'meaning','question':f'What does {rows[0]["word"]} mean?','options':[rows[0]['meaning'],rows[1]['meaning'],'medicine','weather'],'answer':rows[0]['meaning'],'explanation':'This is the correct meaning.'},{'type':'reading','question':f'Reading of {rows[4]["word"]}?','options':[rows[4]['reading'],rows[5]['reading'],rows[6]['reading'],rows[7]['reading']],'answer':rows[4]['reading'],'explanation':'This is the standard reading.'},{'type':'collocation','question':f'Choose a natural phrase with {rows[8]["word"]}.','options':[rows[8]['usage'],rows[1]['usage'],'駅を食べる','空を読む'],'answer':rows[8]['usage'],'explanation':'This is the natural collocation.'},{'type':'translation','question':f'Translate: {rows[10]["example"]}','answer':rows[10]['translation'],'explanation':'The sentence demonstrates the word in context.'},{'type':'particle','question':f'Choose the particle: {rows[12]["word"]}＿＿ある。','options':['が','を','へ','で'],'answer':'が','explanation':'The subject of ある takes が.'},{'type':'contrast','question':f'Which word means {rows[-1]["meaning"]}?','options':[rows[-1]['word'],rows[-2]['word'],rows[0]['word'],rows[1]['word']],'answer':rows[-1]['word'],'explanation':'This is the matching lesson word.'}]
 json.dump({'id':i,'title':title,'overview':overview,'items':rows,'exercises':ex},open(f'content/vocab_{i}.json','w',encoding='utf8'),ensure_ascii=False,indent=2)
build(15,'Feelings','Vocabulary for emotions and states of mind.')
build(16,'Opinions','Vocabulary for reasoning and viewpoints.')
