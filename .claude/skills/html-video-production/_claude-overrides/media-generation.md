# Claude Code Media Contract — Two-Tier Priority Model

This file is the single source of truth for **how speech, music, images, sound effects, and audio transcription are produced inside the `html-video-production` skill under Claude Code**. It overrides any conflicting media instructions in the bundled upstream HyperFrames skills under `references/`. Whenever an upstream file describes a different path (the `audio.mjs` / `resolve.mjs` orchestrators, HeyGen, ElevenLabs, Lyria, `npx hyperframes lambda`, etc.), the model below wins.

Claude Code is a CLI coding agent: it has no built-in "generate a voiceover" or "generate an image" tool. Media therefore comes from either (a) local, offline, open-source models bundled with the HyperFrames CLI, or (b) a paid third-party API the user has explicitly configured (an API key present in the environment). Never assume a provider is available — check for credentials/tools first, and always tell the user what you're about to call before spending money.

## The model in one screen

| Tier | What | When | Examples |
| --- | --- | --- | --- |
| **Tier 1 — Local open-source (default)** | `npx hyperframes tts` (Kokoro), `npx hyperframes transcribe` (whisper.cpp), `npx hyperframes remove-background` (U2-Net), bundled Pixabay SFX, local BGM generation (MusicGen/Lyria recipe) | **Default for all generative media.** Free, local, offline, no account needed. | Voiceover, word-level caption timing, subject cutout/matting, quick SFX, background score |
| **Tier 2 — User-configured paid API (opt-in only)** | HeyGen Starfish TTS, ElevenLabs TTS, OpenAI TTS/image/Whisper APIs, or any other provider the user names | Only when the user asks for a specific paid provider, or Tier 1 quality is insufficient for the deliverable and the user agrees to pay. Requires a credential the user has already set (e.g. `$HEYGEN_API_KEY`, `$ELEVENLABS_API_KEY`, `$OPENAI_API_KEY`) — **never prompt the user to paste a key into chat**, and never silently assume one is authorized just because it happens to be set in the shell. Ask first. | Higher-fidelity narration, HeyGen audio-library retrieval, cloud transcription |
| **Tier 3 — Hard prohibited** | `npx hyperframes init` skill auto-pull · `hyperframes lambda *` (paid AWS cloud render) | Never, regardless of credentials. | — |

> Why tiers and not a blanket ban: the CLI media subcommands (`tts` / `transcribe` / `remove-background`) run **local open-source models**, not paid cloud, so they are the safe, always-available default. Tier 2 exists because some users legitimately have a HeyGen/ElevenLabs/OpenAI account and want that quality — but Claude Code must never spend the user's money without them asking for it. The only absolute prohibitions are the two Tier-3 items.

---

## Tier 1 — Local open-source generation (the default path)

### Hard rules

1. **Narration / voiceover** → `npx hyperframes tts "<text>"` (Kokoro-82M, local). This is the default voice path, not a "last resort" — there is no native Claude Code TTS tool to prefer over it.
2. **Background music / underscore / stings** → local MusicGen/Lyria recipe (see `references/hyperframes-media/SKILL.md`) or the bundled Pixabay tracks. Never compose with ffmpeg synthesis or call a third-party music API without the user asking for it.
3. **Raster images / icons / product shots / textured backgrounds** not supplied by the user → ask the user for source images, or use `npx hyperframes remove-background` on user-supplied photos for cutouts. Claude Code has no local image-generation model bundled; if the composition truly needs a generated image and the user has no source asset, say so and ask whether to (a) use a registry icon/CSS shape instead, (b) source a stock/licensed image, or (c) call a Tier-2 image API they authorize.
4. **Word-level timestamps** → `npx hyperframes transcribe` (whisper.cpp, local) is the default. This works regardless of which tier produced the voice audio.
5. **Always generate the asset before referencing it** in HTML. No `<audio src>` / `<img src>` against a path that does not yet exist.

### The critical substitution: hand-write the ledgers only when bypassing the orchestrators

Upstream workflows call two scripts that can hit **paid cloud providers** when a credential is present:

- `references/hyperframes-media/scripts/audio.mjs` — unified TTS + BGM + SFX → `audio_meta.json`
- `references/media-use/scripts/resolve.mjs` — asset resolver → `.media/manifest.jsonl`

**These scripts are safe to run as-is under Claude Code** as long as no Tier-2 credential is set (`$HEYGEN_API_KEY`, `$ELEVENLABS_API_KEY`, etc.) — with nothing configured, they fall through to the same local engines (Kokoro TTS, MusicGen/Lyria BGM, bundled SFX) described above and write `audio_meta.json` / `.media/manifest.jsonl` themselves. Prefer running them over hand-writing the ledgers, since they already implement duration probing and word-timing capture correctly.

Only hand-write the ledger files if you generate assets by some other means (e.g. the user supplied their own voice recording, or you used a Tier-2 API directly instead of through the orchestrator). The schemas are below.

### `audio_meta.json` — hand-written (id-keyed; consumed by caption/assembly steps)

Place voice files at `assets/voice/<id>.wav`, BGM at `assets/bgm/track.wav`. The `words` array is the caption-timing source — fill it from a `transcribe` pass (preferred) or a Tier-2 transcription API.

```json
{
  "tts_provider": "hyperframes-tts-kokoro",
  "voice_id": "<the voice you used>",
  "bgm": { "path": "assets/bgm/track.wav", "volume": 0.15, "mode": "generate", "query": null, "duration_s": 12.3 },
  "bgm_pending": false, "bgm_provider": "local-musicgen", "bgm_pid": null, "bgm_log": null,
  "bgm_mode": "generate", "bgm_target_duration_s": 12.3, "bgm_seed_duration_s": null, "bgm_loop_count": null,
  "voices": [
    { "id": "01", "path": "assets/voice/01.wav", "duration_s": 3.2,
      "words": [ { "id": "w0", "text": "Hello", "start": 0.0, "end": 0.4 } ] }
  ],
  "sfx": [
    { "id": "01", "name": "whoosh", "file": "assets/sfx/whoosh.mp3", "source": "bundled-pixabay",
      "offset_s": 0, "duration_s": 0.8, "volume": 1 }
  ],
  "total_duration_s": 12.3
}
```

If a workflow expects subset merges (`audio.mjs --only tts,bgm,sfx`, `sync-durations`, `fetch-sfx`), just regenerate/patch the relevant keys of this same file by hand — the downstream steps only read the JSON, they do not require the script to have written it.

### `.media/manifest.jsonl` — hand-written (one JSON record per line)

When a workflow uses the `media-use` resolver, source or generate the image, save it under `.media/images/`, and append one line per asset. Directory map: `bgm→.media/audio/bgm`, `sfx→.media/audio/sfx`, `voice→.media/audio/voice`, `image|icon|brand→.media/images`, `video→.media/video`. IDs are `<type>_<NNN>` zero-padded. After appending, you may regenerate `.media/index.md` by hand or leave it — downstream reads the `.jsonl`.

```json
{ "id":"image_001", "type":"image", "path":".media/images/image_001.png", "source":"user-supplied", "description":"<intent>", "width":1920, "height":1080, "transparent":false, "provenance": { "provider":"user-upload", "prompt":null } }
```

### Speech details

- **Write `narration.txt` first** (the exact string passed to the TTS engine, with pronunciation fixes like "API" → "A P I"), separate from the human-readable `SCRIPT.md`. This makes voice re-generation trivial.
- **Use SSML** where the engine supports it, for pacing: `<break time="...ms"/>`, `<prosody rate/pitch/volume>`, `<emphasis>`.
- **Place the wav** with `data-duration="auto"` so HyperFrames reads true duration via ffprobe; or run `ffprobe -i narration.wav -show_entries format=duration -v quiet -of csv="p=0"` to declare it explicitly.

```html
<audio id="narration" data-start="0" data-duration="auto" data-track-index="2" src="assets/voice/01.wav" data-volume="1"></audio>
```

### Music details

- Decide **role** (underscore / lead bed / sting), **mood arc**, and **duration** (composition length + 0.5 s tail; local generation does not auto-trim).
- `data-volume` defaults: **0.10–0.20** under narration, **0.50–0.70** when music leads, **1.0** for stings.

```html
<audio id="bg-music" data-start="0" data-duration="auto" data-track-index="3" src="assets/bgm/track.wav" data-volume="0.15"></audio>
```

- For audio-reactive beats (`references/hyperframes-animation` / audio-reactive guidance), pre-extract amplitude data from any local `.wav`/`.mp3` with the bundled `extract-audio-data.py` script — it reads local files only and needs no network access.

### Image details

- **Source** user-supplied photos/screenshots/logos first; only reach for generation when nothing suitable exists and the user agrees to it.
- **Do NOT generate** for pure CSS/GSAP shapes, registry iconography (`hyperframes add <name>`), or charts (build those as live SVG/Canvas, not flat PNG).
- **Aspect ratio** matches the output frame: **16:9 (1920×1080)** or **9:16 (1080×1920)**; square only for an explicit Instagram-feed asset.
- Every image needs motion treatment (per the animation skill's motion principles) — never embed a raw flat image.

```html
<img id="hero" class="clip" data-start="0" data-duration="5" data-track-index="1" src="hero.png" />
```

---

## Tier 2 — User-authorized paid providers (opt-in, credential-gated)

Use these only when the user explicitly asks for a specific paid provider's quality/voice/catalog, or Tier 1 genuinely cannot deliver (e.g. a specific licensed BGM library). Confirm with the user before making the call, even if a key is already present in the environment — a key being set does not imply blanket permission to spend it on every task.

| Tool | Provider | Use it for |
| --- | --- | --- |
| HyperFrames audio engine w/ `$HEYGEN_API_KEY` set | HeyGen Starfish TTS + audio-library retrieval | Native word-timestamp TTS and licensed BGM/SFX retrieval, if the user has a HeyGen account and wants it |
| HyperFrames audio engine w/ `$ELEVENLABS_API_KEY` set | ElevenLabs TTS | Higher-fidelity narration when the user has an ElevenLabs account |
| OpenAI Whisper API | Cloud transcription | Word-level timestamps without whisper.cpp installed locally |

```python
from openai import OpenAI
client = OpenAI()
with open("assets/voice/01.wav", "rb") as f:
    t = client.audio.transcriptions.create(
        model="whisper-1", file=f,
        response_format="verbose_json", timestamp_granularities=["word"])
```

Convert `transcript.words` into the `{id,text,start,end}` shape used in `audio_meta.json`. Save as `transcript.json` for the caption step.

---

## Tier 3 — Hard prohibitions (never)

1. **`npx hyperframes init` skill auto-pull.** `init` re-fetches the latest skills from GitHub on every run (the `--skip-skills` flag is currently neutered upstream) and would overwrite this installed, patched skill directory. **Scaffold manually** (`npm init -y` + `npm install hyperframes` + hand-authored composition HTML). `npx hyperframes capture <url>` is fine — it does not re-pull skills.
2. **`hyperframes lambda *`** (deploy / render / progress / destroy / policies) — paid AWS cloud rendering. **Render locally** with `npx hyperframes render` (add `--docker --strict` for long/large jobs); it is CPU-bound but free and offline-safe.

---

## Cross-references

- [`modifications.md`](modifications.md) — every upstream file changed when packaging this skill, for Apache 2.0 §4(b).
- `references/hyperframes-media/` — upstream audio-engine docs (the `audio_meta.json` schema and the local-engine fallback chain).
- `references/media-use/` — upstream asset-resolver docs (the `manifest.jsonl` schema).
- `references/embedded-captions/`, `references/hyperframes-core/` — caption authoring and asset placement (consume the `words` timing produced above).
