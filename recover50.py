import json, shlex
p='C:/Users/Ronit/Downloads/N3/content/kanji.json'
with open(p,encoding='utf-8-sig') as f: data=json.load(f)
recs={}
for line in open('C:/Users/Ronit/Downloads/N3/rewrite50.ps1',encoding='utf-8'):
    if not line.startswith('Add '): continue
    try: a=shlex.split(line[4:].strip(),posix=True)
    except ValueError: continue
    if len(a)<11: continue
    k,m,on,kun,rom=a[:5]; w1,rd1,mw1,w2,rd2,mw2=a[5:11]
    tail=a[11:]
    ex=tail[0] if len(tail)>0 else f'{w1}を覚えました。'
    er=tail[1] if len(tail)>1 else f'{rd1}をおぼえました。'
    tr=tail[2] if len(tail)>2 else f'I learned the word {w1}.'
    co=tail[3] if len(tail)>3 else f'Visual parts: connect the written components with the meaning {m}.'
    mn=tail[4] if len(tail)>4 else f'Imagine a scene linked to {m}.'
    recs[k]={'meaning':m,'onyomi':on,'kunyomi':kun or 'No common independent kun reading taught here','romaji':rom,'words':[{'word':w1,'reading':rd1,'meaning':mw1},{'word':w2,'reading':rd2,'meaning':mw2}],'example':ex,'example_reading':er,'translation':tr,'components':co,'mnemonic':mn,'warning':'Learn each reading through the listed words; compounds may voice or change readings.'}
for lesson in data['lessons']:
    for item in lesson['items']:
        if item['kanji'] in recs: item.update(recs[item['kanji']])
if len(recs)!=50: raise SystemExit(f'parsed {len(recs)} records')
with open(p,'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)
print('rewrote',len(recs))
