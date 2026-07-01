# init, capture, skills

Scaffolding commands.

> **[CLAUDE CODE NOTE]** The `init` command documented below is **disabled by default in this setup** — every `npx hyperframes init` run re-pulls the full skill set from GitHub (the `--skip-skills` flag is neutered) and would overwrite these patched skills and re-enable disabled paid paths. **Do not run `npx hyperframes init`.** Scaffold a project manually instead: create the dir, `npm init -y`, `npm install hyperframes`, and add an empty composition HTML by hand (drop a `<video>.mp4` into the dir as `source.mp4` where the upstream `--video` flag is referenced; place a music file as needed where `--audio` is referenced). The `capture`, `add`, `lint`, `validate`, `inspect`, `preview`, `render` (local), `transcribe`, and `remove-background` commands remain usable. The `init` docs below are retained for reference only.

## init (reference only — disabled by default in this setup; scaffold manually instead)

```bash
npx hyperframes init my-video                                    # TTY: interactive wizard
npx hyperframes init my-video --example warm-grain               # pick an example
npx hyperframes init my-video --example blank --resolution portrait
npx hyperframes init my-video --video clip.mp4                   # with video file
npx hyperframes init my-video --audio track.mp3                  # with audio file
npx hyperframes init my-video --example blank --tailwind         # Tailwind v4 browser runtime
npx hyperframes init my-video --non-interactive --example blank  # CI/agents — flag-only
```

**Default depends on TTY**: in a terminal, the CLI prompts for example/options. Outside a TTY (CI, agents, piped output) it auto-switches to non-interactive and **requires `--example`** (the CLI errors with a usage example if missing). Pass `--non-interactive` to force flag-only mode even on a TTY.

Templates: `blank`, `warm-grain`, `play-mode`, `swiss-grid`, `vignelli`, `decision-tree`, `kinetic-type`, `product-promo`, `nyt-graph`.

Other useful flags:

- `--resolution` — preset: `landscape` (1920×1080), `portrait` (1080×1920), `landscape-4k`, `portrait-4k`, `square` (1080×1080), `square-4k`. Aliases: `1080p`, `4k`, `uhd`, `1080p-square`, `4k-square`.
- `--skip-skills` — **temporarily ignored**: `init` always checks AI coding skills against GitHub while the skills.sh registry catches up. To opt out (CI/tests), set the `HYPERFRAMES_SKIP_SKILLS=1` env var instead.
- `--skip-transcribe` — don't auto-transcribe `--audio` / `--video` with Whisper.
- `--model`, `--language` — Whisper model / language for the auto-transcription.

When using `--tailwind`, invoke the `hyperframes-core` (Tailwind reference) skill before editing classes or theme tokens. The scaffold uses Tailwind v4 browser runtime patterns, not Studio's Tailwind v3 setup.

When `--audio` or `--video` is supplied, `init` transcribes the file with Whisper. For voice/model selection see the `hyperframes-media` skill.

## capture

```bash
npx hyperframes capture https://stripe.com                  # scaffold from a website
npx hyperframes capture https://linear.app -o linear-video  # custom output directory
npx hyperframes capture https://example.com --json          # JSON output for agents
npx hyperframes capture https://example.com --skip-assets   # skip image/SVG download
npx hyperframes capture https://example.com --max-screenshots 12
npx hyperframes capture https://example.com --timeout 60000 # page-load timeout in ms
```

Captures a live URL as an editable HyperFrames project: screenshots become layered scenes, assets are downloaded locally, and the result is a normal project you can `lint` / `preview` / `render`. Use this when the user supplies a URL as the starting point for a video.

## skills

```bash
npx hyperframes skills    # install HyperFrames skills for AI coding tools
```

One-time setup that adds the HyperFrames skill pack (`hyperframes-core`, `-creative`, `-animation`, `-cli`, `-registry`, `-media`, plus the `product-launch-video` and `hyperframes` orchestrators) to the local AI coding environment so agents follow the framework conventions. Re-run after major HyperFrames upgrades.
