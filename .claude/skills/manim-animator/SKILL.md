---
name: manim-animator
description: Generate code-driven explanatory animation videos and precise vector graphics using the Manim engine. Use when the user requests mathematical visualizations, algorithm walkthroughs, scientific concept explanations, step-by-step derivations with LaTeX equations, or animations in the style of 3Blue1Brown — or explicitly mentions Manim, ManimCE, or ManimGL. Do not use for photorealistic AI video generation or standard timeline editing.
---

# Manim Skill

Manim is a Python engine for code-driven vector animation, created by 3Blue1Brown and forked into a community edition. This skill turns a user's idea into a final MP4 through seven stages. Most of the specialized knowledge lives in the `references/` tree and is loaded only when a stage needs it; keep this SKILL.md as the navigation map and workflow spine.

## Seven-stage workflow

Run these stages in order. Stages 4–6 form the iterative loop; stages 1–3 and 7 each execute once.

**Stage 1: Decide the framework.** Read `references/decision_tree.md` and pick ManimCE (default) or ManimGL. Record the choice and do not mix the two during the rest of the task. Return early if the task is actually a better fit for a different skill (avatar video, timeline editing, static charts).

**Stage 2: Install Manim (once per sandbox).** Run `bash scripts/setup.sh`. The script is idempotent; re-running is cheap. It installs the Pango/Cairo headers, build tools, Python headers, FFmpeg, and `pip install manim`. LaTeX is not installed by default; install `texlive-latex-extra texlive-fonts-extra texlive-science` on demand only if the scene uses `MathTex` / `Tex`.

**Stage 3: Plan the scenes.** For anything longer than a single short clip, read `references/composer/README.md` first and produce a `scenes.md` plan (overview, narrative arc, per-scene duration/purpose/visual elements/content/technical notes). While planning, also read `references/plugins.md` and, whenever a scene's topic matches a trigger in that file, record the required plugin in the scene's technical notes as `plugin: <name>`. **When the video includes narration, complete the audio-first workflow before finishing the plan:** generate **one audio clip per scene** with whatever text-to-speech tool or skill is available in the current environment (do not generate a single monolithic narration file), measure each clip's duration with `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 <file>`, and record the measured duration (not an estimate) in each scene's `Duration` field and the clip path in the `Audio Sync` section. These measured durations are the binding contract that stage 4 must honour in `run_time=` parameters. The plan is the single source of truth that stage 4 will turn into code. Skip this stage only when the user's request is already a precise scene specification.

**Stage 4: Write `video.py`.** Load `references/prompts/write_system.md` and obey every hard rule. Consult the rule files inside `references/manimce/rules/` (or `references/manimgl/rules/` for GL) only for the topics the current scenes actually touch. Use `references/manimce/examples/` as few-shot references when the task matches one. Start from `templates/quickstart.py` and expand. If stage 3 recorded any `plugin:` entries, place a single lazy-install block at the top of `video.py` exactly as shown in `references/plugins.md`; never add plugins to `scripts/setup.sh`.

**Stage 5: Render all scenes at low quality.** Run:

    python3 scripts/render_scenes.py --code output/video.py --out output/ [--timeout 120]

The script renders every Scene with `manim -ql --disable_caching` in a subprocess with a per-scene timeout, emits a single JSON report on stdout, and leaves the per-scene MP4s in `output/videos/<stem>/480p15/`.

**Stage 6: Self-review and revise.** Branch on the JSON report's `success_rate`:

- If any scene failed (`success_rate < 100`): load `references/prompts/review_technical.md`, review against code + per-scene `log_tail`, produce a structured review, then rewrite `video.py` with those fixes applied. Re-run stage 5.
- If all scenes passed (`success_rate == 100`): for each successful scene, extract a representative frame with `python3 scripts/extract_frames.py --video <mp4> --out output/frames/ --mode highest_density`. Load `references/prompts/review_visual.md`, review code + frames, apply polish revisions if the review's `needs_revision: true`, then re-run stage 5 once to confirm no regression.

Loop at most three times. Stop the loop when the review returns `needs_revision: false` or when the revision set is empty.

**Stage 7: Finalize.** Once stage 5 reports full success, perform a **pre-flight sync check** before finalizing: compare the total animation duration (sum of per-scene `duration_seconds` from the stage 5 JSON report) against the total narration duration (sum of per-scene audio clip durations from `scenes.md`). If the difference exceeds 1 second, return to stage 6 to adjust `run_time` and `self.wait()` values — do **not** pad with black frames or silence to compensate. Then run:

    bash scripts/finalize_video.sh output/video.py output/ output/final.mp4

This re-renders every Scene at 1080p60 (`manim -qh --write_all`) and concatenates the per-scene MP4s in source order with `ffmpeg -f concat -c copy`. When narration exists, also concatenate the per-scene audio clips in the same order and mix the combined narration (plus optional BGM) into `final.mp4` with ffmpeg. **When subtitles are needed** (default for any video with narration), generate them by running:

    python3 scripts/generate_subtitles.py --audio <scene1.wav> <scene2.wav> ... --out output/subtitles.srt

The script calls the OpenAI Whisper API with `timestamp_granularities=["word"]` on each per-scene clip, offsets timestamps to the concatenated timeline, groups words into readable cues, and writes a standard SRT file (plus a word-level JSON for debugging). Then mux the SRT into the final MP4:

    ffmpeg -y -i output/final.mp4 -i output/subtitles.srt -c copy -c:s mov_text output/final_sub.mp4

Return the absolute path of `final_sub.mp4` (or `final.mp4` if the user explicitly opts out of subtitles) as the task attachment.

## File map

    scripts/
      setup.sh              One-time sandbox install (pip install manim + apt deps).
      render_scenes.py      Per-scene `manim -ql` with timeout, JSON report.
      extract_frames.py     OpenCV frame extraction (highest_density or fixed_count).
      finalize_video.sh     `manim -qh --write_all` + ffmpeg concat.
      generate_subtitles.py Whisper word-level transcription → SRT (stage 7, when narration exists).

    references/
      decision_tree.md      Read in stage 1.
      plugins.md            Read in stage 3 (on-demand plugin trigger table and do-not-install list).
      prompts/
        write_system.md     Read in stage 4 (must-follow hard rules).
        review_technical.md Read in stage 6 when any scene failed.
        review_visual.md    Read in stage 6 when all scenes passed.
      composer/             Read in stage 3 (narrative planning skill).
      manimce/              Rule pack, examples, templates for Manim Community (default).
        rules/  (23 files)  Topic docs: scenes, animations, mobjects, latex, 3d, ...
        examples/ (7 files) Fully-runnable reference scenes.
        templates/ (3)      2D, camera-moving, 3D scene starters.
      manimgl/              Rule pack for ManimGL (only when decision_tree picks GL).
        rules/  (18 files)
        examples/ (75)      Large sample library, many 3B1B-style scenes.
        templates/ (4)

    templates/
      quickstart.py         Copy this to begin a new video.py.

## Key invariants (never violate)

ManimCE code and ManimGL code are mutually incompatible; the choice in stage 1 is final for the task.

Generated code must follow every hard rule in `references/prompts/write_system.md`. No external resource files, no runtime `config.*` mutation, no third-party imports beyond Manim + NumPy + SciPy + stdlib, **except** for Manim plugins explicitly authorized by `references/plugins.md`, which must be lazy-installed from inside `video.py`.

Do not use Manim plugins to duplicate capabilities already available to the agent through other tools or skills. TTS itself is always produced by whatever text-to-speech tool/skill is available in the current environment, never by a Manim plugin's built-in backend; the `manim-voiceover` plugin is allowed only in its local-audio-file mode to couple animation timing to pre-rendered narration audio, and all of its TTS backends remain disabled. Raster assets go through an image-generation tool/skill + `ImageMobject`. Background music goes through a music-generation tool/skill + ffmpeg. Word-level transcription for subtitles goes through the OpenAI Whisper API (`whisper-1` model, `timestamp_granularities=["word"]`) via `scripts/generate_subtitles.py`; do not use local ASR tools (whisper.cpp, etc.) for this purpose. The full deny-list is in `references/plugins.md`.

The same constraints appear in `references/prompts/review_technical.md` and `references/prompts/review_visual.md` — writer and reviewer share the same rulebook so the loop cannot diverge.

Stage 7 runs only after stage 5 reports full success. If stage 7 fails (e.g., a high-quality render exposes a latent bug), fall back to stage 6 once, then retry stage 7. Do not manually hand-edit the final MP4.

## Working with external media tools

Manim renders vector animation from code, but it does not generate raster images, speech, or music on its own. When a scene needs any of those assets, produce them with whatever image/speech/music generation tools or skills are available in the current environment first, then pass the saved file path into the Manim code (guarded per the no-external-resource exception in `references/prompts/write_system.md`).

When a scene needs a **raster image or icon** (logo, photograph, textured background) that cannot reasonably be reconstructed with Manim's vector primitives, use an available image-generation tool/skill to produce the PNG first, save it inside the task's working directory, and then load it with `ImageMobject(path)` in the scene code. Verify the path exists before using it.

When the final video needs **spoken narration**, always produce **one audio clip per scene** with an available text-to-speech tool/skill (do not generate a single monolithic narration file) and save each clip into the working directory with a name matching the scene (e.g., `scene1_hook.wav`, `scene2_definition.wav`). Two pipelines are then available depending on how tightly the animation must follow the narration:

- **Simple mux (default)**: measure each clip's duration with `ffprobe` in stage 3, record the measured durations in `scenes.md`, and feed them into scenes as parameters so each scene's total animation time (sum of all `run_time` + `self.wait()`) equals the corresponding clip's measured duration by construction. Concatenate the per-scene audio clips and mix into the final MP4 with ffmpeg in stage 7. **For subtitles**, run `scripts/generate_subtitles.py` in stage 7 to transcribe the per-scene audio clips with the OpenAI Whisper API (word-level timestamps) and produce an SRT file aligned to the concatenated timeline; then burn or mux the SRT into the final MP4 with ffmpeg. This path needs no plugin.
- **Per-line auto-stretch**: if the user wants every line of narration to drive the duration of its corresponding animation beat (and optionally wants auto-generated SRT subtitles), install `manim-voiceover` per `references/plugins.md` and pin its backend to the local WAV/MP3 files produced by the text-to-speech tool/skill. Never enable Azure / ElevenLabs / gTTS / CoquiTTS backends, and never install any `manim-voiceover-*` fork.

Do not hardcode `self.add_sound(...)` calls to files that have not yet been generated.

When the final video needs **original background music**, produce the track with an available music-generation tool/skill, save it into the working directory, and mix it in during finalization. Follow a music-prompting skill (if available) for prompt construction.

Always generate the media asset **before** writing the Manim code that references it, so the code can be written against a path that actually exists. Do not assume a file path will materialize later.
