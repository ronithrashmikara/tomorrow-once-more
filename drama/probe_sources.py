import urllib.request,urllib.error,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).parent/'research'; ROOT.mkdir(exist_ok=True)
URLS={
 'diffusers_commit':'https://api.github.com/repos/huggingface/diffusers/commits/665f578278365ea4a3318cb8c9b66ce6c01204b9',
 'diffusers_pr':'https://api.github.com/repos/huggingface/diffusers/pulls/14371',
 'model_meta':'https://huggingface.co/api/models/MiniMaxAI/MiniMax-H3',
 'turbo_meta':'https://huggingface.co/api/models/lightx2v/Minimax-h3-Turbo',
 'pricing':'https://modal.com/pricing',
 'space_app':'https://huggingface.co/spaces/MiniMaxAI/MiniMax-H3-Turbo-Lora/raw/main/app.py',
 'space_requirements':'https://huggingface.co/spaces/MiniMaxAI/MiniMax-H3-Turbo-Lora/raw/main/requirements.txt',
 'diffusers_pipeline':'https://raw.githubusercontent.com/huggingface/diffusers/665f578278365ea4a3318cb8c9b66ce6c01204b9/src/diffusers/modular_pipelines/minimax_h3/modular_pipeline.py',
}
def get(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'JapaneseDramaPreflight/1.0'})
  with urllib.request.urlopen(req,timeout=25) as r: data=r.read(); code=r.status
  (ROOT/(name+'.txt')).write_bytes(data)
  return {'name':name,'url':url,'status':code,'bytes':len(data)}
 except Exception as e: return {'name':name,'url':url,'error':str(e)}
result=list(ThreadPoolExecutor(max_workers=5).map(get,URLS.items()))
(ROOT/'preflight.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
