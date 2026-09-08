"""Synthesize every screenplay line with edge-tts and record measured durations."""
import argparse, asyncio, json, re, subprocess, sys
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parent

# Only two Japanese neural voices exist; characters are separated by pitch and rate.
VOICES = {
    "あおい":       ("ja-JP-NanamiNeural", "+6Hz",  "+0%"),
    "みさき":       ("ja-JP-NanamiNeural", "-14Hz", "-8%"),
    "はる":         ("ja-JP-KeitaNeural",  "+6Hz",  "+2%"),
    "りな":         ("ja-JP-NanamiNeural", "+26Hz", "+7%"),
    "れん":         ("ja-JP-KeitaNeural",  "-16Hz", "-4%"),
    "ゆい":         ("ja-JP-NanamiNeural", "+16Hz", "+3%"),
    "さとう":       ("ja-JP-KeitaNeural",  "-26Hz", "-10%"),
    "おきゃくさん": ("ja-JP-KeitaNeural",  "+14Hz", "-2%"),
    "てんいん":     ("ja-JP-NanamiNeural", "-6Hz",  "+5%"),
    "なお":         ("ja-JP-KeitaNeural",  "+20Hz", "+4%"),
    "こえ":         ("ja-JP-NanamiNeural", "-30Hz", "-12%"),
    "__action__":   ("ja-JP-KeitaNeural",  "-10Hz", "-6%"),
}

def speech_text(text):
    # Learner spacing helps the eye, not the voice; collapse it before synthesis.
    return re.sub(r"[\s　]+", "", text).strip()

def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path.name], cwd=path.parent,
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())

def units(screenplay):
    scenes = json.loads(screenplay.read_text(encoding="utf8"))
    rows = []
    for scene in scenes:
        for index, block in enumerate(scene["blocks"]):
            speaker = block.get("speaker", "__action__") if block["type"] == "dialogue" else "__action__"
            rows.append({
                "uid": block.get("id") or f"S{scene['key']}-A{index:03}",
                "scene_key": scene["key"], "scene_en": scene["en"], "scene_jp": scene["jp"],
                "location": scene["location"], "type": block["type"], "speaker": speaker,
                "jp": block["jp"], "en": block["en"],
            })
    return rows

async def synth(row, semaphore, audio):
    path = audio / f"{row['uid']}.mp3"
    voice, pitch, rate = VOICES[row["speaker"]]
    if not path.exists() or path.stat().st_size == 0:
        async with semaphore:
            for attempt in range(4):
                try:
                    tts = edge_tts.Communicate(speech_text(row["jp"]), voice, pitch=pitch, rate=rate)
                    await tts.save(str(path))
                    break
                except Exception as error:
                    if attempt == 3:
                        raise
                    await asyncio.sleep(2 * (attempt + 1))
    row["audio"] = path.name
    row["voice"] = voice
    row["speech_seconds"] = duration(path)
    return row

async def main(screenplay, audio, lines_out):
    audio.mkdir(parents=True, exist_ok=True)
    rows = units(screenplay)
    semaphore = asyncio.Semaphore(8)
    done = 0
    tasks = [asyncio.create_task(synth(row, semaphore, audio)) for row in rows]
    for task in asyncio.as_completed(tasks):
        await task
        done += 1
        if done % 50 == 0:
            print(f"{done}/{len(rows)}", flush=True)
    lines_out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf8")
    total = sum(r["speech_seconds"] for r in rows)
    print(f"lines={len(rows)} measured_speech={total:.1f}s ({total/60:.1f} min)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Japanese voice audio and a measured cue sheet.")
    parser.add_argument("--screenplay", type=Path, default=ROOT.parent / "screenplay.json")
    parser.add_argument("--audio-dir", type=Path, default=ROOT / "audio")
    parser.add_argument("--lines-out", type=Path, default=ROOT / "lines.json")
    args = parser.parse_args()
    asyncio.run(main(args.screenplay, args.audio_dir, args.lines_out))
