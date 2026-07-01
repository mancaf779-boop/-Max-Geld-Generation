# Visual Review Checklist (Aesthetic Pass)

Load this file during the **self-review stage** only when **all scenes rendered successfully**. The goal now shifts from correctness (already done) to visual quality. Use the extracted frames (from `scripts/extract_frames.py`) as the primary signal; the code is a secondary signal.

## Guiding principle

> Minimal, elegant, modern. Most explanatory-animation failures are *too much motion* and *too much color*, not too little. Prefer restraint.

## Inputs you will have

- Current `video.py` source (now passing)
- All scene logs (should be clean at this stage)
- Representative frames for **every scene** — treat each frame as a mandatory review subject
- Previous review notes (to avoid repetition)

## Review each frame on these eight dimensions

For every frame you receive, write one short note per dimension. If the dimension is already handled well, write `OK`.

### 1. Composition & layout
- Is content centered, or intentionally off-center for emphasis? Not accidentally drifted?
- Is there enough whitespace? If the frame feels crowded, suggest `arrange(..., buff=0.5)` or scaling down a group.
- Does the title remain in a consistent top region across all scenes? If titles jump around, note that.
- **Frame boundary check**: verify no element is cut off at any edge. If the pixel aspect ratio is non-16:9, confirm that `config.frame_width / config.frame_height` equals `pixel_width / pixel_height`. A mismatch means the coordinate frame is wrong — flag as **blocking**; all layout will be incorrect regardless of element sizing.
- **Density check**: content should use the full frame, not cluster in one band. If one horizontal third of the frame is packed while another is mostly empty, the frame dimensions likely do not match the pixel output (letterboxing). Flag as blocking.

### 2. Visual hierarchy
- Is the most important element (the "aha" object) the largest or most saturated?
- Is secondary text (labels, axes, notes) visibly demoted in size/opacity?
- Flag any frame where every element competes equally for attention.

### 3. Color discipline
- Count distinct colors. If > 5, the palette is too busy — recommend merging.
- Are colors used semantically (same variable = same color across frames)?
- Is there sufficient contrast against the dark background? Very dark blues / purples on black are unreadable.

### 4. Motion & transitions
- Are scene-to-scene transitions smooth? Abrupt `FadeOut; FadeIn` between related content should become `Transform` or `ReplacementTransform`.
- Any animation that feels too fast (<0.5s `run_time`) to parse? Recommend lengthening.
- Any animation that feels too slow (>3s for a minor move)? Recommend shortening.
- Is there a natural pause (`self.wait(1)`) after reveals for the viewer to absorb?

### 5. Continuity
- Do mobjects that represent the same concept look the same across scenes (same color, font, size)?
- If an equation evolves across scenes, is each step a `TransformMatchingTex`-style morph rather than a restart?

### 6. Decorative restraint
- If there are decorative strokes, background grids, or gradients, are they subdued (stroke_width < 1.5, opacity < 0.3)?
- Flag anything that distracts from the pedagogical content.

### 7. Readability
- Font size of body text should be ≥ 28. Flag any `Text(..., font_size=...)` below that.
- LaTeX expressions: are spacing commands (`\,`, `\;`) used where needed? Any expression that renders cramped should get these.
- Line length of any single `Text(...)` should not exceed the frame width; wrap or break across mobjects otherwise.

### 8. Audio-animation sync (only when narration exists)
- Compare each scene's rendered duration (from the JSON report's `duration_seconds` field) against the target duration in `scenes.md`. If any scene deviates by more than **0.5 seconds**, flag as **blocking** — the viewer will hear narration misaligned with the visual content.
- If the total animation duration deviates from the total narration duration by more than **1 second**, flag as **blocking**.
- Do **not** propose black-frame padding or silence insertion as a fix. The correct fix is adjusting `run_time` and `self.wait()` values in the scene code to hit the target duration.

## Cross-scene polish

- **Opening scene**: Does it hook the viewer with a question, paradox, or concrete example before introducing formalism?
- **Closing scene**: Does it resolve / call back to the opening? Does it end with `self.wait(1)` so the final frame isn't cut off in YouTube thumbnails?
- **Consistent visual identity**: Title style, font, color scheme, and axis style should feel like one video, not six different authors.

## Output format

```
## Per-scene notes
### Scene: <ClassName>
- Composition: ...
- Hierarchy: ...
- Color: ...
- Motion: ...
- Continuity: ...
- Decorative restraint: ...
- Readability: ...
- Audio sync: ...

### Scene: <NextClassName>
...

## Cross-scene polish
- Opening hook: ...
- Closing resolution: ...
- Visual identity: ...

## Prioritized suggestions (top 5, highest-impact first)
1. ...
2. ...

## Verdict
- needs_revision: true  |  needs_revision: false
```

## Do NOT

- Do not propose external files, new dependencies, or plugins.
- Do not propose runtime `config` changes.
- Do not return rewritten code.
- Do not repeat previously addressed points without explicit evidence they're still unresolved.
- Do not be a perfectionist. If the video is already clean and minimal, answer `needs_revision: false` and stop.
