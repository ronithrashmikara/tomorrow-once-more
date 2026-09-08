"""Assemble the measured speech and screenplay into the full-length film.

Timing is derived from decoded PCM sample counts, so subtitles never drift from audio.
"""
import json, subprocess, wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
AUDIO, WAV, FRAMES = ROOT / "audio", ROOT / "wav", ROOT / "frames"
OUT = ROOT.parent.parent / "output"
for folder in (WAV, FRAMES, OUT):
    folder.mkdir(parents=True, exist_ok=True)

W, H, FPS, RATE = 1280, 720, 12, 24000
GAP, SCENE_GAP, HEAD, TAIL = 0.30, 1.10, 7.0, 9.0

FONTS = Path("C:/Windows/Fonts")
def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)
JP_BIG, JP_MID, JP_SMALL = font("YuGothB.ttc", 46), font("YuGothM.ttc", 34), font("YuGothM.ttc", 24)
EN_MID, EN_SMALL, EN_TINY = font("YuGothM.ttc", 28), font("YuGothM.ttc", 21), font("YuGothM.ttc", 17)
TITLE_JP, TITLE_EN = font("YuGothB.ttc", 64), font("YuGothM.ttc", 30)

# Palettes keyed by the light in each location, so the film reads as one day passing.
PALETTES = {
    "dawn":      ((16, 20, 34), (58, 46, 62), (232, 176, 138)),
    "early":     ((18, 22, 30), (62, 62, 72), (226, 200, 156)),
    "morning":   ((20, 26, 32), (60, 74, 82), (232, 214, 172)),
    "midmorning":((22, 28, 32), (72, 84, 86), (238, 222, 182)),
    "midday":    ((24, 28, 30), (86, 92, 88), (244, 234, 204)),
    "afternoon": ((28, 24, 26), (94, 76, 66), (240, 206, 158)),
    "default":   ((20, 24, 30), (70, 76, 84), (230, 214, 186)),
}
ACCENTS = {
    "あおい": (236, 196, 150), "みさき": (206, 152, 152), "はる": (150, 200, 214),
    "りな": (226, 168, 196), "れん": (146, 172, 220), "ゆい": (196, 208, 152),
    "さとう": (198, 178, 146), "おきゃくさん": (176, 186, 196), "てんいん": (200, 184, 214),
    "なお": (166, 210, 186), "こえ": (150, 150, 168), "__action__": (150, 158, 168),
}
NAMES_EN = {
    "あおい": "AOI", "みさき": "MISAKI", "はる": "HARU", "りな": "RINA", "れん": "REN",
    "ゆい": "YUI", "さとう": "SATO", "おきゃくさん": "CUSTOMER", "てんいん": "SHOP CLERK",
    "なお": "NAO", "こえ": "VOICE", "__action__": "SCENE",
}

def light_of(location):
    text = location.lower()
    for key in ("dawn", "midmorning", "midday", "afternoon", "morning", "early"):
        if key in text:
            return key
    return "default"

def background(location, seed):
    """Vertical gradient plus a soft key light, rendered small and resampled for smoothness."""
    low, mid, high = PALETTES[light_of(location)]
    small = np.zeros((90, 160, 3), dtype=np.float32)
    ramp = np.linspace(0, 1, 90, dtype=np.float32)[:, None]
    for channel in range(3):
        small[:, :, channel] = low[channel] * (1 - ramp) + mid[channel] * ramp
    ys, xs = np.mgrid[0:90, 0:160].astype(np.float32)
    rng = np.random.default_rng(seed)
    cx, cy = rng.uniform(30, 130), rng.uniform(18, 46)
    glow = np.exp(-(((xs - cx) / 58) ** 2 + ((ys - cy) / 34) ** 2))
    for channel in range(3):
        small[:, :, channel] += (high[channel] - small[:, :, channel]) * glow * 0.42
    image = Image.fromarray(np.clip(small, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    canvas = np.asarray(image).astype(np.float32)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    vignette = 1 - 0.55 * (((xs - W / 2) / (W / 2)) ** 2 + ((ys - H / 2) / (H / 2)) ** 2)
    canvas *= np.clip(vignette, 0.25, 1)[:, :, None]
    canvas += rng.normal(0, 2.6, canvas.shape)          # light grain keeps flat areas from banding
    canvas[:64] *= 0.30
    canvas[H - 92:] *= 0.30                              # plates that hold the header and caption band
    return Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))

def wrap(draw, text, typeface, width):
    lines, line = [], ""
    for word in text.split(" "):
        probe = (line + " " + word).strip()
        if draw.textlength(probe, font=typeface) <= width or not line:
            line = probe
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    # Japanese has no spaces to break on; fall back to a hard character wrap.
    output = []
    for item in lines:
        while draw.textlength(item, font=typeface) > width:
            cut = len(item)
            while cut > 1 and draw.textlength(item[:cut], font=typeface) > width:
                cut -= 1
            output.append(item[:cut])
            item = item[cut:]
        output.append(item)
    return output

def centered(draw, lines, typeface, top, fill, spacing):
    for index, line in enumerate(lines):
        length = draw.textlength(line, font=typeface)
        draw.text(((W - length) / 2, top + index * spacing), line, font=typeface, fill=fill)
    return top + len(lines) * spacing

def timecode(seconds):
    seconds = int(seconds)
    return f"{seconds // 3600}:{seconds // 60 % 60:02}:{seconds % 60:02}"

def chrome(image, row, position, total):
    draw = ImageDraw.Draw(image)
    draw.text((46, 20), f"SCENE {row['scene_no']} / 24", font=EN_TINY, fill=(150, 156, 166))
    draw.text((46, 40), row["scene_jp"], font=JP_SMALL, fill=(226, 220, 210))
    title = row["scene_en"].upper()
    draw.text((W - 46 - draw.textlength(title, font=EN_TINY), 24), title, font=EN_TINY, fill=(178, 184, 194))
    place = row["location"]
    draw.text((W - 46 - draw.textlength(place, font=EN_TINY), 46), place, font=EN_TINY, fill=(122, 128, 138))
    draw.line([(46, H - 40), (W - 46, H - 40)], fill=(58, 62, 70), width=2)
    draw.line([(46, H - 40), (46 + (W - 92) * position / total, H - 40)], fill=(214, 178, 132), width=2)
    draw.text((46, H - 30), timecode(position), font=EN_TINY, fill=(132, 138, 148))
    stamp = f"{row['uid']}  |  {timecode(total)}"
    draw.text((W - 46 - draw.textlength(stamp, font=EN_TINY), H - 30), stamp, font=EN_TINY, fill=(96, 102, 112))

def frame(row, base, position, total, path):
    image = base.copy()
    draw = ImageDraw.Draw(image)
    accent = ACCENTS[row["speaker"]]
    label = NAMES_EN[row["speaker"]] if row["type"] == "dialogue" else "NARRATION"
    name = row["speaker"] if row["type"] == "dialogue" else "ナレーション"
    chip = f"{name}   {label}"
    length = draw.textlength(chip, font=JP_SMALL)
    left = (W - length) / 2
    draw.rounded_rectangle([left - 22, 132, left + length + 22, 176], 22, outline=accent, width=2)
    draw.text((left, 140), chip, font=JP_SMALL, fill=accent)

    if row["type"] == "dialogue":
        jp_lines = wrap(draw, row["jp"], JP_BIG, W - 220)
        bottom = centered(draw, jp_lines, JP_BIG, 300 - len(jp_lines) * 30, (245, 242, 236), 66)
        en_lines = wrap(draw, row["en"], EN_MID, W - 260)
        centered(draw, en_lines, EN_MID, bottom + 34, (176, 182, 192), 40)
    else:
        jp_lines = wrap(draw, row["jp"], JP_MID, W - 200)
        bottom = centered(draw, jp_lines, JP_MID, 246 - len(jp_lines) * 12, (238, 232, 222), 50)
        en_lines = wrap(draw, row["en"], EN_SMALL, W - 240)
        centered(draw, en_lines, EN_SMALL, bottom + 26, (158, 164, 176), 32)

    chrome(image, row, position, total)
    image.save(path, compress_level=1)

def card(lines, path, seed):
    image = background("Bedroom above the cafe, dawn", seed)
    draw = ImageDraw.Draw(image)
    top = 210
    for text, typeface, colour, spacing in lines:
        top = centered(draw, wrap(draw, text, typeface, W - 200), typeface, top, colour, spacing) + 24
    image.save(path, compress_level=1)

def to_wav(name):
    source, target = AUDIO / name, WAV / (Path(name).stem + ".wav")
    if not target.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-ac", "1",
                        "-ar", str(RATE), "-c:a", "pcm_s16le", str(target)], check=True)
    with wave.open(str(target)) as handle:
        return np.frombuffer(handle.readframes(handle.getnframes()), dtype=np.int16)

def main():
    rows = json.loads((ROOT / "lines.json").read_text(encoding="utf8"))
    order = {key: n for n, key in enumerate(dict.fromkeys(row["scene_key"] for row in rows), 1)}
    for row in rows:
        row["scene_no"] = order[row["scene_key"]]
    with ThreadPoolExecutor(16) as pool:
        samples = list(pool.map(to_wav, [row["audio"] for row in rows]))
    print("decoded", len(samples), flush=True)

    track, timeline, cursor = [np.zeros(int(HEAD * RATE), np.int16)], [], HEAD
    previous_scene = None
    for row, block in zip(rows, samples):
        gap = SCENE_GAP if row["scene_key"] != previous_scene else GAP
        previous_scene = row["scene_key"]
        track.append(np.zeros(int(gap * RATE), np.int16))
        cursor += gap
        track.append(block)
        seconds = len(block) / RATE
        timeline.append((row, cursor, seconds))
        cursor += seconds
    track.append(np.zeros(int(TAIL * RATE), np.int16))
    total = cursor + TAIL

    audio_path = ROOT / "film.wav"
    with wave.open(str(audio_path), "wb") as handle:
        handle.setnchannels(1); handle.setsampwidth(2); handle.setframerate(RATE)
        handle.writeframes(np.concatenate(track).tobytes())
    print(f"audio {total/60:.2f} min", flush=True)

    backgrounds = {}
    for row, _, _ in timeline:
        if row["scene_key"] not in backgrounds:
            backgrounds[row["scene_key"]] = background(row["location"], abs(hash(row["scene_key"])) % 9973)

    open_card, end_card = FRAMES / "000_open.png", FRAMES / "999_end.png"
    card([("あした、もういちど", TITLE_JP, (244, 236, 224), 78),
          ("TOMORROW, ONCE MORE", TITLE_EN, (206, 176, 138), 40),
          ("だい一じかん | The Opening Hour", JP_MID, (168, 174, 184), 44),
          ("A Japanese drama for N5-N4 learners | Japanese audio, kana and English subtitles",
           EN_SMALL, (138, 144, 154), 30)], open_card, 5)
    card([("つづく", TITLE_JP, (244, 236, 224), 78),
          ("TO BE CONTINUED", TITLE_EN, (206, 176, 138), 40),
          ("24 scenes | 1,032 dialogue lines | 11 voices", EN_SMALL, (150, 156, 166), 30)], end_card, 11)

    jobs = [(row, backgrounds[row["scene_key"]], start, total, FRAMES / f"{index:04}.png")
            for index, (row, start, seconds) in enumerate(timeline)]
    with ThreadPoolExecutor(8) as pool:
        for done, _ in enumerate(pool.map(lambda job: frame(*job), jobs), 1):
            if done % 200 == 0:
                print(f"frames {done}/{len(jobs)}", flush=True)

    entries = [(open_card, timeline[0][1])]
    for index, (row, start, seconds) in enumerate(timeline):
        nxt = timeline[index + 1][1] if index + 1 < len(timeline) else total - TAIL
        entries.append((FRAMES / f"{index:04}.png", nxt - start))
    entries.append((end_card, TAIL))

    listing = ROOT / "concat.txt"
    with listing.open("w", encoding="utf8") as handle:
        for path, seconds in entries:
            handle.write("file '%s'\nduration %.4f\n" % (path.as_posix(), seconds))
        handle.write("file '%s'\n" % entries[-1][0].as_posix())

    output = OUT / "Tomorrow_Once_More_Hour_1.mp4"
    subprocess.run(["ffmpeg", "-v", "warning", "-stats", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(listing), "-i", str(audio_path), "-fps_mode", "cfr", "-r", str(FPS),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
                    "-g", "120", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-movflags", "+faststart", str(output)], check=True)
    print("wrote", output)

    (ROOT / "cue_sheet.json").write_text(json.dumps(
        {"runtime_seconds": total, "lines": len(timeline),
         "cues": [{"uid": r["uid"], "scene": r["scene_key"], "speaker": r["speaker"],
                   "start": round(s, 3), "duration": round(d, 3), "jp": r["jp"], "en": r["en"]}
                  for r, s, d in timeline]}, ensure_ascii=False, indent=1), encoding="utf8")

main()
