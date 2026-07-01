# Technical Review Checklist (Correctness Pass)

Load this file during the **self-review stage** when at least one scene failed to render. Work through the checklist in order. For each item, either mark **OK** or describe the exact change needed (file line number, mobject name, animation name). Do not rewrite the whole script in the review — only the next turn's code-revision pass will rewrite code.

## Inputs you will have

- Current `video.py` source
- Per-scene execution logs (stdout + stderr) captured by `scripts/render_scenes.py`, including any `<!> Scene X timed out` markers
- The list of previous review notes (to avoid repeating yourself)
- Optional: representative frames extracted from scenes that *did* render (from `scripts/extract_frames.py`) — only treat these as secondary signals during a technical review

## Checklist

### A. Does the code even parse and import?

1. Valid Python 3.11 syntax. Any `SyntaxError` in logs points to the line to fix.
2. `from manim import *` on line 1. No missing import for NumPy / standard library symbols used below.
3. Every class name in the file matches a `class X(...)` definition (no typos between declaration and reference).

### B. Does each scene render end-to-end?

4. Every scene has a `construct(self)` method. No empty bodies.
5. No reference to undefined mobject names (common cause of `NameError` inside `self.play(...)`).
6. Mobjects used in `self.play(Transform(a, b))` must both exist and be the right subclass (`VMobject` family, not `Group` vs `VGroup` confusion).
7. Mobjects are added to the scene via `self.add(...)` or `self.play(Create(...))` before any animation targets them. Fix the ordering if a mobject is animated before it exists.
8. `self.play(...)` never receives an empty list or a non-Animation object.
9. `MathTex` / `Tex` strings are raw strings and LaTeX is syntactically valid. If logs show `LatexFailed`, locate the offending expression.

### C. Does it obey the write-system constraints?

10. One Scene per class. No aggregator class.
11. No external resource loaded from hardcoded path (`ImageMobject`, `SVGMobject`, `font_file=`, `add_sound`). If present, flag for removal or guard.
12. No runtime config mutation (`config.quality`, `config.pixel_height`, etc.).
13. No third-party imports outside Manim + NumPy + SciPy + stdlib. Flag and request removal.
14. Every scene has a visible title positioned at the top edge.

### D. Does the rendered result behave?

15. For the scenes that rendered, are there any overlapping elements visible in the extracted frames? Note which scene/timestamp.
16. Are any elements outside the visible frame (cut off at the edges)? Note which scene.
17. Did any scene hit the timeout (`<!> Scene X timed out`)? If so, the scene likely has an infinite updater loop or an extremely long `run_time`. Point to the cause.
18. Are there scene-ordering issues — e.g., Scene 2 assumes state that Scene 1 leaves, but the classes don't share state (they can't across `Scene` classes). Flag if code seems to depend on cross-scene state.
19. **Duration vs narration check (only when narration exists)**: for each rendered scene, compare actual duration (from the JSON report's `duration_seconds` field) against the target in `scenes.md`. If any scene deviates by more than 0.5s, flag as blocking: "Scene X: target 10.0s, actual 7.6s — adjust `run_time`/`self.wait()` values." Do not propose black-frame padding.

### E. Non-repetition

20. Do not restate any issue already covered in the **previous reviews** block unless the prior fix did not work. If a prior issue is now fixed, say so in one sentence and move on.

## Output format

Emit a Markdown document with the following exact headings, each followed by a bullet list (possibly empty). If empty, write `None — OK.`

```
## Blocking issues (must fix before next render)
- <scene> L<line>: <what is wrong> → <what to change>

## Correctness issues (will cause visible errors but not crash)
- ...

## Constraint violations (from write-system rules)
- ...

## Notes on previously reported issues
- "<short summary>": fixed / still present / partially fixed

## Verdict
- needs_revision: true  |  needs_revision: false
```

## Do NOT

- Do not propose external libraries, SVG / image / audio files, or any `pip install` suggestion.
- Do not propose `config.*` runtime changes; quality is controlled by the CLI.
- Do not propose "add more comments", "rename variables for clarity", or any non-functional cosmetic suggestion.
- Do not return rewritten code. Describe changes only; the next turn will revise the code.
