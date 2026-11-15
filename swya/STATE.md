# Survive Where You Are (SWYA) — series state & daily production guide

Owner: Roman (King Bob). Channel: TikTok @survivewhereyouare, YouTube @SurviveWhereYouAre.
The owner posts manually at **18:00 Kyiv** daily. The episode must be finished and sent to him **by 17:00 Kyiv**.

## Daily rule (owner, 14 Nov 2026)
If the owner has not sent the vote screenshot / instructions, the agent makes the next episode itself so it is ready by 17:00.
Before starting, check `swya/s1/eN/` for the next episode number N — if that folder already has the final mp4, the episode was already made in the main chat: do nothing.

## Votes — be honest
- Count votes only from real comments (screenshot from owner, or YouTube Studio / TikTok via Claude in Chrome if connected).
- If you could not read comments, continue the story with the option you think is best and **do not** claim viewers chose it (recap says what happened, without "the comments said").
- Never invent vote counts. Split votes → say "the comments were split" and use both ideas if possible.

## Series rules (owner feedback, keep)
- English, simple B1, worldwide audience. 1:20–2:00 per episode. Standalone: recap (≤10 s) woven into the start, **action in the first 2 seconds**.
- Voice: Speko `audio_synthesize`, voice **Fenrir**, model `gemini-3.8-flash-tts`, speed 0.95. Normal lines: "Calm, confident storyteller. Medium, steady pace, not rushed. Smooth continuous flow with only short natural pauses. Controlled and cool, never shouting." **Tense lines = whisper** ("Whisper. A quiet, breathy, tense whisper…"); deadly lines = "Low, dark, grave voice…".
- Structure: cold open → recap with yellow/red tags → numbered rule (paperTag) → events with tags → "On paper… One problem…" (3–4 s, no long lists) → Real fact → choice.
- Choice format 3: "So, what would you do? A… or B? Tell me in the comments. Part N+1 tomorrow." Both options must be risky; show the risk line on each card.
- Camera framing (owner, 15 Nov): every shot must SHOW the action — wide/medium shots where the people and what they do are visible. No shots blocked by shelves/walls/backs of heads, no random half-faces, no empty street views. Check stills for every clip before rendering.
- Models (owner, 15 Nov, E7 v2): no clipping — characters never stand/sit inside other bodies, blankets, furniture or door leaves; open doors fully out of the way; hair must fully cover the head (no skin spikes through hair — walker hair now scale 1.08/.7, offset y .07 z -.045). Women get long hair (`long:true`) so they read as female. Check close-ups in stills for this.
- People: blocky walkers WITH arms and dot eyes; group = NURSE, SUIT, KID, YOU (4 people). **No headphones / nothing on ears.** Phone screens must say who is writing (e.g. "Mom ❤️") and why there is signal.
- Ambient sound always (no silent scenes); music low; **NO continuous synthetic tones under the whole video (owner hated the looping car-alarm 'vuvuvu' in E6) — alarms/hums only as short distant moments (≤3 s), never a constant bed**; whispers in tense parts. Captions white with yellow/red highlights.
- Cover: `cover.py ep.html <t> "PART N" "LINE1" "LINE2" out.png` (series name + yellow PART pill + 2-line title).
- Export: 1440x2560 H.264 BT.709, AAC 256k, loudnorm −14 LUFS (mix.py does it).

## Story so far (Season 1: Zombies on the Subway)
1. S1E1 Subway car stops in tunnel, zombie hits the door, lock broken. Choice: run into tunnel / block door → comments: RUN.
2. S1E2 (v2) Chased into tunnel, hide in the dark, zombie runs past; kid trips near third rail; Mom texts "stations are full of them"; he's coming back. Choice: lights off & walk / hide in service room → 3/3 HIDE.
3. S1E3 Service room; bitten metro worker with keys. Choice: trust him / vent → split 1:1 (vent vs "cut off his arm").
4. S1E4 Worker gives keys, locks door behind them; crawl through vent above a station full of zombies; grate loose. Choice: drop & run to stairs / climb shaft → 3/3 CLIMB (one: "peek first").
5. S1E5 Climb to street, peek; car alarm pulls zombies away; 10 seconds; pharmacy vs bus (driver still in seat) → 4/4 PHARMACY.
6. S1E6 Pharmacy: shelves searched, nurse takes bandages/painkillers/antiseptic + inhaler for the kid; locked back door with note "We are not infected. Please don't knock." + "They lied."; car alarm stops, zombies turn back. Choice: knock on the locked door / barricade the front door and hide → comments not readable by the daily agent (no Chrome); agent chose KNOCK (not claimed as a vote).
7. S1E7 The Back Room: they knock; the lock turns; pharmacist ANA (white coat, metal bar) opens. Rule 7: "look at their hands first" — shaking but clean, no bites. Back room: water, food, radio, keys to her delivery van, alley door. Her BROTHER lies under a blanket, arm bandaged (blood). "He just has a fever." Nurse looks at the bandage, then at YOU, says nothing. Ending: he opens his eyes — yellow-green (turning). Zombies are gathered at the pharmacy front glass. Real fact: human bites get infected easily; every bite that breaks skin needs medical care. Choice: **leave her brother and take the van (risk: Ana has the keys) / take him with us and hope it's a fever (risk: if he turns, it's in the van)**. ← votes pending
Season plan: end at E8 (van escape through the alley, out of the city zone / to a safe place), then a long compilation video (cut recaps & choice cards, add "The comments chose: …" cards) and Season 2.

## Pipeline (repo `swya/pipeline/`)
Setup in a fresh machine: `mkdir -p ~/swya3d && cd ~/swya3d && cp -r <repo>/swya/pipeline/* . && npm i three@0.160.0` ; python deps: numpy, pillow, playwright (Chrome at /usr/bin/google-chrome or playwright chromium; flags already in rend.py). ffmpeg required.
1. Make `epN/` with `audio/a1.wav…`, copy `segs.py rend.py cover.py build.py mix.py ep.html` from the previous episode (or pipeline/). The html loads `../node_modules/three/build/three.min.js`.
2. Edit `T` in build.py (words wrapped in `*` are highlighted; must match audio), clip count and gaps → `python3 build.py` (writes tl.js + voice.wav).
3. Edit ep.html: sets are built in world space at different X offsets (car x=0, tunnel 60, room 120, vent/station 180, street 260 with pharmacy interior at local x 9..17; E7 added a back room at local x 17..21, z -14.2..-10.6 with hidden south wall for cutaway cameras, alley door on x=21, ANA + BRO walkers). `render(t)` = cameras + overlays per clip, `wT(clip,word)` gives word times.
4. Check stills: `python3 rend.py stills ep.html 3 20 40 …` and look at them. Fix dark/blocked shots.
5. Render: `nohup python3 rend.py video ep.html 0 <total> full.mp4 &` (2–3 s/frame → ~1.5–2.5 h). Start early.
6. `python3 mix.py` (don't name a variable `tl` — it breaks wT), cover, then mux:
   `ffmpeg -i full.mp4 -i mix.wav -map 0:v -map 1:a -vf "scale=1440:2560:flags=lanczos,format=yuv420p" -c:v libx264 -preset veryfast -crf 16 -maxrate 20M -bufsize 40M -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 256k -shortest swya_s1eN_<name>.mp4`
7. Commit to `swya/s1/eN/` (mp4, cover, ep.html, build.py, mix.py) and update this file (story + pending choice).
8. Send the owner: mp4 + cover + YouTube title/description + TikTok caption + first pinned comment.
