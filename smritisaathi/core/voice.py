"""Voice layer: real TTS (pre-generated clips played offline via flet-audio) and real STT
(OS recogniser via flet-stt). Degrades gracefully on desktop where STT isn't available."""
import asyncio, re
from pathlib import Path
from core.speech_texts import clip_id

ASSET_AUDIO = Path(__file__).resolve().parent.parent / "assets" / "audio"
LOCALES = {"hi": "hi_IN", "mr": "mr_IN", "en": "en_IN"}

# ---------------- intent parsing (navigation by voice)
INTENTS = {
    "daily":     ["today", "daily", "smriti time", "आज", "आजचा", "आजचे", "स्मृति समय", "स्मृती वेळ", "aaj"],
    "games":     ["game", "play", "खेल", "खेळ", "खेलो", "खेळा", "khel"],
    "reminders": ["remind", "medicine", "tablet", "याद", "आठवण", "दवा", "दवाई", "औषध", "गोळी", "yaad"],
    "home":      ["home", "back", "main menu", "घर", "होम", "मुख्य", "वापस", "मागे"],
}


def _norm(s):
    s = (s or "").lower().translate(str.maketrans("०१२३४५६७८९", "0123456789"))
    return re.sub(r"[.,!?;:\"'()\[\]।॥-]", " ", s)   # keep Devanagari vowel signs (not \w in Python)


def parse_intent(candidates):
    if isinstance(candidates, str):
        candidates = [candidates]
    for c in candidates or []:
        t = _norm(c)
        for intent, words in INTENTS.items():
            if any(w in t for w in words):
                return intent
    return None


# ---------------- answering quiz questions by voice
NUMWORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "शून्य": 0, "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पाँच": 5, "पांच": 5, "छह": 6, "छः": 6, "सात": 7, "आठ": 8, "नौ": 9, "दस": 10,
    "दोन": 2, "पाच": 5, "सहा": 6, "नऊ": 9, "दहा": 10,
}


def match_option(candidates, options):
    """Return index of the option the person said, or None."""
    for c in candidates or []:
        toks = _norm(c).split()
        toks = [str(NUMWORDS[t]) if t in NUMWORDS else t for t in toks]
        text = " ".join(toks)
        for i, o in enumerate(options):
            on = _norm(o).strip()
            on = str(NUMWORDS.get(on, on))
            if on.isdigit():
                if on in toks:
                    return i
            elif on and on in text:
                return i
    return None


class Voice:
    def __init__(self, page=None):
        self.page = page
        self.audio = None
        self.stt = None
        self._stt_ready = None
        self.last_heard = ""
        if page is not None:
            try:
                import flet_audio as fa
                self.audio = fa.Audio()
                page.services.append(self.audio)
            except Exception as ex:
                print("[voice] audio unavailable:", ex)
            try:
                from flet_stt import FletStt
                self.stt = FletStt()      # service: must NOT be added to page.controls/overlay
            except Exception as ex:
                print("[voice] speech-to-text unavailable:", ex)

    @property
    def has_stt(self):
        return self.stt is not None and self._stt_ready is not False

    # ---- TTS
    def clip_path(self, text, lang):
        return f"audio/{lang}/{clip_id(lang, text)}.mp3"

    def speak(self, text, lang):
        """Fire-and-forget. Plays the pre-generated clip for `text`; silently skips unknown text."""
        if self.audio is None or self.page is None or not text:
            return
        rel = self.clip_path(text.strip(), lang)
        if ASSET_AUDIO.exists() and not (ASSET_AUDIO.parent / rel).exists():
            print(f"[voice:{lang}] (no clip) {text}")
            return
        self.page.run_task(self._play, rel)

    async def _play(self, rel):
        try:
            self.audio.src = rel
            self.audio.update()
            await self.audio.play()
        except Exception as ex:
            print("[voice] play failed:", ex)

    async def stop_speaking(self):
        try:
            if self.audio is not None:
                await self.audio.pause()
        except Exception:
            pass

    # ---- STT
    async def listen(self, lang, seconds=8):
        """Returns a list of candidate transcripts (best first) or None."""
        if self.stt is None:
            return None
        try:
            if self._stt_ready is None:
                self._stt_ready = bool(await self.stt.initialize())
            if not self._stt_ready:
                return None
            from flet_stt import SttResult
            await self.stop_speaking()
            fut = asyncio.get_running_loop().create_future()

            def on_result(e):
                r = SttResult(e)
                self.last_heard = r.text
                if r.final and not fut.done():
                    fut.set_result([r.text] + [a.get("text", "") for a in r.alternates if a.get("text")])

            def on_error(e):
                if not fut.done():
                    fut.set_result(None)

            self.stt.on_result, self.stt.on_error = on_result, on_error
            await self.stt.listen(locale_id=LOCALES.get(lang, "en_IN"), listen_for_seconds=seconds,
                                  pause_for_seconds=3, partial_results=True, listen_mode="confirmation")
            try:
                return await asyncio.wait_for(fut, seconds + 5)
            except asyncio.TimeoutError:
                await self.stt.stop()
                return None
        except Exception as ex:
            print("[voice] listen failed:", ex)
            return None
