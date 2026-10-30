"""Pre-generate every spoken prompt as an mp3 (run once, online). Ships in assets/ so the app speaks OFFLINE.

    pip install edge-tts
    python tools/generate_audio.py --check      # verify the voices exist
    python tools/generate_audio.py              # generate all missing clips (hi, mr, en)
    python tools/generate_audio.py --lang mr --force
"""
import argparse, asyncio, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import edge_tts
from core.speech_texts import speakable, clip_id

# Neural voices (Microsoft Edge TTS). Confirm with --check; swap names here if you prefer other voices.
VOICES = {"hi": "hi-IN-SwaraNeural", "mr": "mr-IN-AarohiNeural", "en": "en-IN-NeerjaNeural"}
RATE = "-15%"        # slightly slower than normal speech for elderly listeners
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "audio"


async def check():
    voices = {v["ShortName"] for v in await edge_tts.list_voices()}
    for lang, v in VOICES.items():
        print(lang, v, "OK" if v in voices else "NOT FOUND — pick one of:",
              "" if v in voices else sorted(x for x in voices if x.startswith(lang + "-")))


async def main(langs, force):
    items = [x for x in speakable() if x[0] in langs]
    sem, manifest, done = asyncio.Semaphore(4), {}, 0

    async def one(lang, shown, spoken):
        nonlocal done
        cid = clip_id(lang, shown)
        manifest[f"{lang}/{cid}"] = shown
        path = OUT / lang / f"{cid}.mp3"
        if path.exists() and not force:
            return
        async with sem:
            for attempt in range(3):
                try:
                    await edge_tts.Communicate(spoken, VOICES[lang], rate=RATE).save(str(path))
                    done += 1
                    return
                except Exception as ex:
                    if attempt == 2:
                        print("FAILED", lang, shown, ex)
                    await asyncio.sleep(1.5)

    for l in langs:
        (OUT / l).mkdir(parents=True, exist_ok=True)
    await asyncio.gather(*(one(*x) for x in items))
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(items)} prompts, {done} newly generated -> {OUT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=list(VOICES), action="append")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    asyncio.run(check() if a.check else main(a.lang or list(VOICES), a.force))
