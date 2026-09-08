from pathlib import Path
import json
F=Path(__file__).parent/'content/final'
def read(n):return json.loads((F/f'{n}.json').read_text(encoding='utf-8'))
def save(n,d):(F/f'{n}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
V=read('vocabulary');seen=set()
for i,title in [(7,'Directions and transport'),(8,'Services and procedures'),(9,'School life'),(10,'Learning and study')]:
 d=json.loads((F.parent/f'vocab_{i:02d}.json').read_text(encoding='utf-8-sig'))
 d['title']=title;d['overview']='Study each word through its Japanese example and English translation.'
 for x in d['items']:
  x['usage']=x['example'];x['example_romaji']='';x['nuance']='Read the example as a complete phrase, then recall the word from the English translation.'
 d['exercises']=[dict(question='Translate: '+x['example'],answer=x['translation'],explanation=x['reading']+' — '+x['meaning']) for x in d['items'][:3]]
 V['lessons'][i-1]=d
for l in V['lessons']:
 out=[]
 for x in l['items']:
  w=x['word'];k=w[:-2] if w.endswith('する') else w
  if k not in seen:out.append(x);seen.add(k)
 l['items']=out
save('vocabulary',V)
K=read('kanji')
for i,l in enumerate(K['lessons'],1):
 l['title']=f'Kanji set {i:02d}'
 a,b,c=l['items'][:3]
 l['exercises']=[dict(question='Give the meaning of '+a['kanji']+'.',answer=a['meaning'],explanation=a['mnemonic']),dict(question='Read this word: '+b['words'][0]['word'],answer=b['words'][0]['reading'],explanation=b['words'][0]['meaning']),dict(question='Translate: '+c['example'],answer=c['translation'],explanation=c['example_reading'])]
save('kanji',K)
G=read('grammar')
fix={'ば':'Godan: final u-sound changes to e-sound + ば. Ichidan: remove る + れば. する→すれば; 来る→くれば. い-adjective: remove い + ければ. Noun/な-adjective: なら(ば). Negative: ない→なければ.','たら':'Plain past form + ら: Vた/だ + ら; い-adjective かったら; noun/な-adjective だったら; negative なかったら.','と':'Verb/い-adjective plain nonpast + と; noun/な-adjective + だと.','までに':'Time noun or dictionary-form verb + までに.','うちに':'Verb dictionary/ている/ない, い-adjective, な-adjective + な, or noun + の, followed by うちに.','間に':'Verb plain/ている, い-adjective, な-adjective + な, or noun + の, followed by 間に.'}
for p in ['はずだ','はずがない','ようだ','おかげで','せいで','ために']:
 fix[p]='Verb/い-adjective plain form; noun + の; な-adjective + な; followed by '+p+'.'
for p in ['みたいだ','らしい','かもしれない','でしょう','に違いない']:
 fix[p]='Verb/い-adjective plain form, or noun/な-adjective stem without だ, followed by '+p+'.'
for l in G['lessons']:
 for x in l['items']:
  if x['pattern'] in fix:x['formation']=fix[x['pattern']]
  # Translation checks avoid ambiguous or context-free multiple-choice stems.
  e=x['examples'][0]
  x['question']=dict(question='Translate this sentence and explain the role of '+x['pattern']+': '+e['jp'],answer=e['en'],explanation=x['meaning']+' '+x['nuance'])
save('grammar',G)
print({n:sum(len(l['items']) for l in d['lessons']) for n,d in [('vocabulary',V),('kanji',K),('grammar',G)]})
