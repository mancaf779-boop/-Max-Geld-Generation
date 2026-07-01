# ManimCE vs ManimGL vs "Don't Use Manim"

This decision should happen **once per task**, immediately after understanding what the user wants. Record the choice (CE, GL, or decline) and stick with it; do not mix the two frameworks — their APIs are incompatible.

## When to decline Manim altogether

Return early and recommend a different skill if any of the following is true. Manim is the wrong tool for:

| Situation | Better tool |
|---|---|
| User wants a realistic-looking talking-head video, avatar, or film-style footage | avatar-video or text-to-video skills |
| User wants to edit existing video files (cut, splice, color-grade) | a video-editor skill, not Manim |
| User wants to assemble a website-to-video promo, with HTML compositions, registry blocks, or GSAP | `hyperframes-html-video-production` skill |
| User wants a timeline-based composition with draggable clips and live preview | HyperFrames or a DAW-style skill |
| User only needs a static chart or plot, not an animation | matplotlib / plotly via data-analysis skill |

## When to use ManimCE (Manim Community Edition) — the default

Choose ManimCE whenever the user's request matches any of the following. This is the correct choice for roughly 95% of Manim tasks:

| Signal | Example phrasing |
|---|---|
| Educational or explanatory content, any discipline | "Explain gradient descent", "Animate how a binary heap works", "Visualize Fourier series" |
| Math / algorithm / data-structure walk-through | "Show AVL rotations step by step" |
| Short-form social clip that uses code-driven precision | "30-second TikTok explaining why 0.999… = 1" |
| User wants something reproducible, shareable, or to integrate with plugins later | "Make a video I can hand off to someone else to edit" |
| User does not mention 3Blue1Brown or OpenGL or interactive development | — |

Import contract for ManimCE:
```python
from manim import *
```
Render contract: `scripts/render_scenes.py` and `scripts/finalize_video.sh` use ManimCE by default.

## When to use ManimGL (3Blue1Brown's version)

Switch to ManimGL **only when the user explicitly triggers one of these signals**. Otherwise keep ManimCE.

| Trigger | Typical phrasing |
|---|---|
| Explicit 3b1b visual style request | "Make it look like 3Blue1Brown", "I want that Grant Sanderson style" |
| Interactive REPL-style development | "I want to tweak the scene live", "give me `.embed()` so I can iterate", `checkpoint_paste()` |
| OpenGL-specific features | "custom GLSL shader", "volumetric lighting", "particle cloud you can only do in GL" |
| ManimGL-specific class names | `InteractiveScene`, `self.camera.frame`, `ShowCreation`, `Tex` (no `MathTex`) |
| User wants cutting-edge 3D that CE struggles with | "rotating 3D manifold with shader-based color field" |

Import contract for ManimGL:
```python
from manimlib import *
```
ManimGL is NOT installed by `scripts/setup.sh`. Install separately on demand:
```bash
sudo pip3 install manimgl
```
Render contract: `manimgl scene.py SceneName --write_file`. The scripts in this skill target ManimCE; for GL, follow `references/manimgl/rules/cli.md`.

## Incompatibility cheat sheet

If the user switches mid-task, you must translate, not mix. Common differences:

| Concept | ManimCE | ManimGL |
|---|---|---|
| Import | `from manim import *` | `from manimlib import *` |
| Math formula class | `MathTex(r"...")` / `Tex(r"...")` | `Tex(r"...")` (no separate `MathTex`) |
| Creation animation | `Create(x)` | `ShowCreation(x)` |
| Default scene base class | `Scene` | `Scene` (but `InteractiveScene` is preferred for development) |
| CLI command | `manim -qh file.py MyScene` | `manimgl file.py MyScene --write_file` |
| Interactive mode | not first-class | `-se`, `.embed()`, `checkpoint_paste()` |
| Plugin ecosystem | rich | virtually none |
| Config file | `manim.cfg` (INI) | `custom_config.yml` (YAML) |

## Recording the decision

Before writing any code, the agent should state internally (or in a visible note to the user) something like:

> Using **ManimCE** because the user asked for "an educational animation explaining gradient descent" — no 3b1b-style, interactive, or shader cues present.

Then open only the corresponding rule pack (`references/manimce/rules/` or `references/manimgl/rules/`) and ignore the other.
