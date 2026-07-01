> [!NOTE]
> **Claude Code adaptation note.** This skill is installed for Claude Code and runs under the media contract in [`_claude-overrides/media-generation.md`](../../_claude-overrides/media-generation.md). Where this file and the contract disagree, the contract wins. In particular:
> - **Skip the `npx hyperframes auth status` preflight** unless the user has explicitly asked to use a paid provider (HeyGen / ElevenLabs) and already has credentials configured. Otherwise proceed straight to local generation.
> - **`scripts/audio.mjs` and `media-use/scripts/resolve.mjs` are safe to run directly.** With no paid credential configured they fall through to local engines (Kokoro TTS, local BGM generation, bundled SFX) and write `audio_meta.json` / `.media/manifest.jsonl` themselves — no hand-writing needed. See the media contract (Tier 1) for the ledger schema if you generate assets by another means.
> - **Do not surface a TTS-provider choice** unless the user asked for one. Default voice path is local `npx hyperframes tts` (Kokoro).
> - **Never use `npx hyperframes init` (it auto-overwrites this installed skill directory) or `hyperframes lambda *` (paid cloud).** Scaffold manually; render locally.

---
name: hyperframes-registry
description: Install and wire registry blocks and components into HyperFrames compositions. Use when running hyperframes add, installing a block or component, wiring an installed item into index.html, or working with hyperframes.json. Covers the add command, install locations, block sub-composition wiring, component snippet merging, registry discovery, and authoring a new block or component to contribute upstream (idea → scaffold → validate → PR).
---

# HyperFrames Registry

The registry provides reusable blocks and components installable via `hyperframes add <name>`.

- **Blocks** — standalone sub-compositions (own dimensions, duration, timeline). Included via `data-composition-src` in a host composition.
- **Components** — effect snippets (no own dimensions). Pasted directly into a host composition's HTML.

## Quick reference

```bash
hyperframes add data-chart              # install a block
hyperframes add grain-overlay           # install a component
hyperframes add shimmer-sweep --dir .   # target a specific project
hyperframes add data-chart --json       # machine-readable output
hyperframes add data-chart --no-clipboard  # skip clipboard (CI/headless)
```

After install, the CLI prints which files were written and a snippet to paste into your host composition. The snippet is a starting point — you'll need to add `data-composition-id` (must match the block's internal composition ID), `data-start`, and `data-track-index` attributes when wiring blocks.

Note: `hyperframes add` only works for blocks and components. For examples, upstream uses `hyperframes init <dir> --example <name>` — but **[CLAUDE CODE NOTE]** `npx hyperframes init` is disabled here (it re-pulls/overwrites patched skills); instead copy the desired example out of `node_modules/hyperframes` (or the upstream `examples/` dir) into your manually-scaffolded project by hand.

## Install locations

Blocks install to `compositions/<name>.html` by default.
Components install to `compositions/components/<name>.html` by default.

These paths are configurable in `hyperframes.json`:

```json
{
  "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
  "paths": {
    "blocks": "compositions",
    "components": "compositions/components",
    "assets": "assets"
  }
}
```

See [install-locations.md](./references/install-locations.md) for full details.

## Wiring blocks

Blocks are standalone compositions — include them via `data-composition-src` in your host `index.html`:

```html
<div
  data-composition-id="data-chart"
  data-composition-src="compositions/data-chart.html"
  data-start="2"
  data-duration="15"
  data-track-index="1"
  data-width="1920"
  data-height="1080"
></div>
```

Key attributes:

- `data-composition-src` — path to the block HTML file
- `data-composition-id` — must match the block's internal ID
- `data-start` — when the block appears in the host timeline (seconds)
- `data-duration` — how long the block plays
- `data-width` / `data-height` — block canvas dimensions
- `data-track-index` — layer ordering (higher = in front)

See [wiring-blocks.md](./references/wiring-blocks.md) for full details.

## Wiring components

Components are snippets — paste their HTML into your composition's markup, their CSS into your style block, and their JS into your script (if any):

1. Read the installed file (e.g., `compositions/components/grain-overlay.html`)
2. Copy the HTML elements into your composition's `<div data-composition-id="...">`
3. Copy the `<style>` block into your composition's styles
4. Copy any `<script>` content into your composition's script (before your timeline code)
5. If the component exposes GSAP timeline integration (see the comment block in the snippet), add those calls to your timeline

See [wiring-components.md](./references/wiring-components.md) for full details.

## Discovery

Browse available items:

```bash
# Read the registry manifest
curl -s https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry/registry.json
```

Each item's `registry-item.json` contains: name, type, title, description, tags, dimensions (blocks only), duration (blocks only), and file list.

See [discovery.md](./references/discovery.md) for details on filtering by type and tags.

## Contributing a new block or component

To author a NEW registry item (caption style, VFX block, transition, lower third, or a reusable component) and ship it as an upstream PR — not install an existing one — follow the full idea → scaffold → build → validate → preview → ship workflow in [contributing.md](./references/contributing.md). Copy-paste starter templates (caption / VFX / component / `registry-item.json`) are in [templates.md](./references/templates.md).
