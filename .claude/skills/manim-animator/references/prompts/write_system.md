# Write-System Constraints for Manim Scene Code

Load this file **before writing any Manim Python code**. These are the hard rules that keep generated code renderable and aesthetically consistent. They are distilled from 3Blue1Brown's own guidance, the Manim Community best-practice skill pack, and empirical failure modes observed in LLM-driven Manim generation.

## Hard Rules (must follow)

1. **One Scene, one class.** Every visual unit is a separate `class` inheriting from `Scene`, `ThreeDScene`, or `MovingCameraScene`. Do **not** create an aggregator class that imports or calls other scenes.
2. **Each scene has a visible title at the top.** Use a `Text(...)` or `MathTex(...)` positioned with `.to_edge(UP)` (or equivalent). Content is laid out below the title.
3. **No overlapping elements.** Every mobject must be positioned so it does not overlap others unless overlap is itself the intended animation (e.g., intentional layering). Use `.next_to()`, `.shift()`, `arrange(...)`, `.to_corner(...)` instead of hardcoded absolute coordinates whenever possible.
4. **Respect the frame.**
   - The default frame is 14.222 × 8.0 (16:9 landscape). For non-standard aspect ratios (9:16 portrait, 1:1 square, 21:9 ultrawide, etc.), set **both** pixel and frame dimensions in `manim.cfg` — the `-r W,H` CLI flag only changes pixel output and does **not** change the coordinate frame, causing letterboxing:
     ```ini
     [CLI]
     pixel_width = 1080
     pixel_height = 1920
     frame_width = 8.0
     frame_height = 14.222
     ```
     Rule of thumb: keep `frame_width / frame_height` equal to `pixel_width / pixel_height`; the shorter axis gets `8.0`.
   - Size elements relative to the actual frame, not hardcoded values: single-line text width ≤ 85 % of `config.frame_width`; `Axes` `x_length` ≤ `config.frame_width - 1.5`; keep ≥ 0.5 units margin from every edge. Scale or wrap long text (use `Tex` with `\parbox` or split into multiple `Text` mobjects).
   - When the target ratio is not 16:9, render a one-shot diagnostic scene **before** writing content code to confirm `config.frame_width` and `config.frame_height` match intent.
   - Do not rely on off-screen anchor points.
5. **No external resource files.**
   - **Forbidden**: hardcoded paths in `ImageMobject("foo.png")`, `SVGMobject("bar.svg")`, `Text(..., font_file=...)`, `self.add_sound("x.mp3")`.
   - **Allowed exception**: the resource was generated or uploaded earlier in the same task and its absolute path is known. In that case, guard the call with `from pathlib import Path` + `assert Path(p).exists()`. No bare try/except hiding the failure.
6. **Do not mutate runtime config inside the code.** Forbidden: `config.quality = ...`, `config.pixel_height = ...`, `config.frame_rate = ...`, `config.output_file = ...`. Quality and output are controlled by the CLI invocation in `scripts/render_scenes.py` and `scripts/finalize_video.sh`, not by the script.
7. **Use only Manim Community + NumPy + SciPy + Python standard library by default.** Do not `import` any other third-party package without an explicit user request for a plugin (and even then, only plugins explicitly enabled by the skill's plugin mechanism).
8. **Imports sit at the top of the file.** `from manim import *` on line 1. No lazy or conditional imports inside `construct()`.
9. **Pacing matters.** Prefer `self.play(animation, run_time=...)` with explicit `run_time` for any non-trivial animation. Use `self.wait(N)` after major reveals so the viewer can read/absorb. Default `run_time` is often too fast for explanatory content. **When the video has narration**, each scene's total animation time (sum of all `run_time` + `self.wait()`) **must equal** the corresponding narration clip's `ffprobe`-measured duration recorded in `scenes.md`. Do not guess durations; use the measured values as the ground truth. Add a comment at the top of each scene class stating the target duration, e.g., `# Target: 8.23s (from scene1_hook.wav)`.
10. **Visual continuity over replacement.** Prefer `Transform` / `ReplacementTransform` / `TransformMatchingTex` / `.animate` over `FadeOut(a); FadeIn(b)` when the two objects are conceptually related.

## Preferred Patterns (strong recommendations)

- **Group and arrange.** Use `VGroup(...).arrange(DOWN, buff=0.5)` or `.arrange_in_grid(...)` to compose layouts. Avoid hand-tuning positions.
- **Color with intent.** Reuse a small palette (3–5 colors). Use `set_color_by_tex` or `set_color_by_tex_to_color_map` to color parts of equations semantically (variable = one color, constant = another).
- **LaTeX escaping.** In `MathTex(r"...")` always use a **raw string**. Double-escape backslashes when not raw (`"\\frac"`). Wrap each logical token in a separate argument when you need per-piece color or animation: `MathTex("x", "=", "y")`.
- **Camera for 3D.** In `ThreeDScene.construct()`, set `self.set_camera_orientation(phi=..., theta=...)` before adding 3D objects. Use `self.begin_ambient_camera_rotation(rate=0.1)` for slow reveal spins.
- **Updaters for reactive animation.** For animations where B must follow A, use `b.add_updater(lambda m: m.next_to(a, RIGHT))` plus a `ValueTracker` for parameter animation. Do **not** overuse updaters for things that `Transform` can express.
- **Scene ends clean.** Each scene should end with `self.wait(0.5)` minimum, and should not leave dangling animations. Use `self.clear()` or explicit `FadeOut(...)` before a scene-ending transition only if the next scene expects a blank stage.

## Anti-Patterns (must avoid)

- Using `print()` or `logging` inside `construct()` as a substitute for visible content.
- Importing `matplotlib`, `PIL`, or `opencv` to generate images and then feeding them to `ImageMobject`. If an image is needed, generate it as a Manim Mobject (e.g., reconstruct the chart with `Axes` + `plot()`).
- Using `subprocess` to shell out.
- Defining a `main()` that instantiates `Scene` and calls `.render()` manually. Scenes are rendered by the CLI.
- Hardcoding paths like `/home/user/...`, `C:\\...`, or assuming `manim` working directory.
- Putting a 10-minute script in one `Scene`. Break into multiple scenes of 10–60 seconds each.

## Output Contract

When asked to produce the final code, return a **single Python file** whose body consists only of:

1. `from manim import *` (and `import numpy as np` if needed)
2. One or more `class <Name>(Scene | ThreeDScene | MovingCameraScene):` definitions, each with a complete `construct(self)` method

No prose, no markdown fences, no driver code.

## Cross-Reference

Before writing code, consult these knowledge packs:

- `references/composer/` — to turn a vague idea into a scene-by-scene plan (`scenes.md`)
- `references/manimce/rules/` — Manim Community Edition rule pack (default choice, 23 topic files)
- `references/manimgl/rules/` — ManimGL rule pack (only when user explicitly wants 3Blue1Brown-style interactive/OpenGL workflow)
- `references/manimce/examples/` or `references/manimgl/examples/` — use as few-shot when the task matches
- `references/manimce/templates/` — starting skeletons for 2D / camera / 3D scenes
