# Modifications to Upstream HyperFrames Skills

This document records every change made to the upstream HyperFrames skill materials when packaging them as the `html-video-production` Claude Code skill (built on HyperFrames). Maintained per Apache License 2.0 §4(b) ("modified files must carry prominent notices stating that You changed the files").

## Provenance

- **Upstream project:** [`heygen-com/hyperframes`](https://github.com/heygen-com/hyperframes)
- **Upstream license:** Apache License 2.0 (preserved verbatim in `../UPSTREAM_LICENSE_APACHE-2.0.txt`)
- **Pinned upstream commit:** `c811a2750a2f9a242b764959e7509217f9943511`
- **Pinned commit date:** 2026-06-28
- **Packaging model:** Full coverage. All 19 upstream skills under `skills/` are redistributed under `references/` (the upstream `skills/<name>/` layout is flattened one level so that every skill sits directly at `references/<name>/`, preserving the upstream `../<sibling-skill>/` cross-links verbatim).
- **Immediate lineage:** This Claude Code build adapts an intermediate third-party repackaging of the same upstream materials that had been built for a different AI agent product. That intermediate build renamed nothing structurally but injected agent-specific media-routing instructions throughout every bundled `SKILL.md`. This build replaces those agent-specific instructions with Claude-Code-appropriate equivalents (see "Why these changes exist" below); it does not re-derive from the original upstream commit directly.

### Bundled upstream skills (19/19)

Domain skills: `hyperframes` (legacy router), `hyperframes-core`, `hyperframes-animation`, `hyperframes-creative`, `hyperframes-cli`, `hyperframes-registry`, `hyperframes-media`, `media-use`.

Workflow skills: `product-launch-video`, `faceless-explainer`, `pr-to-video`, `motion-graphics`, `embedded-captions`, `talking-head-recut`, `website-to-video`, `music-to-video`, `slideshow`, `general-video`, `remotion-to-hyperframes`.

## Why these changes exist

Upstream ships several third-party / paid media paths: the unified audio orchestrator `hyperframes-media/scripts/audio.mjs` and the asset resolver `media-use/scripts/resolve.mjs` both **prefer the paid HeyGen cloud API** when a `HEYGEN_API_KEY` is present and fall back to local engines (Kokoro TTS, MusicGen/Lyria BGM, bundled SFX) otherwise; the CLI exposes `tts`, `transcribe`, `remove-background` (local open-source models), and `lambda *` (paid AWS cloud render). Claude Code has no native media-generation tools of its own (no built-in "generate a voiceover" / "generate an image" call), unlike the agent this bundle was originally packaged for. These are governed by the **Two-Tier Priority Model** in [`media-generation.md`](media-generation.md):

- **Tier 1 (default):** local, free, offline open-source paths — `hyperframes tts` (Kokoro) for voice, local MusicGen/Lyria for BGM, `hyperframes transcribe` (whisper.cpp) for caption timing, `hyperframes remove-background` (U2-Net), and the bundled Pixabay SFX.
- **Tier 2 (opt-in, credential-gated):** a user-configured paid API (HeyGen, ElevenLabs, OpenAI, etc.) — only when the user asks for it and a credential is already present; Claude Code must not prompt for or assume authorization to spend money.
- **Tier 3 (hard-prohibited):** `npx hyperframes init` skill auto-pull and `hyperframes lambda *` (paid AWS cloud render).

The modifications below are the minimum required to (a) point every bundled skill at this contract, (b) remove product-specific plumbing that doesn't apply to Claude Code (a prior sign-in/offline gate for a different agent's credential store, that agent's internal notification tooling, that agent's sandbox filesystem conventions), (c) fix hardcoded paths and cross-references so the skill works no matter where it's installed, and (d) annotate modified files per §4(b). All other upstream content — the actual HyperFrames domain knowledge (composition contracts, GSAP animation, design system, CLI reference, registry blocks, caption engine, and all workflow guidance) — is preserved.

## Modified files (relative to skill package root)

### 1. Every bundled `references/<skill>/SKILL.md` (all 19)

- **"Claude Code note" callout** at the top of each `SKILL.md` (above the YAML frontmatter, replacing the prior agent-specific override banner). The callout: (a) points to `media-generation.md` as the controlling media contract; (b) says to skip the `npx hyperframes auth status` preflight unless the user wants a Tier-2 paid provider; (c) explains the Tier-1 local-first default and the Tier-2 opt-in path; (d) forbids `npx hyperframes init` and `hyperframes lambda *`.

### 2. `references/hyperframes-cli/SKILL.md`

- **Scaffold step (Workflow #1) rewritten** — the upstream instruction to run `npx hyperframes init my-video` (which re-pulls and overwrites installed skills on every run, with `--skip-skills` currently neutered) is replaced with a manual scaffold recipe (`npm init -y` + `npm install hyperframes` + hand-authored composition HTML). `npx hyperframes capture <url>` is explicitly still allowed because it does not re-pull skills.
- **Cloud render line (Workflow #7) rewritten** — the `npx hyperframes lambda render ...` option is replaced with a note that `hyperframes lambda *` is disabled (paid AWS cloud) and that long/large jobs should use local `render --docker --strict`.
- All other CLI command documentation (lint, validate, inspect, preview, render, doctor, browser, info, upgrade, skills, compositions, docs, benchmark, telemetry, and the `tts` / `transcribe` / `remove-background` subcommands) is preserved verbatim from upstream.

### 3. Workflow `SKILL.md` files that invoke the audio/asset orchestrators

Affected files: `references/faceless-explainer/SKILL.md`, `references/pr-to-video/SKILL.md`, `references/product-launch-video/SKILL.md`, `references/general-video/SKILL.md`, `references/motion-graphics/SKILL.md`.

- **Inline note markers** immediately before each command line that runs `node .../scripts/audio.mjs ...` or `node .../resolve.mjs ...`, clarifying these orchestrators are safe to run as-is under the Two-Tier model (they already fall back to local engines with no credential set) and pointing to `media-generation.md` for the ledger schema if generating media by some other means. The original upstream command lines are left intact beneath each marker.

### 4. Sign-in (`auth status`) preflight blocks rewritten in workflow bodies

Affected files: `references/product-launch-video/SKILL.md`, `references/faceless-explainer/SKILL.md`, `references/pr-to-video/SKILL.md`, `references/website-to-video/SKILL.md`, `references/music-to-video/SKILL.md`, `references/hyperframes-media/SKILL.md` (Preflight section), `references/hyperframes-media/references/bgm.md`, `references/hyperframes-media/references/tts.md`, `references/hyperframes-media/references/requirements.md`.

- The upstream **"Show sign-in status" / Preflight** passages — which run `npx hyperframes auth status` and relay HeyGen sign-in guidance — are annotated in place with a note: run the preflight only if the user wants a Tier-2 paid provider; otherwise skip straight to local Tier-1 generation (`hyperframes tts`, local BGM generation).

### 5. `npx hyperframes init` / `skills update` auto-pull rewritten in bodies

Affected files: `references/product-launch-video/SKILL.md`, `references/faceless-explainer/SKILL.md`, `references/pr-to-video/SKILL.md`, `references/music-to-video/SKILL.md`, `references/motion-graphics/SKILL.md`, `references/embedded-captions/SKILL.md` (two mentions), `references/hyperframes/SKILL.md` ("Keeping skills current" section, incl. `skills check` / `skills update`), `references/hyperframes-cli/references/init-and-scaffold.md` (top-of-file note + section heading).

- Every body instruction to scaffold via `npx hyperframes init` (and the router's `skills check` / `skills update` guidance) is annotated in place with a manual-scaffold recipe (`npm init -y` + `npm install hyperframes`), because `init` / `skills update` re-pull the full skill set from GitHub on every run (the `--skip-skills` flag is neutered) and would overwrite this installed skill directory.

### 6. TTS/BGM provider-choice prompts rewritten

Affected files: `references/website-to-video/SKILL.md` (Step 4 summary line), `references/website-to-video/references/step-4-vo.md` (banner rewritten; BGM-source menu, "TTS Provider" choice, HeyGen/ElevenLabs/Kokoro audition blocks, transcription branch, escalation + pronunciation notes), `references/hyperframes-media/references/tts-to-captions.md`.

- Passages that ask the user to pick a voice/music provider, or that document HeyGen/ElevenLabs REST calls and API-key setup, are annotated with the Tier-1/Tier-2 model: default to local `hyperframes tts`, only surface a provider choice if the user already indicated they have a paid account. Upstream provider-chain tables and engine details are retained beneath the note (not deleted) so the schemas remain documented.

### 7. Agent-product-specific plumbing removed

- References to a prior agent's internal user-notification tool and sandbox filesystem conventions (e.g. fixed absolute install paths under a specific home directory) are removed or replaced with Claude Code equivalents (plain progress narration in the assistant's own responses; paths relative to the skill's own directory, resolved via `references/<name>/SKILL.md` rather than an absolute path). No upstream domain-knowledge content was removed by this pass — only product-specific wrapper text.

## Bundled scripts left in place but governed by the contract

The upstream orchestrator scripts (`*/scripts/audio.mjs`, `media-use/scripts/resolve.mjs`, and their `lib/` providers, plus `assemble-index.mjs`, `captions.*`, `transitions.*`, `build-frame.*`, `analyze-beatgrid.py`, etc.) are redistributed **unmodified**. They are retained for two reasons: (1) their header comments document the exact `audio_meta.json` / `manifest.jsonl` schemas; (2) they are directly runnable — with no Tier-2 credential set, they already produce local-only output. The media-generating orchestrators are annotated by the inline markers above rather than edited, so future upstream re-syncs stay clean.

## Bundled assets

| Path | Source / License | Status |
| --- | --- | --- |
| `assets/sfx/*.mp3` (19 files) + `CREDITS.md` | Pixabay Content License (commercial-free, no attribution required), as shipped in upstream `hyperframes-media/assets/sfx/` | Copied to the package root `assets/` for Tier-1 direct use. |

## Excluded from the bundle (size compliance)

To keep the package lightweight while preserving **all instructional text**, the following **binary / demo / regenerable** files were stripped by the upstream packaging step this build inherited. None are needed to read or follow the skills; at build time the agent obtains real equivalents via `npm install hyperframes` (which pulls the framework, fonts, GSAP, and example assets into `node_modules/`).

- **Demo/illustrative binaries under `references/`**: images (`*.png/.jpg/.jpeg/.gif/.webp/.avif`), example renders (`*.mp4/.webm/.mov`), and duplicate SFX `*.mp3` copies. The HTML/Markdown that references them is preserved; only the heavy binaries are removed.
- **Bundled web fonts** (`*.woff2/.woff/.ttf/.otf`, e.g. `embedded-captions/modes/standard/fonts/files/`) and the generated `fonts.css`. Fonts are reinstalled with the framework; `build-fonts-css.cjs` is kept so the CSS can be regenerated.
- **Vendored `gsap*.min.js` copies** — GSAP is installed via npm; the `hyperframes-animation` skill documents its usage.
- **Canonical `assets/sfx/` at the package root is retained** (Tier-1, always allowed) so the SFX stay available offline without any external fetch.

## Added files

| Path | Purpose |
| --- | --- |
| `SKILL.md` (top-level) | Router: fidelity gate (reject photoreal-only requests → suggest a dedicated video-generation tool instead), intent dispatch across the 19 bundled skills, and the hard rules. Not derived from any single upstream file. |
| `_claude-overrides/media-generation.md` | Single source of truth for the Two-Tier Priority Model and the exact `audio_meta.json` / `.media/manifest.jsonl` schemas. |
| `_claude-overrides/modifications.md` | This file. |
| `LICENSE`, `NOTICE.txt`, `UPSTREAM_LICENSE_APACHE-2.0.txt` | Apache 2.0 license + upstream attribution. |
| `assets/sfx/` | Tier-1 Pixabay SFX (see above). |

## Re-syncing with future upstream releases

1. Bump the pinned commit at the top of this file.
2. Re-copy all 19 skills under `references/`, flattening the `skills/<name>/` layout one level and stripping heavy media binaries.
3. Re-apply the modifications above: (a) prepend the Claude Code note to every `SKILL.md`; (b) re-patch the two CLI lines; (c) re-run the inline-marker pass over the five orchestrator-invoking workflow files; (d) re-apply the body annotations in §§4–6; (e) re-check for any newly introduced product-specific plumbing (agent-internal tool names, absolute sandbox paths) and replace/remove it per §7.
4. Update the bundled-skill list and asset table if the upstream skill set changes.
5. Grep guards after re-sync: `grep -rn '/home/ubuntu'` and `grep -rniE 'notify_user'` should return nothing; `grep -rln -i manus` (excluding `LICENSE`/`NOTICE.txt`/`UPSTREAM_LICENSE_APACHE-2.0.txt`, and excluding "manuscript") should return nothing outside this file's provenance section.
