import json
p='content/vocabulary.json';d=json.load(open(p,encoding='utf8'))
qs=[('reading','Choose the reading for {w}.',['{r}','まど','しょくじ','ねだん']),('context','Which word fits this sentence: {e}?',['{w}','目覚まし','天気','宿題']),('particle','Which particle belongs after {w}?',['を','が','へ','で']),('translation','Which translation matches the example?',['{t}','It is raining today.','I studied yesterday.','Please wait here.']),('contrast','Which word is the opposite or counterpart of {w}?',['{w}','壊れる','新鮮','安い']),('usage','Which collocation is natural with {w}?',['{w}を確認する','{w}を泳ぐ','{w}が食べる','{w}へ眠る'])]
for l in d['lessons'][1:4]:
 for i,e in enumerate(l['exercises']):
  it=l['items'][i]; typ,q,opts=qs[i]; opts=[x.format(w=it['word'],r=it['reading'],e=it['example'],t=it['translation']) for x in opts]; e.update(type=typ,question=q.format(w=it['word'],r=it['reading'],e=it['example'],t=it['translation']),options=opts,answer=opts[0],explanation='The first option is supported by the example and dictionary usage.')
json.dump(d,open(p,'w',encoding='utf8'),ensure_ascii=False,indent=2)