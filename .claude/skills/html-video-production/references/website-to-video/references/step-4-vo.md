> [!IMPORTANT]
> **[CLAUDE CODE NOTE — read first.]** This file runs under the media contract in [`../../../_claude-overrides/media-generation.md`](../../../_claude-overrides/media-generation.md). By default, narration is produced by local `npx hyperframes tts` and background music by the local BGM generation recipe (Tier 1) — don't ask the user to choose a TTS/music provider (HeyGen / ElevenLabs / Artlist / etc.), and don't request or set `HEYGEN_API_KEY` / `ELEVENLABS_API_KEY`, unless the user has already told you they want a specific paid provider and have credentials configured. Word-level timestamps are obtained with the OpenAI Whisper API or `hyperframes transcribe` (Tier 2). Keep all timing / reconciliation / captions logic below as-is.

# Step 4: VO, Timing + Captions

## If Step 2 said "no narration"

Skip the TTS sections below. The storyboard already has beat durations planned based on pacing and rhythm — those become `data-start` and `data-duration` values directly in Step 5.

**Background music (local):** If the user supplied a track, use it; otherwise produce one with the local BGM generation recipe from the video's mood (Tier 1). Do **not** present a music-source menu (Artlist / Musicbed / Uppbeat / Pixabay / etc.). Note the resulting file path in the storyboard for Step 5 to wire into `index.html`. If music is intentionally skipped, the video uses bundled Pixabay SFX (`assets/sfx/`) only — confirm that's intentional.

Move to Step 5.

---

## Generate a test clip before full narration — calibrate timing first

Generate a short 2-sentence test clip NOW with local `npx hyperframes tts` using the script's opening lines, and measure its actual duration. Generated speech rarely matches the words-per-second estimate exactly, so if the test clip implies the full audio is more than ~15% off the planned duration, revise the storyboard beat timings before generating the full narration.

**Do this before committing to beat count and durations:** synthesize the first two sentences with `npx hyperframes tts`, measure the clip length, then `seconds ÷ words × total script words = estimated full audio length`.

If the estimate puts your video at ±15% of the planned duration, proceed. If it's more than 15% off, recalibrate the script length first:

- **Audio TOO SHORT** (more than 15% under planned duration) → add strategic pauses. In `narration.txt`, insert blank lines between paragraphs (≈0.6s each) or `...` between sentences (≈0.4s each). Aim for the pauses to land at storyboard beat boundaries so the silence feels intentional, not dead air.
- **Audio TOO LONG** (more than 15% over planned duration) → identify the beat in your storyboard with the highest words-per-second density. Cut one supporting sentence from THAT beat's lines — preserve the lead sentence (the one that names the beat's idea). Re-measure with another test clip before committing to full generation.
- **Audio matches plan but beat boundaries drift** → adjust the storyboard durations to match the actual narration, not the other way around. The audio is the ground truth once narration is generated.

The script formula assumes constant words-per-second, but punctuation, dramatic pauses, and silence cues all stretch real audio. Always trust a measured test clip over the formula.

## Background music

Add a subtle underscore by default — even with narration present, a quiet bed makes pauses feel intentional. Produce it with the local BGM generation recipe (Tier 1) from the video's mood, or use a user-supplied track. Do **not** present a music-source menu. Note the track in the storyboard for Step 5 to wire into `index.html`.

## Voice (local — no provider choice)

**[CLAUDE CODE NOTE]** Narration is always produced with local `npx hyperframes tts`. Do **not** ask the user to choose a provider, do **not** call HeyGen / ElevenLabs APIs, do **not** request or set any API keys, and do **not** run `npx hyperframes tts`. Pick or describe a voice via the local TTS engine's own voice parameters; if you want to compare voices, synthesize the first sentence of `SCRIPT.md` with two different `npx hyperframes tts` voice settings and keep the more natural one.

local `npx hyperframes tts` does **not** return word-level timestamps, so always obtain them in the dedicated transcription step below (Whisper API or `hyperframes transcribe`, Tier 2).

## Script length check

Before generating, verify the script makes sense for the video. Word count depends entirely on the creative direction. The storyboard's pacing and style determine how much narration the video needs.

The key check: are there stretches where NOTHING is happening — no narration AND no compelling visual movement? Those are dead spots that lose the viewer. Every second needs either spoken words or strong visual energy carrying it.

## Generate full narration

Generate the full script as `narration.wav` (or `.mp3`) in the project directory.

**If any command hangs for more than 60 seconds — don't just wait.** The user is sitting there watching you do nothing. Escalation order:

1. **Try again** — kill the process, run the same command again (transient failures are common)
2. **Try different flags** — smaller model (`--model tiny.en`), different voice, shorter test sentence first
3. **Try a different tool for the same task** — if `hyperframes transcribe` hangs, call the OpenAI Whisper API on the audio instead
4. **Re-synthesize** — regenerate the clip with `npx hyperframes tts` (a different voice or shorter test sentence first)

Never sit idle for 10 minutes hoping a stuck process will finish.

**Pronunciation of product names / tech terms:** if `npx hyperframes tts` mispronounces a name or acronym, spell it phonetically in `narration.txt` (the exact spoken string), e.g. `API` → `A P I`, `Vercel` → `Ver-sell`, `Supabase` → `Soopa-base`. Always synthesize the first two sentences as a test before generating the full audio, and avoid raw SSML tags in the spoken text.

**Also save the exact spoken text** — with pronunciation substitutions applied (e.g., `API` → `A P I`, `$2T` → `two trillion` and etc.) — as `narration.txt` in the same directory. This is the string passed to TTS, distinct from `SCRIPT.md` which is the human-readable creative doc. Having `narration.txt` makes it trivial to regenerate the audio later with a different voice without re-deriving the substitutions. Name it exactly `narration.txt`.

## Transcribe for word-level timestamps

local `npx hyperframes tts` does not emit word timestamps, so always transcribe the generated narration. Either path is fine:

```bash
# Tier 2 (local, offline) — whisper.cpp via the bundled CLI:
npx hyperframes transcribe narration.wav
```

or call the OpenAI Whisper API on `narration.wav` (per `../../../_claude-overrides/media-generation.md`). Either way, produce `transcript.json` with `[{ text, start, end }]` for every word. These timestamps are the source of truth for all beat durations.

## Map timestamps to beats

Go through STORYBOARD.md beat by beat. For each beat:

1. Find the first word of that beat's VO cue in `transcript.json`
2. Find the last word of that beat's VO cue
3. Set `beat.start = firstWord.start`, `beat.end = lastWord.end`
4. Add 0.3-0.5s padding at the end for visual breathing room

Update STORYBOARD.md with real durations. Replace estimated times (e.g., "0:00-0:05") with actual timestamps as precise as possible (e.g., "0.00-3.21s").

Beat boundaries land on word onsets — hard cuts to the VO.

## Timing reconciliation — required before Step 5

After mapping all beats, compare real total audio duration against the storyboard's planned duration:

```
real_total = last_word.end + cta_hold (typically 2–3s)
planned_total = sum of all beat planned durations
delta = |real_total - planned_total|
```

**If delta > 15% of planned total — do not proceed to Step 5 without resolving it.** Common causes and fixes:

- **Audio shorter than planned (most common with Kokoro):** Kokoro generates compressed speech with minimal pauses. Proportionally scale all non-CTA beat durations down to match the real audio. Example: planned 30s, audio 19s — multiply each beat duration by 19/30 (excluding the CTA hold). Update STORYBOARD.md.
- **Audio much longer than planned (>30% over):** The script was too long for the intended duration. Trim the script (remove one beat's VO), regenerate audio, re-transcribe.
- **CTA beat timing:** The CTA beat should hold for 2–3 seconds after the last spoken word — not extend to fill empty time. `cta_start = last_word.end + 0.3s`, `cta_duration = 2.5s`. Hard cap. Dead silence after the CTA hold loses the viewer.

**Always tell the user** if you adjusted durations significantly from the storyboard plan. They approved a specific beat structure — if it changed, they need to know.

## Captions

After the narration is generated and transcribed, ask the user:

> **Would you like captions on the video?**
>
> - **Yes** — per-word captions synced to the narration. Great for social media (most viewers watch on mute) and accessibility.
> - **No** — narration audio only, no text overlay.

If yes, captions are built as a separate composition (`compositions/captions.html`) in Step 5. The `transcript.json` drives the timing — each word appears/highlights as it's spoken. Read [the captions reference](../../hyperframes-media/references/captions/authoring.md) for styling options (scale-pop, typewriter, fade+slide, etc.) and positioning rules.

## Save timing data for Step 5

Record the final beat timings (start, duration) so Step 5 (Build) can use them when building `index.html`. The storyboard now has real timestamps — these become `data-start` and `data-duration` values on each scene slot when the root composition is assembled in Step 5.
