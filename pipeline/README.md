# Mr Fine production pipeline (rebuilt 7 Nov 2026)

Per episode folder (see ep2/):
1. Voice: Speko audio_synthesize, google-tts `gemini-3.8-flash-lite-tts`.
   Narrator + Mr Fine = voice `Puck`, instructions "Lively TikTok-style narrator, wide intonation, medium unhurried pace".
   Kid = `Zephyr` (instructed as 11-year-old boy), Mom = `Kore`. One clip per beat -> audio/*.wav.
2. `assemble.py`: phrase list per clip (must match silence segments from segs.py), places clips on a timeline,
   writes timeline.json (karaoke captions + speaker) and voice.wav. Then build timeline.js (envelopes for lip-sync).
3. `sfx.py`: synthesized music bed + SFX, ducked under voice -> mix.wav.
4. `scene.html`: SVG renderer, render(t). Layout: 1080x1920, red banner y474-646, 16:9 panel at y652, captions y1352.
   Mr Fine always on the LEFT (TikTok buttons cover the right).
5. `render.py video A B out.mp4` (playwright + Chrome, JPEG q92 -> x264 crf16, BT.709 tagged). Two halves in parallel.
6. Concat, add mix.wav, then upscale to 1440x2560 crf14 BT.709 for upload (YouTube gives higher quality to >1080p uploads).
