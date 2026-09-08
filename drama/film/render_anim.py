"""Animated learning-drama cut built from character stills and optional scenery.

Characters are composited over white, the speaker animated with a slow idle
float and a breath-scale while their line plays, the previous speaker held
beside them dimmed. Raw frames are piped straight into ffmpeg, so nothing is
written to disk per frame.

Drop character art in film/characters/<name>.png (see CHARACTER_FILES). Add
16:9 scenery to film/backgrounds and map it in visuals.json. Missing art falls
back to a flat placeholder figure so the cut always renders.
"""
import argparse, json, subprocess, wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
AUDIO, WAV, ART = ROOT / "audio", ROOT / "wav", ROOT / "characters"
BACKGROUNDS, VISUALS = ROOT / "backgrounds", ROOT / "visuals.json"
OUT = ROOT.parent.parent / "output"
for folder in (WAV, ART, BACKGROUNDS, OUT):
    folder.mkdir(parents=True, exist_ok=True)

W, H, RATE = 1280, 720, 24000
GAP, SCENE_CARD, HEAD, TAIL = 0.30, 1.40, 6.0, 8.0
FLOOR = 528                       # where every character's feet sit
SPEAKER_H, LISTENER_H = 400, 350   # figure heights, speaker slightly nearer
SPEAKER_X, LISTENER_X = 0.21, 0.79  # they face each other across the caption
CAPTION_TOP, CAPTION_BOTTOM = 556, 694

FONTS = Path("C:/Windows/Fonts")
def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)
JP_BIG, JP_MID, JP_SMALL = font("YuGothB.ttc", 44), font("YuGothM.ttc", 32), font("YuGothM.ttc", 23)
EN_MID, EN_SMALL = font("YuGothM.ttc", 27), font("YuGothM.ttc", 20)
# Largest pair first; a long line steps down until the caption band fits it.
CAPTION_STEPS = [(font("YuGothB.ttc", 44), 56, font("YuGothM.ttc", 27), 36),
                 (font("YuGothB.ttc", 38), 48, font("YuGothM.ttc", 24), 32),
                 (font("YuGothB.ttc", 32), 41, font("YuGothM.ttc", 21), 28),
                 (font("YuGothB.ttc", 27), 35, font("YuGothM.ttc", 19), 25)]
TITLE_JP, TITLE_EN = font("YuGothB.ttc", 58), font("YuGothM.ttc", 27)

INK, SUB, FAINT, PAPER = (26, 26, 30), (118, 122, 132), (176, 180, 188), (255, 255, 255)

ACCENTS = {
    "あおい": (72, 110, 176), "みさき": (186, 96, 96), "はる": (74, 156, 182),
    "りな": (200, 96, 148), "れん": (86, 116, 190), "ゆい": (120, 150, 74),
    "さとう": (150, 122, 74), "おきゃくさん": (118, 130, 144), "てんいん": (146, 112, 176),
    "なお": (78, 158, 118), "こえ": (108, 108, 128), "__action__": (120, 124, 134),
}
NAMES_EN = {
    "あおい": "AOI", "みさき": "MISAKI", "はる": "HARU", "りな": "RINA", "れん": "REN",
    "ゆい": "YUI", "さとう": "SATO", "おきゃくさん": "CUSTOMER", "てんいん": "CLERK",
    "なお": "NAO", "こえ": "VOICE", "__action__": "NARRATION",
}
CHARACTER_FILES = {jp: en.lower() for jp, en in NAMES_EN.items()}


# ---------------------------------------------------------------- character art

def placeholder(colour, height):
    """Flat stand-in figure, so the cut renders before real art exists."""
    width = int(height * 0.46)
    card = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    head = int(height * 0.20)
    draw.ellipse([(width - head) // 2, 0, (width + head) // 2, head], fill=colour + (255,))
    draw.rounded_rectangle([width * 0.12, head * 1.12, width * 0.88, height],
                           radius=int(width * 0.22), fill=colour + (210,))
    return card


def art_path(speaker):
    """Art may be filed under the kana role name or its romaji."""
    for stem in (speaker, CHARACTER_FILES[speaker]):
        for suffix in (".png", ".webp", ".jpg", ".jpeg"):
            path = ART / (stem + suffix)
            if path.exists():
                return path, suffix
    return None, None


def load_art(speaker, height):
    path, suffix = art_path(speaker)
    if path is None:
        return placeholder(ACCENTS[speaker], height)
    art = Image.open(path).convert("RGBA")
    if suffix in (".jpg", ".jpeg"):
        # A flat format carries no alpha, so key its white ground out here.
        pixels = np.asarray(art).astype(np.int16)
        lightness = pixels[:, :, :3].min(axis=2)
        alpha = np.clip((246 - lightness) * 8, 0, 255).astype(np.uint8)
        art = Image.fromarray(np.dstack([pixels[:, :, :3].astype(np.uint8), alpha]))
    # The stage is white, so fade out anything that is already essentially white.
    # Card panels the cutout missed disappear; a white shirt loses a fill that was
    # invisible against white anyway, while its linework and shading stay.
    pixels = np.asarray(art).astype(np.float32)
    lightness = pixels[:, :, :3].min(axis=2)
    pixels[:, :, 3] *= np.clip((225 - lightness) / 25, 0, 1)
    art = Image.fromarray(pixels.astype(np.uint8))

    scale = height / art.height
    return art.resize((max(1, round(art.width * scale)), height), Image.LANCZOS)


def art_cache(speakers):
    cache = {}
    for speaker in speakers:
        if art_path(speaker)[0] is None:
            continue        # no drawing: the line plays over the caption alone
        cache[speaker] = {"speaker": np.asarray(load_art(speaker, SPEAKER_H)).astype(np.int16),
                          "listener": np.asarray(load_art(speaker, LISTENER_H)).astype(np.int16)}
    return cache


def paste(canvas, art, cx, feet, opacity=1.0):
    """Alpha-composite an RGBA array centred on cx with its feet on `feet`."""
    height, width = art.shape[:2]
    x0, y0 = int(cx - width / 2), int(feet - height)
    x1, y1 = x0 + width, y0 + height
    sx0, sy0 = max(0, -x0), max(0, -y0)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x1), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        return
    patch = art[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
    alpha = (patch[:, :, 3:4] * opacity) / 255.0
    target = canvas[y0:y1, x0:x1]
    canvas[y0:y1, x0:x1] = target + (patch[:, :, :3] - target) * alpha


def shadow(draw, cx, width):
    draw.ellipse([cx - width * 0.42, FLOOR - 9, cx + width * 0.42, FLOOR + 9], fill=(238, 239, 242))


# ---------------------------------------------------------------- scenery

def load_visuals():
    if not VISUALS.exists():
        return {"default_mode": "white", "backgrounds": {}}
    return json.loads(VISUALS.read_text(encoding="utf8"))


def cover(image):
    """Resize and centre-crop background art to the teaching-video canvas."""
    image = image.convert("RGB")
    scale = max(W / image.width, H / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    left, top = (resized.width - W) // 2, (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def stage_for(row, mode, visual_config, cache):
    """Return an intentionally quiet stage, leaving captions legible in scenic mode."""
    if mode != "scenic":
        return Image.new("RGB", (W, H), PAPER)
    filename = visual_config.get("backgrounds", {}).get(row["scene_key"])
    path = BACKGROUNDS / filename if filename else None
    if not path or not path.exists():
        return Image.new("RGB", (W, H), PAPER)
    if path not in cache:
        cache[path] = cover(Image.open(path)).filter(ImageFilter.GaussianBlur(radius=0.7))
    # The washed backdrop gives atmosphere without competing with learner text.
    return Image.blend(cache[path], Image.new("RGB", (W, H), PAPER), 0.62)


# ---------------------------------------------------------------- text layout

def wrap(draw, text, typeface, width):
    lines, line = [], ""
    for word in text.split(" "):
        probe = (line + " " + word).strip()
        if draw.textlength(probe, font=typeface) <= width or not line:
            line = probe
        else:
            lines.append(line); line = word
    if line:
        lines.append(line)
    output = []
    for item in lines:                      # Japanese has no spaces; hard-wrap it
        while draw.textlength(item, font=typeface) > width:
            cut = len(item)
            while cut > 1 and draw.textlength(item[:cut], font=typeface) > width:
                cut -= 1
            output.append(item[:cut]); item = item[cut:]
        output.append(item)
    return output


def centred(draw, lines, typeface, top, fill, spacing):
    for index, line in enumerate(lines):
        length = draw.textlength(line, font=typeface)
        draw.text(((W - length) / 2, top + index * spacing), line, font=typeface, fill=fill)
    return top + len(lines) * spacing


def timecode(seconds):
    seconds = int(seconds)
    return f"{seconds // 3600}:{seconds // 60 % 60:02}:{seconds % 60:02}"


def fit_caption(draw, jp_text, en_text):
    """Pick the largest type that keeps both lines inside the caption band."""
    room = CAPTION_BOTTOM - CAPTION_TOP
    for jp_font, jp_step, en_font, en_step in CAPTION_STEPS:
        jp = wrap(draw, jp_text, jp_font, W - 190)
        en = wrap(draw, en_text, en_font, W - 230)
        height = len(jp) * jp_step + 12 + len(en) * en_step
        if height <= room:
            return jp, jp_font, jp_step, en, en_font, en_step, height
    return jp, jp_font, jp_step, en, en_font, en_step, height


def line_plate(row, position, total, stage=None):
    """Everything that does not move: captions, name chip, headers, floor."""
    plate = stage.copy() if stage else Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(plate)

    draw.text((48, 30), f"SCENE {row['scene_no']} / 24", font=EN_SMALL, fill=FAINT)
    draw.text((48, 54), row["scene_jp"], font=JP_SMALL, fill=SUB)
    title = row["scene_en"].upper()
    draw.text((W - 48 - draw.textlength(title, font=EN_SMALL), 30), title, font=EN_SMALL, fill=FAINT)
    draw.text((W - 48 - draw.textlength(row["location"], font=EN_SMALL), 54),
              row["location"], font=EN_SMALL, fill=FAINT)

    accent = ACCENTS[row["speaker"]]
    if row["type"] == "dialogue":
        draw.rounded_rectangle([26, CAPTION_TOP - 14, W - 26, H - 12], radius=26, fill=(255, 255, 255))
        chip = f"{row['speaker']}   {NAMES_EN[row['speaker']]}"
        length = draw.textlength(chip, font=JP_SMALL)
        left = (W - length) / 2
        draw.rounded_rectangle([left - 20, 104, left + length + 20, 144], 20, fill=accent)
        draw.text((left, 111), chip, font=JP_SMALL, fill=PAPER)
        draw.line([(48, FLOOR + 3), (W - 48, FLOOR + 3)], fill=(240, 241, 244), width=2)

        jp, jp_font, jp_step, en, en_font, en_step, height = fit_caption(draw, row["jp"], row["en"])
        top = CAPTION_TOP + (CAPTION_BOTTOM - CAPTION_TOP - height) / 2
        bottom = centred(draw, jp, jp_font, top, INK, jp_step)
        centred(draw, en, en_font, bottom + 12, SUB, en_step)
    else:
        label = "ナレーション   NARRATION"
        length = draw.textlength(label, font=JP_SMALL)
        draw.text(((W - length) / 2, 111), label, font=JP_SMALL, fill=FAINT)
        jp = wrap(draw, row["jp"], JP_MID, W - 180)
        bottom = centred(draw, jp, JP_MID, 300 - len(jp) * 24, INK, 48)
        centred(draw, wrap(draw, row["en"], EN_SMALL, W - 220), EN_SMALL, bottom + 18, SUB, 30)

    draw.line([(48, H - 34), (W - 48, H - 34)], fill=(238, 239, 242), width=2)
    draw.line([(48, H - 34), (48 + (W - 92) * position / total, H - 34)], fill=accent, width=2)
    draw.text((48, H - 26), timecode(position), font=EN_SMALL, fill=FAINT)
    stamp = f"{row['uid']}  |  {timecode(total)}"
    draw.text((W - 48 - draw.textlength(stamp, font=EN_SMALL), H - 26), stamp, font=EN_SMALL, fill=FAINT)
    return plate


def scene_plate(row):
    plate = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(plate)
    draw.text((48, 30), f"SCENE {row['scene_no']} / 24", font=EN_SMALL, fill=FAINT)
    top = centred(draw, wrap(draw, row["scene_jp"], TITLE_JP, W - 220), TITLE_JP, 286, INK, 70)
    top = centred(draw, wrap(draw, row["scene_en"], TITLE_EN, W - 260), TITLE_EN, top + 18, SUB, 36)
    centred(draw, [row["location"]], EN_SMALL, top + 10, FAINT, 28)
    return plate


def title_plate(lines):
    plate = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(plate)
    top = 236
    for text, typeface, colour, spacing in lines:
        top = centred(draw, wrap(draw, text, typeface, W - 200), typeface, top, colour, spacing) + 22
    return plate


# ---------------------------------------------------------------- audio

def to_wav(name, audio, wav):
    source, target = audio / name, wav / (Path(name).stem + ".wav")
    if not target.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-ac", "1",
                        "-ar", str(RATE), "-c:a", "pcm_s16le", str(target)], check=True)
    with wave.open(str(target)) as handle:
        return np.frombuffer(handle.readframes(handle.getnframes()), dtype=np.int16)


# ---------------------------------------------------------------- build

def build(scenes_wanted, fps, suffix, visual_mode, visual_config, lines_path, audio, wav):
    rows = json.loads(lines_path.read_text(encoding="utf8"))
    order = {key: n for n, key in enumerate(dict.fromkeys(r["scene_key"] for r in rows), 1)}
    for row in rows:
        row["scene_no"] = order[row["scene_key"]]
    if scenes_wanted:
        rows = [r for r in rows if r["scene_no"] in scenes_wanted]
    if not rows:
        raise SystemExit("no rows selected")

    with ThreadPoolExecutor(16) as pool:
        samples = list(pool.map(lambda name: to_wav(name, audio, wav), [r["audio"] for r in rows]))

    segments, track, cursor = [], [np.zeros(int(HEAD * RATE), np.int16)], HEAD
    segments.append({"kind": "title", "start": 0.0, "seconds": HEAD, "row": rows[0]})
    previous = None
    for row, block in zip(rows, samples):
        if row["scene_key"] != previous:
            track.append(np.zeros(int(SCENE_CARD * RATE), np.int16))
            segments.append({"kind": "scene", "start": cursor, "seconds": SCENE_CARD, "row": row})
            cursor += SCENE_CARD
        else:
            track.append(np.zeros(int(GAP * RATE), np.int16))
            if segments:
                segments[-1]["seconds"] += GAP
            cursor += GAP
        previous = row["scene_key"]
        track.append(block)
        seconds = len(block) / RATE
        segments.append({"kind": "line", "start": cursor, "seconds": seconds, "row": row})
        cursor += seconds
    track.append(np.zeros(int(TAIL * RATE), np.int16))
    segments.append({"kind": "end", "start": cursor, "seconds": TAIL, "row": rows[-1]})
    total = cursor + TAIL

    audio_path = ROOT / f"anim{suffix}.wav"
    with wave.open(str(audio_path), "wb") as handle:
        handle.setnchannels(1); handle.setsampwidth(2); handle.setframerate(RATE)
        handle.writeframes(np.concatenate(track).tobytes())
    print(f"audio {total/60:.2f} min, {len(segments)} segments", flush=True)

    art = art_cache(sorted({r["speaker"] for r in rows}))
    have = [NAMES_EN[s] for s in art if art_path(s)[0] is not None]
    missing = [NAMES_EN[r["speaker"]] for r in rows if art_path(r["speaker"])[0] is None]
    print(f"art: {', '.join(have) if have else 'none'}"
          f"{'  |  no drawing (caption only): ' + ', '.join(sorted(set(missing))) if missing else ''}", flush=True)

    output = OUT / f"Tomorrow_Once_More_Animated{suffix}.mp4"
    encoder = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-i", str(audio_path),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(output)],
        stdin=subprocess.PIPE)

    title = np.asarray(title_plate([
        ("あした、もういちど", TITLE_JP, INK, 70),
        ("TOMORROW, ONCE MORE", TITLE_EN, SUB, 36),
        ("だい一じかん | The Opening Hour", JP_MID, SUB, 44),
        ("Japanese audio | kana and English on screen", EN_SMALL, FAINT, 28)])).astype(np.float32)
    ending = np.asarray(title_plate([
        ("つづく", TITLE_JP, INK, 70),
        ("TO BE CONTINUED", TITLE_EN, SUB, 36)])).astype(np.float32)

    listener = None
    scenery = {}
    written = 0
    for segment in segments:
        row, seconds = segment["row"], segment["seconds"]
        frames = max(1, round(seconds * fps))

        if segment["kind"] in ("title", "end"):
            plate = title if segment["kind"] == "title" else ending
            for _ in range(frames):
                encoder.stdin.write(plate.astype(np.uint8).tobytes())
            written += frames
            listener = None
            continue

        if segment["kind"] == "scene":
            plate = np.asarray(scene_plate(row)).astype(np.float32)
            for _ in range(frames):
                encoder.stdin.write(plate.astype(np.uint8).tobytes())
            written += frames
            listener = None
            continue

        speaker = row["speaker"]
        drawn = row["type"] == "dialogue" and speaker in art
        plate = Image.new("RGB", (W, H), PAPER)
        draw = ImageDraw.Draw(plate)
        if drawn:
            shadow(draw, W * SPEAKER_X, art[speaker]["speaker"].shape[1])
            if listener and listener != speaker and listener in art:
                shadow(draw, W * LISTENER_X, art[listener]["listener"].shape[1])
        stage = stage_for(row, visual_mode, visual_config, scenery)
        base = np.asarray(line_plate(row, segment["start"], total, stage)).astype(np.float32)
        base = np.minimum(base, np.asarray(plate).astype(np.float32))  # keep the floor shadows

        if drawn:
            still = base.copy()
            if listener and listener != speaker and listener in art:
                paste(still, art[listener]["listener"], W * LISTENER_X, FLOOR, 0.45)
            figure = art[speaker]["speaker"]
            for index in range(frames):
                phase = index / fps
                bob = np.sin(phase * 2.6) * 4.0
                canvas = still.copy()
                paste(canvas, figure, W * SPEAKER_X, FLOOR + bob)
                encoder.stdin.write(np.clip(canvas, 0, 255).astype(np.uint8).tobytes())
            listener = speaker
        else:
            for _ in range(frames):
                encoder.stdin.write(np.clip(base, 0, 255).astype(np.uint8).tobytes())
            listener = speaker if row["type"] == "dialogue" else None

        written += frames
        if segment["start"] and int(segment["start"]) % 300 < 1:
            print(f"  {timecode(segment['start'])} / {timecode(total)}", flush=True)

    encoder.stdin.close()
    encoder.wait()
    print(f"wrote {output}  ({written} frames, {written/fps/60:.2f} min)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenes", default="", help="e.g. 1,2,3 — default is the whole film")
    parser.add_argument("--fps", type=int, default=20)
    parser.add_argument("--suffix", default="")
    parser.add_argument("--visual-mode", choices=("white", "scenic"), default=None,
                        help="white is the study layout; scenic uses mapped scenery behind it")
    parser.add_argument("--lines", type=Path, default=ROOT / "lines.json")
    parser.add_argument("--audio-dir", type=Path, default=AUDIO)
    parser.add_argument("--wav-dir", type=Path, default=WAV)
    args = parser.parse_args()
    wanted = {int(x) for x in args.scenes.split(",") if x.strip()}
    config = load_visuals()
    args.wav_dir.mkdir(parents=True, exist_ok=True)
    build(wanted, args.fps, args.suffix, args.visual_mode or config.get("default_mode", "white"),
          config, args.lines, args.audio_dir, args.wav_dir)
