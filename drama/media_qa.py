"""Inspect locally generated media and transcribe Japanese without using cloud credits."""
from pathlib import Path
import argparse,json,subprocess,re
from faster_whisper import WhisperModel
from pykakasi import kakasi
from difflib import SequenceMatcher

def kana(text):
    text=''.join(x['hira'] for x in kakasi().convert(text))
    return re.sub('[^ぁ-ゖー]','',text)

def inspect(path,expected=None,model=None):
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],text=True))
    model=model or WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=8,download_root=str(Path(__file__).parent/'asr_models'))
    segments,info=model.transcribe(str(path),language='ja',beam_size=5,word_timestamps=True,condition_on_previous_text=False,vad_filter=False)
    rows=[{'start':s.start,'end':s.end,'text':s.text,'avg_logprob':s.avg_logprob,'no_speech_prob':s.no_speech_prob,
           'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in (s.words or [])]} for s in segments]
    text=''.join(x['text'] for x in rows)
    result={'file':str(path),'duration':float(meta['format']['duration']),
        'streams':[{'type':s['codec_type'],'codec':s['codec_name'],'width':s.get('width'),'height':s.get('height'),'sample_rate':s.get('sample_rate')} for s in meta['streams']],
        'asr_text':text,'asr_kana':kana(text),'segments':rows,'review_note':'ASR is a screening check, not native-speaker certification.'}
    if expected is not None:
        result['expected']=expected;result['expected_kana']=kana(expected)
        result['kana_similarity']=SequenceMatcher(None,kana(expected),kana(text)).ratio()
    out=path.with_suffix('.qa.json');out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('path');ap.add_argument('--expected');args=ap.parse_args();inspect(Path(args.path),args.expected)
