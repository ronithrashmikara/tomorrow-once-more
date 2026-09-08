"""Run only an explicitly selected shot list, with one GPU and a hard time/budget bound."""
from pathlib import Path
import json,time,modal
from modal_h3 import gpu_image,cache,HERE
app=modal.App('aoi-h3-turbo-production')
image=gpu_image.add_local_python_source('h3_runtime')

@app.function(image=image,volumes={'/cache':cache},gpu='B200',cpu=(4,4),memory=(196608,196608),
    timeout=3300,startup_timeout=120,max_containers=1,min_containers=0,scaledown_window=2,
    retries=0,single_use_containers=True)
def render(jobs,run_id):
    import torch
    from diffusers.utils.export_utils import encode_video
    from h3_runtime import load_pipeline
    started=time.monotonic(); pipe=load_pipeline('fl2va')
    folder=Path('/cache/production')/run_id; folder.mkdir(parents=True,exist_ok=True)
    report={'run_id':run_id,'load_seconds':time.monotonic()-started,'shots':[],'complete':False}
    last_frame=None; previous_scene=None
    for index,job in enumerate(jobs):
        # Leave ten minutes for a slow final shot, encoding and committing. No auto-retries.
        if time.monotonic()-started>2600:
            report['stop_reason']='time budget'; break
        kwargs={}
        prompt=job['prompt']
        if last_frame is not None and previous_scene==job['scene_id']:
            kwargs['image']=last_frame
            prompt='For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.\n\n'+prompt
        tick=time.monotonic()
        with torch.inference_mode():
            state=pipe(prompt=prompt,height=544,width=960,num_frames=job['frames'],
                num_inference_steps=5,generator=torch.Generator('cpu').manual_seed(job['seed']),**kwargs)
        frames=state.get('videos')[0]; last_frame=frames[-1]; previous_scene=job['scene_id']
        path=folder/(job['shot_id']+'.mp4')
        encode_video(frames,fps=24,output_path=str(path),audio=state.get('audio')[0].cpu(),audio_sample_rate=state.get('sampling_rate'))
        row={'shot_id':job['shot_id'],'seconds':len(frames)/24,'generation_seconds':time.monotonic()-tick,'quality_review':'pending'}
        report['shots'].append(row); report['elapsed_seconds']=time.monotonic()-started
        (folder/'report.json').write_text(json.dumps(report,indent=2)); cache.commit()
        print(json.dumps(row),flush=True)
        del state,frames
    else: report['complete']=True
    report['elapsed_seconds']=time.monotonic()-started
    (folder/'report.json').write_text(json.dumps(report,indent=2)); cache.commit()
    return report

@app.local_entrypoint()
def main(jobs_file:str,run_id:str):
    jobs=json.loads(Path(jobs_file).read_text(encoding='utf8'))
    if not 1<=len(jobs)<=50: raise ValueError('Expected 1–50 selected shots')
    if not run_id.replace('-','').isalnum(): raise ValueError('Unsafe run identifier')
    for j in jobs:
        if not 124<=j['frames']<=345 or (j['frames']-5)%17: raise ValueError('Unsupported frame count')
        if not j['shot_id'].replace('-','').isalnum(): raise ValueError('Unsafe shot identifier')
    ledger_path=HERE/'budget_15.json'; ledger=json.loads(ledger_path.read_text())
    reservation=8.0 # B200 + four CPUs + 192 GiB RAM, 3300s + 120s startup + margin.
    if ledger['reserved_usd']+reservation>ledger['limit_usd']-ledger['reserve_usd']:
        raise RuntimeError('Budget gate: insufficient unreserved budget')
    ledger['reserved_usd']+=reservation
    ledger['attempts'].append({'kind':'production','run_id':run_id,'reserved_usd':reservation,'started_epoch':time.time()})
    ledger_path.write_text(json.dumps(ledger,indent=2))
    report=render.remote(jobs,run_id)
    out=HERE/'production'/run_id; out.mkdir(parents=True,exist_ok=True)
    (out/'report.json').write_text(json.dumps(report,indent=2))
    for row in report['shots']:
        with (out/(row['shot_id']+'.mp4')).open('wb') as f:
            for chunk in cache.read_file('production/'+run_id+'/'+row['shot_id']+'.mp4'): f.write(chunk)
    print(json.dumps(report,indent=2))
