# MaxForge Lab — Builder Skill

A standalone, brandable **Claude skill** for turning ideas into working,
deployable automations — with a built-in prompt library for top-quality output.

**Loop:** reuse → create → validate → execute.
**Covers:** n8n workflows, standalone scripts (Python/Node/Bash), scheduled jobs,
API integrations — plus a prompt for every common revenue task.

> Honest by design: builds automation that does real work; never promises
> guaranteed income or outcomes.

## Install

Drop the skill into any project so Claude Code / claude.ai can load it:

```bash
# from your project root
cp -r maxforge-lab/.claude/skills/maxforge-builder .claude/skills/
```

Or use this repo directly as a project — the skill lives at
`.claude/skills/maxforge-builder/` and loads automatically.

## What's inside

```
.claude/skills/maxforge-builder/
├── SKILL.md                     # the skill definition
├── prompts/                     # one comprehensive prompt per task
│   ├── GUIDELINES.md            # global rules (read first)
│   ├── social-post.md  blog-article.md  content-repurpose.md
│   ├── cold-outreach.md  lead-qualify.md
│   ├── product-description.md  price-monitor-decision.md
│   ├── client-audit-report.md  proposal-quote.md
│   └── n8n-workflow-spec.md
├── scripts/
│   ├── run.py                   # generic executor (Python/Node/Bash)
│   └── n8n/                     # create / validate / deploy workflows
└── references/
    ├── marketplace.md           # reuse before building
    └── build-targets.md         # pick the right artifact
```

## Quick start

```bash
SKILL=.claude/skills/maxforge-builder

# 1. Create an n8n workflow from a spec
python3 $SKILL/scripts/n8n/create_workflow.py --spec spec.json --out wf.json

# 2. Validate it
python3 $SKILL/scripts/n8n/validate_workflow.py wf.json

# 3. Deploy live (or Import from File in the n8n UI)
export N8N_BASE_URL="https://your-instance.app.n8n.cloud"
export N8N_API_KEY="<n8n Settings → n8n API>"
python3 $SKILL/scripts/n8n/deploy_workflow.py wf.json --activate
```

For content/outreach/e-commerce/reporting, grab the matching prompt from
`prompts/`, fill the `{{variables}}`, and parse the strict JSON it returns.

## Branding

Rename freely — this is your MaxForge Lab package. To rebrand the skill name,
edit the `name:` and title in `SKILL.md`. To publish it as a Claude Code plugin
marketplace, add a `.claude-plugin/marketplace.json` pointing at this skill.

## License

MIT — see [LICENSE](LICENSE).
