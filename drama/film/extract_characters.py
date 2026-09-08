"""Cut the nine character cards out of the contact sheet and key their backgrounds out.

The sheet is a grid of pastel cards, each with lettering down its left side and the
figure on its right. We locate the cards from the white gutters, keep only the
figure side, then remove the flat card background by flooding inward from the
border - which leaves interior whites (shirts, aprons, the cat) untouched.
"""
import argparse, json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "characters_src"
OUT_DIR = ROOT / "characters"
for folder in (SRC_DIR, OUT_DIR):
    folder.mkdir(parents=True, exist_ok=True)

# Reading order across the sheet.
SHEET_NAMES = ["AOI", "RIKU", "MEI", "SORA", "NATSUKI", "HARU", "KAITO", "YUZU", "REN"]

# Which drawing plays which speaking role. Edit this, not the art.
ROLE_ART = {
    "あおい": "AOI",        # protagonist, apron, coffee pot - an exact match
    "みさき": "HARU",       # the oldest-reading woman on the sheet, cardigan and menu
    "はる": "KAITO",        # script's Haru is 12; this is the youngest, brightest face available
    "りな": "MEI",          # arrives with strawberries in the script, holds strawberry cake here
    "れん": "REN",          # named match, adult man with a coffee cup
    "ゆい": "YUZU",         # quiet, composed, the friend who waits for an honest answer
    "さとう": "RIKU",       # the still, formal-reading adult man
    "てんいん": "SORA",     # young shop clerk
    "おきゃくさん": "NATSUKI",  # weakest fit: script's customer is a man of about 60
    # なお (78) has no match on the sheet - falls back to a placeholder figure.
    # こえ is never shown, by design.
}

# Fraction of each card's width to keep, measured from the right edge, so the
# lettering on the left is cropped away. Overridable per card.
KEEP = 0.58
KEEP_OVERRIDES = {"AOI": 0.66, "HARU": 0.70, "YUZU": 0.62, "NATSUKI": 0.60}

# Pale characters sit close to the pale grounds; they need a tighter match.
TOLERANCE = {"SORA": 26, "YUZU": 44}


def bands(mask, axis, min_size):
    """Runs of rows/columns that contain any card pixels."""
    present = mask.any(axis=axis)
    runs, start = [], None
    for index, value in enumerate(present):
        if value and start is None:
            start = index
        elif not value and start is not None:
            if index - start >= min_size:
                runs.append((start, index))
            start = None
    if start is not None and len(present) - start >= min_size:
        runs.append((start, len(present)))
    return runs


def find_cards(sheet):
    pixels = np.asarray(sheet).astype(np.int16)
    ink = pixels.min(axis=2) < 246          # anything not sheet-white
    boxes = []
    for top, bottom in bands(ink, 1, 80):
        strip = ink[top:bottom]
        for left, right in bands(strip, 0, 80):
            boxes.append((left, top, right, bottom))
    return boxes


def ground_colours(pixels, where):
    """Light, well-supported colours found in `where` - the grounds to strip."""
    sample = pixels[where]
    if len(sample) < 200:
        return []
    keys, counts = np.unique((sample // 12).astype(np.int32), axis=0, return_counts=True)
    colours = []
    for index in np.argsort(counts)[::-1][:6]:
        if counts[index] < len(sample) * 0.04:
            break
        member = (sample // 12 == keys[index]).all(axis=1)
        colour = sample[member].mean(axis=0)
        if colour.mean() > 172:          # every card ground is pale; clothing is not
            colours.append(colour)
    return colours


def key_out(card, tolerance=62):
    """Strip the card's grounds one layer at a time.

    Each card is a white margin around a sharp-edged pastel panel, so one pass
    only reaches the margin. After removing it the panel is what now touches the
    exposed edge, and the next pass takes it. Interior whites - a shirt, an
    apron highlight, the cat - survive because the drawing's own outlines keep
    them from ever touching that edge.
    """
    pixels = np.asarray(card).astype(np.int16)
    height, width = pixels.shape[:2]

    removed = np.zeros((height, width), bool)
    seam = np.zeros((height, width), bool)
    seam[0], seam[-1], seam[:, 0], seam[:, -1] = True, True, True, True

    seen = []
    for _ in range(4):
        colours = ground_colours(pixels, seam & ~removed)
        seen += colours
        if not colours:
            break
        ground = np.zeros((height, width), bool)
        for colour in colours:
            ground |= np.abs(pixels - colour).sum(axis=2) < tolerance
        ground &= ~removed

        labels, count = ndimage.label(ground)
        if not count:
            break
        touching = np.unique(labels[seam & ground])
        touching = touching[touching > 0]
        if not len(touching):
            break
        sizes = ndimage.sum(np.ones_like(labels, bool), labels, index=touching)
        big = touching[sizes > 400]
        if not len(big):
            break
        removed |= np.isin(labels, big)
        seam = ndimage.binary_dilation(removed, iterations=2) & ~removed

    # Where the crop left no white margin, a panel can reach the edge with
    # nothing to seed from. Any border pixel that is pale, flat and matches a
    # ground already found is such a panel - the figures all meet the border in
    # dark clothing, so this cannot bite into one.
    if seen:
        matches_ground = np.zeros(pixels.shape[:2], bool)
        for colour in seen:
            matches_ground |= np.abs(pixels - colour).sum(axis=2) < tolerance
        local = ndimage.uniform_filter(pixels.astype(np.float32).mean(axis=2), size=5)
        variation = ndimage.uniform_filter(
            (pixels.astype(np.float32).mean(axis=2) - local) ** 2, size=5)
        border = np.zeros(pixels.shape[:2], bool)
        border[0], border[-1], border[:, 0], border[:, -1] = True, True, True, True
        removed |= border & matches_ground & (pixels.mean(axis=2) > 168) & (variation < 36)

    # Some panels are a mid slate blue - too dark for the pale gates above. They
    # are still separable from clothing by their cool cast: these drawings put
    # blue only in panels, hair and eyes, and hair is far darker while eyes never
    # reach the border in a region this large.
    red, blue = pixels[:, :, 0], pixels[:, :, 2]
    cool = (blue - red >= 12) & (pixels.mean(axis=2) > 110)
    labels, count = ndimage.label(cool)
    if count:
        border = np.zeros(pixels.shape[:2], bool)
        border[0], border[-1], border[:, 0], border[:, -1] = True, True, True, True
        # A panel sits inside the white margin, so it never reaches the card
        # border - what it touches is the margin we have already taken.
        outside = ndimage.binary_dilation(removed | border, iterations=2)
        touching = np.unique(labels[outside & cool])
        touching = touching[touching > 0]
        if len(touching):
            sizes = ndimage.sum(np.ones_like(labels, bool), labels, index=touching)
            removed |= np.isin(labels, touching[sizes > 400])

    # Last sweep: a pale, barely-tinted region still touching the stripped area
    # is panel, not character. Safe even if it clips a white sleeve, because the
    # film composites these over white - erasing a near-white interior changes
    # nothing on screen, while a surviving tinted panel is plainly visible.
    spread = pixels.max(axis=2) - pixels.min(axis=2)
    washed = (pixels.mean(axis=2) > 222) & (spread < 24)
    labels, count = ndimage.label(washed)
    if count:
        near = ndimage.binary_dilation(removed, iterations=2)
        touching = np.unique(labels[near & washed])
        touching = touching[touching > 0]
        if len(touching):
            sizes = ndimage.sum(np.ones_like(labels, bool), labels, index=touching)
            removed |= np.isin(labels, touching[sizes > 300])

    # Colour clusters jump the sharp margin/panel seam but cannot follow a
    # gradient; this last pass grows outward pixel by pixel wherever neighbours
    # nearly match, which follows the panels' soft shading. Restricted to pale
    # pixels so it can never wander into dark clothing or hair.
    pale = pixels.mean(axis=2) > 168
    vertical = np.abs(pixels[1:, :] - pixels[:-1, :]).sum(axis=2) < 26
    horizontal = np.abs(pixels[:, 1:] - pixels[:, :-1]).sum(axis=2) < 26
    while True:
        grown = removed.copy()
        grown[1:, :] |= removed[:-1, :] & vertical
        grown[:-1, :] |= removed[1:, :] & vertical
        grown[:, 1:] |= removed[:, :-1] & horizontal
        grown[:, :-1] |= removed[:, 1:] & horizontal
        grown &= pale
        grown |= removed
        if grown.sum() == removed.sum():
            break
        removed = grown

    # Keep only the figure itself: the largest surviving region, with its holes
    # filled. That restores pale hair and sleeves the ground pass punched through,
    # and drops leftover panel corners and stray lettering in one move.
    kept = ~removed
    labels, count = ndimage.label(kept)
    if count:
        sizes = ndimage.sum(np.ones_like(labels, bool), labels, index=np.arange(1, count + 1))
        figure = labels == (int(np.argmax(sizes)) + 1)
        figure = ndimage.binary_fill_holes(figure)
    else:
        figure = kept

    alpha = np.where(figure, 255, 0).astype(np.uint8)
    alpha = ndimage.median_filter(alpha, size=3)
    alpha = ndimage.gaussian_filter(alpha, 0.8)

    rgba = np.dstack([pixels.astype(np.uint8), alpha])
    solid = np.argwhere(alpha > 24)
    if solid.size:
        y0, x0 = solid.min(axis=0)
        y1, x1 = solid.max(axis=0) + 1
        rgba = rgba[y0:y1, x0:x1]
    return Image.fromarray(rgba)


def main(sheet_path):
    sheet = Image.open(sheet_path).convert("RGB")
    boxes = find_cards(sheet)
    print(f"found {len(boxes)} cards in {sheet.size[0]}x{sheet.size[1]}")
    if len(boxes) != len(SHEET_NAMES):
        print("  expected 9 - check the sheet or the gutter threshold")

    written = {}
    for name, (left, top, right, bottom) in zip(SHEET_NAMES, boxes):
        card = sheet.crop((left, top, right, bottom))
        keep = KEEP_OVERRIDES.get(name, KEEP)
        card = card.crop((int(card.width * (1 - keep)), 0, card.width, card.height))
        card.save(SRC_DIR / f"{name}.png")
        cut = key_out(card, TOLERANCE.get(name, 62))
        cut.save(SRC_DIR / f"{name}_cut.png")
        written[name] = cut.size
        print(f"  {name:9} card {right-left}x{bottom-top}  ->  cutout {cut.size[0]}x{cut.size[1]}")

    for role, sheet_name in ROLE_ART.items():
        source = SRC_DIR / f"{sheet_name}_cut.png"
        if source.exists():
            Image.open(source).save(OUT_DIR / f"{role}.png")
    (OUT_DIR / "mapping.json").write_text(
        json.dumps(ROLE_ART, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"wrote {len(ROLE_ART)} role images to {OUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet", type=Path)
    main(parser.parse_args().sheet)
