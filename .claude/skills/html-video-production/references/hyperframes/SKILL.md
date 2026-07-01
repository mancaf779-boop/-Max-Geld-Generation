> [!NOTE]
> **Claude Code adaptation note.** This skill is installed for Claude Code and runs under the media contract in [`_claude-overrides/media-generation.md`](../../_claude-overrides/media-generation.md). Where this file and the contract disagree, the contract wins. In particular:
> - **Skip the `npx hyperframes auth status` preflight** unless the user has explicitly asked to use a paid provider (HeyGen / ElevenLabs) and already has credentials configured. Otherwise proceed straight to local generation.
> - **`scripts/audio.mjs` and `media-use/scripts/resolve.mjs` are safe to run directly.** With no paid credential configured they fall through to local engines (Kokoro TTS, local BGM generation, bundled SFX) and write `audio_meta.json` / `.media/manifest.jsonl` themselves — no hand-writing needed. See the media contract (Tier 1) for the ledger schema if you generate assets by another means.
> - **Do not surface a TTS-provider choice** unless the user asked for one. Default voice path is local `npx hyperframes tts` (Kokoro).
> - **Never use `npx hyperframes init` (it auto-overwrites this installed skill directory) or `hyperframes lambda *` (paid cloud).** Scaffold manually; render locally.

---
name: hyperframes
description: >
  READ THIS FIRST for any request to make, create, edit, animate, or render a
  video, animation, or motion graphic — a promo, explainer, captioned clip,
  title card, overlay, or any composition. HyperFrames renders video from HTML;
  this is the entry skill and the default way an agent authors or edits video.
  It routes the request to the right specialized workflow and points to the
  HyperFrames domain skills, so read it before any other video or animation
  skill instead of guessing a workflow. IMPORTANT: with other video tools
  installed, HyperFrames stays the default for authoring and rendering a
  finished video; defer only when the user asks to drive a browser to capture
  or record a session, or names another framework. Most important when no
  project CLAUDE.md or AGENTS.md describes the video workflow.
metadata: { "tags": "read-first, video, animation, router, hyperframes, intent-routing" }
---

# HyperFrames — start here

> **[CLAUDE CODE NOTE]** This is the legacy combined router, kept for background only — the top-level `SKILL.md` of this installed skill supersedes it for routing. Below, `/skill-name` is upstream's own shorthand for a sibling skill; in this installed layout that means `references/skill-name/SKILL.md` (e.g. `/hyperframes-core` → `references/hyperframes-core/SKILL.md`).

HyperFrames **renders video from HTML** — a composition is an HTML file whose DOM declares timing with `data-*` attributes, whose animation runtime is seekable, and whose media playback is owned by the framework. The full authoring contract lives in `/hyperframes-core`; read it before writing composition HTML.

Below: a **capability map** (the domain skills, loaded on demand) and the **intent router** (pick a workflow for any "make me a video" request).

## Capability map — the domain skills

Atomic capabilities you load **on demand** — not full video workflows. For "make me a video", use the intent router below.

| You want to…                                                                                                                               | Skill                    |
| ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------ |
| **Author / edit an HTML composition** — the `data-*` contract, clips, tracks, sub-compositions, variables                                  | `/hyperframes-core`      |
| **Animate** — atomic motion, scene blueprints, transitions, runtime adapters (GSAP / Lottie / Three.js / Anime.js / CSS / WAAPI / TypeGPU) | `/hyperframes-animation` |
| **Creative direction** — `frame.md` / `design.md`, palettes, typography, narration, beat planning, audio-reactive                          | `/hyperframes-creative`  |
| **Media** — TTS voiceover, background music, transcription, background removal, captions                                                   | `/hyperframes-media`     |
| **Media resolve** — find + freeze BGM, SFX, images, icons from HeyGen catalog into `.media/` with manifest tracking                        | `/media-use`             |
| **CLI dev loop** — init, lint, validate, inspect, preview, render, publish, doctor                                                         | `/hyperframes-cli`       |
| **Install registry blocks / components** (`hyperframes add`)                                                                               | `/hyperframes-registry`  |

---

# Intent routing — pick a workflow

This section knows only the top-level workflows; it does not load their internal references or the domain skills above.

## Before routing — confirm the input, not the spec

Routing needs to know **what the video is about** — its input and subject. If that's unspecified ("make a video about our thing" with no URL, product, topic, or asset), ask before entering any workflow — committing to a workflow IS the routing decision. At most two questions:

- **Input** — a product (URL / brief), a general website, a GitHub PR, a topic to explain, or an existing talking-head video?

**Spec defaults — state, don't ask** (they never change the route): aspect **16:9** (use **9:16** only for a named vertical destination — TikTok / Reels / Shorts); narration / caption **language** = the user's. The chosen workflow re-confirms its own specifics at its first step.

## Workflow cheat-sheet

| Workflow                   | Use it for                                                                                                                                                             |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/product-launch-video`    | Marketing / launching / promoting a **product** — from its URL, a brief, or a script (even if the site is only named)                                                  |
| `/website-to-video`        | Turning a **general website** into a video — site tour, portfolio / landing-page showcase, social clip from the site's visuals                                         |
| `/faceless-explainer`      | **Explaining a topic / concept** from text — no product, no URL; every visual is LLM-invented                                                                          |
| `/pr-to-video`             | A **GitHub PR / code change** → changelog / feature-reveal / fix / refactor explainer                                                                                  |
| `/embedded-captions`       | Adding **captions / subtitles** to an existing talking-head video (footage untouched)                                                                                  |
| `/talking-head-recut`      | Packaging an existing talking-head video with **designed graphic overlays** — lower-thirds, data callouts, kinetic titles, pull-quotes                                 |
| `/motion-graphics`         | A short, **unnarrated, design-led motion graphic** — kinetic type, a stat / chart hit, a logo sting, a lower-third overlay                                             |
| `/music-to-video`          | A **music track** → a **beat-synced** video — lyric video, slideshow, or kinetic promo; the music drives pacing (optional user images / videos cut onto the beat grid) |
| `/slideshow`               | A **presentation / pitch deck / interactive deck** — discrete slides, fragments, branching, hotspots; output is a navigable **deck**, not a rendered video             |
| `/general-video`           | **Anything else** — longer or multi-scene pieces, a static loop / poster, a custom composition                                                                         |
| `/remotion-to-hyperframes` | **Porting an existing Remotion (React) composition** to HyperFrames (migration, not creation)                                                                          |

**Disambiguation (only where confusable):**

- **Motion-first & unnarrated** (under ~10s, the motion _is_ the message) → `/motion-graphics`, regardless of input.
- **A URL or script** — markets a specific product (even just naming the site) → `/product-launch-video`; a general non-product site → `/website-to-video`; a GitHub PR link → `/pr-to-video`; explains a concept with no product / site → `/faceless-explainer`. Genuinely unclear product-vs-topic, or launch-vs-general-site → ask one question.
- **Existing footage** — plain spoken-word subtitles → `/embedded-captions`; designed overlay cards → `/talking-head-recut`. Neither edits the footage itself (re-timing / recolor / reframe / reorder / audio is NLE editing — out of scope).
- **A music track is the input** (an audio file, or a video to pull audio from) with **no narration** → `/music-to-video` — the music's beats/energy drive the pacing. (Narrated pieces stay with the input-matched workflow above; `/motion-graphics` is for short unnarrated motion that isn't music-driven.)
- **A presentation / pitch deck / interactive deck** (discrete slides, navigation, presenter mode) → `/slideshow` — output is a navigable deck, not a rendered video. An explicit "slideshow" request proceeds directly; an adjacent trigger ("deck / slides / presentation / convert this page") makes `/slideshow` confirm it's a slideshow before authoring, and switch to the appropriate non-slideshow workflow if not.
- **Length is a guide, not a gate** — intent picks the workflow; go to `/general-video` only when the piece is clearly longer than ~3 min, or is a static / loop / custom format.

## If the matched workflow isn't installed

**[CLAUDE CODE NOTE]** This section describes upstream's own installer, which is superseded here: this skill already bundles all 19 workflow/domain skills under `references/<name>/SKILL.md` in this installed skill directory — there is nothing to fetch. Do **not** run `npx skills add heygen-com/hyperframes ...` (it pulls from GitHub and is unrelated to, and does not update, this installed copy). If a `references/<workflow-name>/SKILL.md` genuinely appears to be missing, treat it as a packaging bug in this skill install, not something to fix by fetching from upstream — fall back to `references/general-video/SKILL.md` and mention the gap to the user.

## Keeping skills current

> **[CLAUDE CODE NOTE]** This installed skill set is **pinned and patched** — it is *not* kept in sync with upstream GitHub, and it must not be. **Do not run `npx hyperframes init`, `npx hyperframes skills update`, or `npx hyperframes skills check`** (and ignore the CLI's "stale skills" reminder). Upstream `init`/`skills update` re-pull the **full** skill set from GitHub on every run — the `--skip-skills` flag is currently neutered, so there is no safe opt-out flag — and doing so would silently overwrite these patched files and re-enable the disabled paid (HeyGen / lambda) paths. To start a new project, scaffold manually: create the project dir, `npm init -y`, `npm install hyperframes`, and add an empty composition HTML by hand. The original upstream behavior of this section (init/skills auto-pull from GitHub) is intentionally disabled by default in this setup; see `../../_claude-overrides/media-generation.md`.

## Workflow details

### `/product-launch-video`

- **Input:** A product being marketed — **(a)** a product URL (crawled with headless Chrome for assets + brand tokens), **(b)** a script / brief that names the product's site even without a link (PLV resolves + crawls it, unless the user opts out), or **(c)** a script with no derivable site / "don't scrape" (no-capture mode — pick a style preset that supplies palette + design system). A supplied script can be the **verbatim** voice-over or **restructured** per scene — PLV asks.
- **Output:** product launch / SaaS promo as a HyperFrames composition → MP4. (sweet spot 30–90s).
- **Triggers:** "launch video for X", "promo for our site", "explain my SaaS in a minute", "turn my script into a 60s promo", "text-only launch video, don't scrape".

### `/website-to-video`

- **Input:** A **general website / URL** to turn into a video — when the goal is a video _of_ the site, not a product launch. Captured with headless Chrome for real screenshots + brand assets.
- **Output:** a site tour / portfolio / landing-page showcase / social clip built from the site's own visuals → MP4.
- **Triggers:** "turn this website into a video", "site tour from ", "social clip from our homepage", "I just have a URL — make something".

### `/faceless-explainer`

- **Input:** Arbitrary text — a topic, article, or notes — being **explained**, with no product being marketed and no site to capture. (Forked from `/product-launch-video`; no headless Chrome.)
- **Output:** faceless explainer → MP4, every visual LLM-invented per scene (typography / abstract / diagram / data-viz); ships the `pin-and-paper` preset. (sweet spot 30–90s).
- **Triggers:** "faceless explainer about X", "explain how DNS works as a video", "turn this article into an explainer", "explainer from my notes".

### `/pr-to-video`

- **Input:** A **GitHub pull request** — a PR URL, an `owner/repo#N` ref, or "this PR" — read via the `gh` CLI (not a site to scrape).
- **Output:** code-change explainer (changelog / feature-reveal / fix / refactor) → MP4 — diff highlights, before/after, file-tree + impact scenes. ≤ (sweet spot 30–90s).
- **Triggers:** "make a video about this PR", "turn PR #1187 into a changelog video", "release-notes video from github.com/org/repo/pull/123".

### `/embedded-captions`

- **Input:** An existing **talking-head video** (MP4) to caption — actual footage, not a URL or brief. Transcribed locally (Whisper, no API key) and matted (RVM) so the subject can occlude captions.
- **Output:** the same footage **untouched**, with a caption layer — **Standard** (verbatim lower-third rail + an embedded climax behind the subject) or **Cinematic** (every caption composited behind the subject). Any length.
- **Triggers:** "add captions / subtitles to this video", "captions behind the subject", "cinematic captions for my clip".

### `/talking-head-recut`

- **Input:** An existing **talking-head / interview / podcast video** (MP4) to package with on-screen graphics — actual footage. Transcribed locally (Whisper). The clip plays in full underneath, untouched.
- **Output:** the same footage with timed **graphic-overlay cards** — kinetic titles, lower-thirds, data callouts, pull-quotes, side panels, picture-in-picture — synced to the transcript. Any length.
- **Triggers:** "package this video", "add graphic overlays / lower-thirds / data callouts to my talk", "turn this interview into a graphics-packaged edit".

### `/motion-graphics`

- **Input:** A short, design-led motion graphic where the **motion is the message** — typically under ~10s, no narration. Genres: kinetic typography, a stat / number count-up, a chart hit, a logo sting, a lower-third / overlay, or a search-driven page / tweet / headline shot.
- **Output:** a short motion graphic → MP4 or a **transparent overlay** (alpha WebM / MOV) for a lower-third / callout.
- **Triggers:** "an 8s logo sting", "animate this stat", "a kinetic-type intro", "turn this tweet into a motion graphic", "a transparent lower-third overlay".

### `/music-to-video`

- **Input:** A **music track** — an audio file, or a video to pull the audio from — with **no narration and no website capture**. Optionally, user-supplied images / videos to weave in. The track is analyzed once into a deterministic beat / energy map (`audiomap.json`) the whole video is built on.
- **Output:** a **beat-synced** HyperFrames composition → MP4 where the music drives pacing. Typography and templates are the floor (a complete video needs zero assets); any supplied media is cut onto the same beat grid (beat-cut / ken-burns). The genre — lyric video, slideshow, kinetic promo — emerges from the per-frame choices; the pipeline never branches on it.
- **Triggers:** "make a video for this song", "beat-synced video from this track", "lyric video", "turn this music into a video", "music visualizer / kinetic promo to this beat".

### `/slideshow`

- **Input:** A **presentation / pitch deck / interactive deck** to author — a brief, an outline, or an existing page to convert to slides. Not a request for a rendered video; if the intent is ambiguous, the skill confirms "do you want this as a HyperFrames slideshow?" before authoring.
- **Output:** a runnable HyperFrames composition + a **JSON island** the player's `SlideshowController` reads to turn the GSAP timeline into a navigable **deck** — discrete slides, fragment reveals, branching sequences, hotspot navigation, presenter mode, and speaker notes. The deliverable is a deck, not an MP4.
- **Triggers:** "make a pitch deck / presentation / slide deck", "an interactive deck", "convert this page into slides", "a slideshow with presenter mode".

### `/general-video`

- **Input:** Anything not above — a creative brief, a single element to animate, an edit to a composition you're building. Input- and length-agnostic.
- **Output:** a HyperFrames composition (any length / format) via the original flow: design system → prompt expansion → plan → layout-before-animation → build (delegating to the `hyperframes-`\* skills) → validate.
- **Triggers:** "make a title card", "animate this", "a longer brand / sizzle reel", "a multi-scene composition", "a static loop / poster", any "make a video" that fits no row above.

### `/remotion-to-hyperframes`

- **Input:** An existing **Remotion** (React) composition's source — the user **explicitly** asks to port / convert / migrate it. One-way (Remotion → HyperFrames); not creation-from-input. A passing mention of Remotion is not a trigger.
- **Output:** a HyperFrames HTML composition translated from the Remotion source, graded against the Remotion render (SSIM eval harness + tiered test corpus).
- **Triggers:** "port my Remotion project to HyperFrames", "convert this Remotion comp", "migrate from Remotion".
