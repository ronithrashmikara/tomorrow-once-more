from pathlib import Path
import json,time,shutil
from gradio_client import Client
root=Path(__file__).parent/'benchmark';root.mkdir(exist_ok=True)
prompt=('Realistic Japanese live-action drama. A fictional Japanese woman aged 22, '
 'shoulder-length dark hair, cream cotton pajamas, sits in a modest bedroom in morning light '
 'holding an intact blue ceramic cup. Medium close-up. She looks toward the door with tears of '
 'recognition and says softly exactly <d>[Japanese] おかあさん？</d> Then she closes her mouth. '
 'Gentle room tone, distant kettle, no music, no captions, no text, steady camera, no cuts.')
t=time.monotonic()
try:
 c=Client('MiniMaxAI/MiniMax-H3-Turbo-Lora',download_files=str(root))
 result=c.predict(prompt,None,None,'960x544 · 16:9 fast',5,6,4112,False,'larry',api_name='/output_video')
 report={'route':'public Hugging Face H3 Turbo Space','result':result,'elapsed_seconds':time.monotonic()-t,'quality_review':'pending'}
 (root/'hf_sample_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
except Exception as e:
 report={'route':'public Hugging Face H3 Turbo Space','error':str(e),'elapsed_seconds':time.monotonic()-t,'video_produced':False}
 (root/'hf_sample_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
