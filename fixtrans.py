import json
p='content/vocabulary.json';d=json.load(open(p,encoding='utf8'))
for li in range(8,12):
 l=d['lessons'][li]
 for i,it in enumerate(l['items']):
  m=it['meaning'];
  if li==8: ts=[f'I checked {m} in class.',f'I studied {m} in the lecture.',f'I am studying with {m}.',f'I am preparing for {m}.']
  elif li==9: ts=[f'I practice {m} every day.',f'I looked up {m} in a dictionary.',f'I wrote about {m} in my notes.',f'I asked my teacher about {m}.']
  elif li==10: ts=[f'I handle {m} at work.',f'I discussed {m} at the company.',f'My supervisor entrusted me with {m}.',f'I want to gain experience with {m} next month.']
  else: ts=[f'I confirmed {m} at the meeting.',f'I summarized {m} in the materials.',f'I consulted the customer about {m}.',f'Our team is advancing {m}.']
  it['translation']=ts[i%4]
json.dump(d,open(p,'w',encoding='utf8'),ensure_ascii=False,indent=2)