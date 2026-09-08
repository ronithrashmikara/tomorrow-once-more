import json,re
from pathlib import Path
for f in Path('content').glob('vocab_*.json'):
 try:
  d=json.loads(f.read_text(encoding='utf-8'));print(f.name,len(d['items']),sum('について確認しました' not in x['example'] for x in d['items']))
 except Exception as e: print(f.name,e)
for f in Path('content').glob('kanji_*_*.json'):
 try:
  d=json.loads(f.read_text(encoding='utf-8'));print(f.name,len(d),sum(x['example']!='この漢字は大切です。' and 'A useful compound' not in json.dumps(x,ensure_ascii=False) for x in d))
 except Exception as e: print(f.name,e)
