# Director run — 9 September 2026

- Model: `minimax/h3-max/director`, configured at 768p, 16:9, memory 12.
- One paid session, no paid retry. Server confirmed that the initial reference image was present.
- Seven chunk messages, indices 0–6, each requesting 10 seconds. Total returned playable duration: 61.125 seconds, including output that had not yet played when stopped.
- Final duration: 51.763 seconds. Export: H.264/AAC MP4 at constant 24 fps, 1280×800 including the external subtitle panel. Image area is scaled from the incoming stream.
- Prompt version 1: opening. Version 2: save receipt, applied at 17:44:07 UTC and represented in chunks 4–5. Version 3: call Misaki, applied at 17:44:25 UTC and represented in chunk 6.
- Stop: generated-duration limit at 17:44:30 UTC. The last received chunk had not played through, so the final phone-call action is not claimed as visible in the recording.
- Estimated generation cost: 70 × $0.02 = **$1.40**. This is an estimate based on received chunks, not billing verification. The billing endpoint returned 403 (key permission).
- Japanese TTS: three local voice files. English and kana rendered by the local app; no claim of Director speech accuracy or native-speaker review.
- Raw browser WebM emitted an Opus packet warning at the tail during conversion. The final MP4 passes a full FFmpeg decode without errors. Audio is present (peak -3.4 dB, average -26.6 dB, including deliberate silence between lines).
- Raw telemetry remains in ignored `tmp/director/events.json`; no key or private billing data is committed.

The images and video demonstrate the actual prototype. They do not demonstrate the entire N5–N4 curriculum, public hosted branching, or a granted fal credit award.
