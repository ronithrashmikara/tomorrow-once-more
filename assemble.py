from pathlib import Path
import json,re,collections
ROOT=Path(__file__).parent; C=ROOT/'content'; F=C/'final';F.mkdir(exist_ok=True)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,d):(F/f'{n}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
V=load(C/'vocabulary.json');K=load(C/'kanji.json');G=load(C/'grammar.json')
bad=['この漢字は大切です','A useful compound built','The sentence uses','The sentence means','旅行の予定を説明する文で','を実際の場面で使う','をノートに整理した','Context decides whether','Use this pattern when the surrounding']
missing=[]
for i in range(1,33):
 p=C/f'vocab_{i:02d}.json'
 if not p.exists():missing.append(p.name);continue
 d=load(p)
 if any(s in json.dumps(d,ensure_ascii=False) for s in bad):missing.append(p.name+' has placeholder');continue
 V['lessons'][i-1]=d
if missing:print('VOCAB PENDING:',', '.join(missing))
valid_k_files=['kanji_051_100.json','kanji_101_150.json','kanji_151_175.json','kanji_176_225.json','kanji_226_275.json','kanji_276_325.json','kanji_326_370.json']
ki={x['kanji']:x for l in K['lessons'] for x in l['items']}
for name in valid_k_files:
 p=C/name
 if not p.exists():print('KANJI PENDING:',name);continue
 for x in load(p):
  assert not any(s in json.dumps(x,ensure_ascii=False) for s in bad),(name,x['kanji'])
  ki[x['kanji']]=x
for l in K['lessons']:l['items']=[ki[x['kanji']]for x in l['items']]
gpatch={}
for name in ['grammar_repair_01.json','grammar_final_repairs.json']:
 for x in load(C/name):gpatch[x['pattern']]=x
# Duplicated attributive forms are taught with their base construction;
# adjacent-level extras that did not contribute to the N3 route are omitted.
omit={'に関する','による','たまま','における','つつ','ように努める','しかしながら','させられる'}
for l in G['lessons']:
 l['items']=[gpatch.get(x['pattern'],x)for x in l['items']if x['pattern']not in omit]
for x in load(C/'grammar_extra.json'):
 i=x.pop('lesson');G['lessons'][i-1]['items'].append(x)
for l in G['lessons']:
 a,b=l['items'][:2]
 l['exercises']=[dict(type='translation',question='Translate naturally: '+a['examples'][1]['jp'],answer=a['examples'][1]['en'],explanation=a['nuance']),dict(type='production',question='Express this in Japanese using '+b['pattern']+': '+b['examples'][2]['en'],answer=b['examples'][2]['jp'],explanation='Other natural wording is acceptable if it preserves the relationship. '+b['formation']),dict(type='comparison',question='Explain the usage distinction between '+a['pattern']+' and '+b['pattern']+'.',answer=a['pattern']+': '+a['meaning']+'. '+b['pattern']+': '+b['meaning']+'.',explanation=a['comparison']+' '+b['comparison'])]
for name,d in [('vocabulary',V),('kanji',K),('grammar',G)]:
 problems=[]
 for l in d['lessons']:
  for x in l['items']:
   s=json.dumps(x,ensure_ascii=False)
   if any(t in s for t in bad):problems.append((l['id'],x.get('word',x.get('kanji',x.get('pattern')))))
 print(name,'count',sum(len(l['items'])for l in d['lessons']),'bad',len(problems),str(problems[:8]))
 save(name,d)
for name in ['readings','reviews']:save(name,load(C/f'{name}.json'))
status=dict(vocabulary_missing=missing,kanji_files_missing=[n for n in valid_k_files if not(C/n).exists()])
(ROOT/'tmp/pdfs/assembly_status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
