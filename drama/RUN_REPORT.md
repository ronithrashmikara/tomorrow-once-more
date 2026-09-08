# Tomorrow, Once More: delivery and compute report

Date: 8 September 2026.

## Delivered

- **A finished full-length film: `output/Tomorrow_Once_More_Hour_1.mp4`, 1:07:51, 1280x720, 121 MB.**
  It is a rendered caption film with real Japanese voice performance, not generated footage. See "What the film is" below.
- Opening-hour screenplay: 24 sequential scenes, 1,032 paired Japanese/English dialogue turns, Japanese action summaries, comprehension questions and study notes.
- A 7 hour 30 minute story plan and reusable full-production prompt.
- Broad N5/N4 grammar inventory, grouped variants, supplementary discourse expressions, and marked bridge topics. This is an unofficial editorial syllabus, not an official exhaustive JLPT specification.
- Editable source, structured screenplay JSON, per-cue timing, and the film build scripts.

## What the film is

Every one of the 1,032 dialogue lines and 48 narration blocks was synthesized as Japanese
neural speech (Microsoft `ja-JP-NanamiNeural` and `ja-JP-KeitaNeural`). The eleven characters
are separated by per-character pitch and rate, because only two Japanese voices exist on that
service. Measured speech totals 61.9 minutes; the film runs 67.9 minutes with turn spacing,
scene breaks and title cards.

The picture is composed, not generated: per-scene lighting palettes keyed to the time of day
in each location, a speaker chip, the kana line, the English line, scene header, and a
progress bar with timecode. **No AI-generated video model produced any frame of this file.**
It is stated here rather than implied, because the earlier plan committed to not substituting
a slideshow silently.

Timing is derived from decoded PCM sample counts rather than container metadata, so subtitles
cannot drift from the audio across the hour. Verified by transcribing four windows spread
across the film with faster-whisper and confirming the scripted line is heard at its own cue
timestamp (kana script versus kanji transcript accounts for the literal string difference):

| Cue | At | Script | Heard |
|---|---|---|---|
| S01-L007 | 0:00:40 | おかあさんの こえ……。 | お母さんの声 |
| S07-L032 | 0:17:58 | おかあさんの ともだちですか。 | お母さんの友達ですか |
| S16-L023 | 0:43:08 | はい。でも、バターの しゃしんも です。 | はい でもバターの写真もです |
| S24-L027 | 1:05:55 | えきの うらの かいしゃです。 | 駅の裏の会社です |

Build: `film/tts_build.py` (speech), then `film/render_film.py` (picture, mux, cue sheet).
`film/cue_sheet.json` carries every cue's start, duration, speaker and both texts.

## Modal / MiniMax H3 status

The payment-method block reported earlier is **resolved**. A bounded L40S hardware check ran
successfully, so GPU functions now register.

Two bounded H3 Turbo benchmark attempts were made. Neither produced a video, and neither
reached a completed GPU generation:

1. `modal_h3.py` downloaded the checkpoint into a plain `local_dir`. The repository's
   `modular_model_index.json` still resolves each component against the Hub, so the offline
   load returned a pipeline with no transformer. This attempt did reach the B200 and failed
   during component loading.
2. `modal_h3_run.py` moved the download into the real HF cache. That worked (290 GB, 525 s),
   but `snapshot_download` pinned the commit SHA, so the cache holds `snapshots/<sha>` with no
   `refs/main`; the offline `from_pretrained` then asked for `main` and found nothing. This
   attempt failed before the GPU call, so no GPU seconds were spent on it.

The remaining fix is to pass `revision=MODEL_REV` to `ModularPipeline.from_pretrained`. It has
not been run.

**Cleanup performed.** All task apps are stopped with zero running tasks. No web endpoint and
no warm container was created. The two model-cache volumes (`aoi-h3-cache-v2`,
`aoi-h3-benchmark-cache`) were deleted at the user's request, so a retry re-downloads the
weights (about 9 minutes). Unrelated volumes were left alone.

## Cost of an H3 hour, before anyone commits to it

An hour of H3 output is roughly 700 shots of 5 seconds. At an optimistic 45 seconds per shot on
B200, that is about 9 hours of B200 plus the 192 GB RAM the current function requests -
on the order of $100 or more, well past the $15 gate in `budget_15.json` and past $30.
The hosted MiniMax H3 768P API at the checked $0.08/second would be $288 for 3,600 output
seconds, and Modal credits do not pay that separate bill.

No per-shot number has been measured yet. Before any full-film job: fix the revision pin, run
the single bounded benchmark, read its real generation seconds, then recompute including
loading, retries and storage, and keep a reserve. Do not start a batch whose upper-bound cost
exceeds the remaining budget.

## Credentials

The Modal token was supplied in conversation and used only as environment variables in the
invocation shell. It is not written into any project file, PDF or report. **Rotate it.**

## References

- https://modal.com/pricing
- https://modal.com/docs/guide/gpu
- https://platform.minimax.io/docs/guides/pricing-paygo
- https://huggingface.co/MiniMaxAI/MiniMax-H3
- https://huggingface.co/lightx2v/Minimax-h3-Turbo
