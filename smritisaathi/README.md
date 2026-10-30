# SmritiSaathi — Frontend (Python + Flet)

Voice-first, multilingual (Hindi / Marathi / English) cognitive game client + caregiver web dashboard.
Stack per the project report: **Flet** UI, **SQLite** offline store, **FastAPI** backend (next phase),
**TensorFlow Lite** adaptive engine (hook ready), Firebase Cloud Messaging (backend phase).

## Voice (Hindi / Marathi / English)
**Speaking (TTS) — offline.** Every prompt the app says (instructions, results, digits, quiz questions, ~73 per language) is
pre-generated once as an mp3 and shipped in `assets/audio/<lang>/`, then played with `flet-audio`.
```bash
pip install edge-tts
python tools/generate_audio.py --check   # confirm the 3 neural voices exist (hi-IN-SwaraNeural, mr-IN-AarohiNeural, en-IN-NeerjaNeural)
python tools/generate_audio.py           # needs internet once; re-run after you add/change any text
```
If you add new spoken text, add it via `core/i18n.py` or `core/content.py` and re-run the script; unknown text is skipped silently.

**Listening (STT).** `flet-stt` uses Android's Google speech recogniser with locales `hi_IN`, `mr_IN`, `en_IN`.
Mic dialog = voice navigation ("खेळ", "आठवण", "games"…); quiz games get an "answer by voice" button.
Typed fallback is always available. Offline recognition needs the language packs downloaded on the phone
(Android Settings → Google → Speech / offline speech recognition); otherwise recognition uses the cloud.
STT works on Android/iOS builds only, not desktop or web.

## Run
```bash
pip install -r requirements.txt
flet run main.py                      # patient app (desktop window; add --android / --ios to preview)
python seed_demo.py                   # optional: 14 days of fake data
flet run --web caregiver/dashboard.py # caregiver dashboard in the browser
flet build apk                        # Android build
```

## Layout
- `main.py`, `app.py` — entry, navigation, game sessions, daily battery flow
- `screens/patient.py` — language, home, game hub, intro/result, reminders, voice dialog
- `games/` — memory cards, digit span F/B, Knox cube, piano tiles, arrow sums, find-the-stars, recall; `REGISTRY` maps each game to its cognitive domains (Sec. 3.1)
- `core/` — `db.py` (schema = Table 4.2), `i18n.py`, `voice.py`, `adaptive.py`, `sync.py`, `theme.py`
- `caregiver/dashboard.py` — six-domain trends, activity, reminder compliance, alerts, add reminders

## Honest status / next steps
- **Voice**: implemented (see above) but untested on a real device — `flet-stt` is a young community package; test Hindi/Marathi recognition accuracy with elderly speakers.
- **Crossword / Karaoke**: shown as "coming soon" (both need research per the report).
- **Pygame**: the report lists Pygame for games; Pygame can't render inside Flet, so games are native Flet controls here.
- **Attention test, Arrow Sums, recall questions**: my interpretation — validate protocols and content with your clinical psychologists.
- **Adaptive engine**: rule-based now; `predict()` is where the TFLite model goes.
- **Sync**: posts unsynced rows to `POST {API}/api/sync`; implement in FastAPI next.
- Hindi/Marathi strings are my translations — have native speakers review.
