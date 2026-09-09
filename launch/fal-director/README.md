# Live Rewind Director — launch kit

This is the prepared 90-second launch demo for **Tomorrow, Once More**. It turns the existing illustrated Japanese-learning story into one continuous, viewer-directed H3 Max Director stream.

## Budget lock

| Item | Value |
| --- | ---: |
| Director launch price through 14 September 2026 | $0.02 / generated second |
| Minimum charge | 60 seconds / $1.20 |
| Planned recorded demo | 90 seconds / $1.80 |
| Retry reserve | 60 seconds / $1.20 |
| Recommended balance | **$3.00** |
| Selected resolution | 768p |

The browser must send `stop` and close the WebRTC session at 90 seconds. Do not rely on the account balance to cap the demo: it allows up to 150 seconds with $3 at the promotional rate.

## What is ready

- `assets/aoi-cafe-opening.jpg` is the exact first-frame reference. It combines the project's Aoi design and family-cafe scenery into a 16:9 opening shot.
- `director-demo.json` contains the world prompt, exact fal configure object, captions, three branch prompts, cost guardrail, and recording path.
- The three buttons teach a simple Japanese action while changing the next live story beat.

## API integration

Use `@fal-ai/client@alpha` and `@fal-ai/server-proxy@alpha`. The browser connects to a server-side `/api/fal/proxy` route and opens `minimax/h3-max/director` through WebRTC. Keep `FAL_KEY` only in the server environment; it must never be committed or placed in browser code.

Start the session with the `configure` object in `director-demo.json`, attach the incoming audio/video MediaStream to the player, and send a choice's `prompt` text as a `{ type: "prompt", prompt_version: 1, prompt: "..." }` message. Close the session at the 90-second timer.

## Caption and audio approach

Generated-video typography is unreliable for a learning product. Render `opening_captions` and the selected choice `caption` as HTML/CSS over the video: kana first, English directly below. For the launch recording, use Japanese TTS or a prerecorded Japanese dialogue track; Director accepts an `audio_url` at startup and on later prompts, so the stream can be conditioned on the exact audio. Keep caption text outside the video prompt.

## Launch proof

Record this route: opening → **Save the receipt** → **Call Misaki**. The recording demonstrates a supplied character frame, preserved café continuity, an audience choice, and a story change in one uninterrupted session. Pair it with the public repository and a short post tagging `@fal`.
