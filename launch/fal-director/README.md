# Tomorrow, Once More — live Director prototype

[Watch the recorded Director demo](../../repo_assets/clips/director-live-demo.mp4) · [Launch post copy](LAUNCH_POST.md) · [Measured run report](RUN_REPORT.md)

Aoi wakes one year before her family's café collapses. This Japanese-learning story lets the learner choose her next action. H3 Max Director provides continuous animated footage that accepts new directions during the session; the application adds deterministic kana/English captions and Japanese TTS.

The 9 September 2026 recording is **51.76 seconds**. It shows the opening image animated into a café scene and Aoi putting away a clue. Two directions were sent automatically during recording. The API returned generated chunks for both; the phone-call chunk arrived at the stop limit, before its playback was captured. This is a local prototype and recorded demonstration, not a hosted public interactive service. The existing longer film is an illustrated renderer and is separate from this Director demonstration.

## Run locally

Requires Node 22+, desktop Chrome, and Python with `edge-tts` if rebuilding the three speech files. Audio assets are included. Dependencies are pinned by the lockfile.

```powershell
cd launch/fal-director
npm ci --legacy-peer-deps
node record.mjs
```

The default is a **free dry run**: it checks the local browser recorder without calling fal. To make one paid session, put `FAL_KEY=your-key` in a local `.env` file, which Git ignores, then run:

```powershell
node --env-file=.env record.mjs --live
```

The tool binds only to loopback, keeps the key server-side, authorizes proxy requests with a random per-run token, limits the proxy to Director, and admits at most one session per process. It records video and Japanese audio to `tmp/director/` at the repository root. It closes at the first of 70 reported generated seconds, 60 seconds of recording, or an 85-second watchdog. Starting the command again makes another paid attempt; do not use a retry loop. Browser limits are safeguards, not a provider-enforced dollar cap. In-flight work and the per-session minimum affect final billing.

## Assets and behavior

- `director-demo.json`: original 90-second planning brief and three branch prompts. The executable recorder uses the shorter limits above.
- `assets/aoi-cafe-opening.jpg`: opening reference assembled from the existing Aoi and café art.
- `assets/audio/`: three prerecorded Japanese TTS lines, mixed into the local recording. These are not Director-generated voices or a tested lip-sync implementation.
- `capture.js`: canvas captions, live WebRTC receive, recorder, buttons and scripted choice timing. Captions express the chosen intent when sent; generated action can follow later.
- `balance.mjs`: optional read-only billing check; requires a billing-capable key.

For production, synchronize captions with received scene timing, use richer dialogue, and build authenticated access and persistent billing controls before hosting paid generation for visitors.

## Pricing checked on 9 September 2026

The quoted standard launch rate is $0.02 per generated second with a $1.20 minimum. Seven reported 10-second chunks imply **$1.40**, not an invoice-confirmed charge. The billing endpoint rejected this key's read permission. The current advertised session ceiling is 15 minutes, subject to balance. Promotional pricing ends around 14 September; recheck the endpoint before another run.

Sources: [Director pricing](https://fal.ai/h3-max-director), [Director API](https://fal.ai/models/minimax/h3-max/director/api), [billing API](https://fal.ai/docs/platform-apis/v1/account/billing).
