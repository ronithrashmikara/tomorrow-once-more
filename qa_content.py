import json,re,collections
from pathlib import Path
root=Path(__file__).parent
report={}
for name,key,ex in [('vocabulary','word','example'),('kanji','kanji','example'),('grammar','pattern','examples')]:
    d=json.loads((root/'content'/f'{name}.json').read_text(encoding='utf-8-sig')); items=[(l['id'],x) for l in d['lessons'] for x in l['items']]
    counts=collections.Counter(x[key] for l,x in items)
    suspect=[]
    for l,x in items:
        s=json.dumps(x,ensure_ascii=False)
        reasons=[]
        for pat in ['について確認しました','The sentence uses','この漢字は大切です','A useful compound built','旅行の予定を説明する文で','a different meaning','the expression shown in the context','Context decides whether','Use this pattern when the surrounding']:
            if pat in s:reasons.append('placeholder: '+pat)
        for f in ['reading','example_reading']:
            if name=='grammar':continue
            if f in x and re.search('[一-龯]',x[f]):reasons.append('kanji in '+f)
        for f in ['romaji','example_romaji']:
            if f in x and re.search('[ぁ-ヿ一-龯]',str(x[f])):reasons.append('Japanese in '+f)
        if name=='grammar':
            for i,e in enumerate(x['examples']):
                if re.search('[一-龯]',e['reading']):reasons.append(f'kanji in reading ex{i+1}')
                if re.search('[ぁ-ヿ一-龯]',e['romaji']):reasons.append(f'Japanese in romaji ex{i+1}')
        if reasons:suspect.append({'lesson':l,'item':x[key],'issues':reasons})
    report[name]={'count':len(items),'duplicates':[x for x,n in counts.items() if n>1],'suspect_count':len(suspect),'suspects':suspect}
    print(name,len(items),'suspect',len(suspect),'duplicates',report[name]['duplicates'])
(root/'tmp/pdfs/content_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
