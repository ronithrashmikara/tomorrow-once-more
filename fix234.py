import json
from pykakasi import kakasi
k=kakasi()
d=json.load(open('content/vocabulary.json',encoding='utf8'))
for l in d['lessons'][1:4]:
 for it in l['items']:
  a=k.convert(it['example']); it['example_reading']=''.join(z['hira'] for z in a); it['example_romaji']=' '.join(z['hepburn'] for z in a)
json.dump(d,open('content/vocabulary.json','w',encoding='utf8'),ensure_ascii=False,indent=2)