"""Everything the app can say out loud. Used by tools/generate_audio.py and by Voice for lookups.
Yields (lang, display_text, spoken_text). Strings with {placeholders} are not pre-recorded."""
from core.i18n import S
from core.content import CK, PERSONAL_Q, DIGIT_WORDS
import hashlib


def clip_id(lang, text):
    return hashlib.sha1(f"{lang}|{text}".encode("utf-8")).hexdigest()[:12]


def speakable():
    seen = set()
    def emit(lang, shown, spoken=None):
        k = (lang, shown)
        if k not in seen:
            seen.add(k)
            return [(lang, shown, spoken or shown)]
        return []
    out = []
    for lang, strings in S.items():
        for key, text in strings.items():
            if "{" in text or key in ("app_name",):
                continue
            out += emit(lang, text, text.replace("✓", "").replace("•", ""))
        for d, w in enumerate(DIGIT_WORDS[lang]):
            out += emit(lang, str(d), w)
        for q, _, _ in CK[lang]:
            out += emit(lang, q)
        for q in PERSONAL_Q.values():
            out += emit(lang, q[lang])
    return out
