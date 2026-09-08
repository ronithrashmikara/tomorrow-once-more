from pathlib import Path
import json,zipfile,hashlib
ROOT=Path(__file__).parent
scenes=json.loads((ROOT/'screenplay.json').read_text(encoding='utf8'))
shots=[]
for s in scenes:
    group=[];duration=0
    def emit():
        global group,duration
        if not group:return
        shots.append({'shot_id':f'{s["id"]}-SH{sum(x["scene_id"]==s["id"] for x in shots)+1:02}',
            'scene_id':s['id'],'scene_title_en':s['en'],'scene_title_kana':s['jp'],
            'target_start_seconds':group[0]['start'],'target_end_seconds':group[-1]['end'],
            'duration_is_estimate':True,'generation_status':'not_generated',
            'location':s['location'],'content':group,
            'production_note':'Choose camera coverage and character references before generation. Re-time to verified Japanese audio. Subtitles are added in editing, never painted by the video model.'})
        group=[];duration=0
    for b in s['blocks']:
        if b['type']=='action':
            emit();group=[b];duration=b['duration_estimate'];emit()
        else:
            if duration+b['duration_estimate']>11 and group:emit()
            group.append(b);duration+=b['duration_estimate']
    emit()
(ROOT/'shot_manifest.json').write_text(json.dumps(shots,ensure_ascii=False,indent=2),encoding='utf8')
md=['# Tomorrow, Once More / もういちど、あした','', 'Opening-hour screenplay. Timing is estimated; Japanese speech only.','']
for s in scenes:
    md+=['## '+s['id']+' '+s['en']+' / '+s['jp'],'',s['location'],'']
    for b in s['blocks']:
        if b['type']=='action':md+=['*'+b['en']+'*','',b['jp'],'']
        else:md+=['**'+b['id']+' '+b['speaker']+'**','',b['jp'],'',b['en'],'']
(ROOT/'screenplay.md').write_text('\n'.join(md),encoding='utf8')
files=['master_prompt.txt','screenplay.md','screenplay.json','grammar_inventory.json','timing_report.json','shot_manifest.json','modal_h3.py','hf_sample.py','RUN_REPORT.md']
dest=ROOT.parent/'output/Tomorrow_Once_More_Project.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for name in files:
        data=(ROOT/name).read_bytes()
        assert b'ak-jq' not in data and b'as-Jq' not in data,'Credential in output'
        z.writestr(name,data)
    z.write(ROOT.parent/'output/pdf/Tomorrow_Once_More_Opening_Hour.pdf','Tomorrow_Once_More_Opening_Hour.pdf')
print('Shots:',len(shots),'Package:',dest)
