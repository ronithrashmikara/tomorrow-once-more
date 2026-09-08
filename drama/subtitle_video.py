"""Add kana/English subtitles to a speech-screened clip, preserving its audio."""
from pathlib import Path
import argparse,json,subprocess

def stamp(value):
    ticks=round(value*100); h,ticks=divmod(ticks,360000); m,ticks=divmod(ticks,6000); s,c=divmod(ticks,100)
    return f'{h}:{m:02}:{s:02}.{c:02}'

def safe(text):
    return text.replace('\\','').replace('{','').replace('}','').replace('\n',' ')

def subtitle(video,jp,en):
    qa=json.loads(video.with_suffix('.qa.json').read_text(encoding='utf8'))
    if qa.get('kana_similarity',0)<0.85:
        raise ValueError('Speech screening did not pass; review or regenerate before subtitling.')
    rows=[x for x in qa['segments'] if x['text'].strip()]
    if not rows: raise ValueError('No spoken segment detected')
    start=max(0,min(x['start'] for x in rows)-0.12)
    end=min(qa['duration'],max(x['end'] for x in rows)+0.3)
    ass=video.with_suffix('.ass')
    ass.write_text('[Script Info]\nScriptType: v4.00+\nPlayResX: 960\nPlayResY: 720\nWrapStyle: 0\n'
      '[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
      'Style: JP,Meiryo,32,&H00FFFFFF,&H00FFFFFF,&H0011100E,&H0011100E,0,0,0,0,100,100,0,0,1,1,0,2,35,35,82,1\n'
      'Style: EN,Meiryo,24,&H00D5D9DF,&H00FFFFFF,&H0011100E,&H0011100E,0,0,0,0,100,100,0,0,1,1,0,2,35,35,35,1\n'
      '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
      f'Dialogue: 0,{stamp(start)},{stamp(end)},JP,,0,0,0,,{safe(jp)}\n'
      f'Dialogue: 0,{stamp(start)},{stamp(end)},EN,,0,0,0,,{safe(en)}\n',encoding='utf-8-sig')
    output=video.with_name(video.stem+'_subtitled.mp4')
    # Run in the media directory so libavfilter needs no Windows drive escaping.
    subprocess.run(['ffmpeg','-y','-i',video.name,'-vf',f'pad=960:720:0:0:color=0x0e1011,ass={ass.name}',
        '-c:v','libx264','-preset','fast','-crf','19','-c:a','copy','-movflags','+faststart',output.name],cwd=video.parent,check=True,capture_output=True)
    return output

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('video',type=Path);ap.add_argument('--jp',required=True);ap.add_argument('--en',required=True)
    a=ap.parse_args(); print(subtitle(a.video.resolve(),a.jp,a.en))
