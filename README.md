# Max-Geld-Generation

An n8n workflow automation that uses **Claude** to generate daily content for your
niche and delivers ready-to-post drafts — the repeatable routine behind building an
audience and monetizing it (affiliate, ad revenue, services, digital products).

> ⚠️ No automation *guarantees* income. This one removes the daily work of *creating*
> content so you can post consistently. The money comes from what you do with the output.

## Contents

| File | What it is |
|------|-----------|
| [`n8n/ai-content-money-engine.json`](n8n/ai-content-money-engine.json) | Importable n8n workflow |
| [`docs/SETUP.md`](docs/SETUP.md) | Step-by-step setup guide |

## Quick start

1. Import `n8n/ai-content-money-engine.json` into n8n (**Import from File**).
2. Add three credentials: Anthropic (Claude) API key, Telegram bot, Google Sheets (Sheets is optional).
3. Edit the **Config** node with your niche and topics.
4. Test it, then toggle **Active**. It runs daily at 9am.

Full instructions: **[docs/SETUP.md](docs/SETUP.md)**.

## The flow

```
Daily 9am → Config → Pick Topic → Generate with Claude → Parse
          → Telegram draft (review & post)
          → Google Sheet (content calendar)
```

Default model: `claude-opus-4-8` (swap to `claude-sonnet-5` / `claude-haiku-4-5` in the
Claude node to lower cost).
