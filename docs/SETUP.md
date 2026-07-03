# AI Content Money Engine — n8n Setup Guide

A daily automation that uses **Claude** to write original content for your niche,
then delivers a ready-to-post draft to you (Telegram) and logs it to a spreadsheet.

**Honest framing:** this workflow does not "make money by itself." It removes the
daily grind of *creating* content so you can consistently post, build an audience,
and monetize (affiliate links, ad revenue, selling a service/product). The money
comes from *what you do with the output* — showing up every day is the part most
people quit. This automates that part.

---

## What the workflow does

```
Daily 9am  →  Config (your niche)  →  Pick topic + build prompt
           →  Generate with Claude  →  Parse into clean fields
           →  ├─ Send draft to Telegram (review & post)
              └─ Log to Google Sheet (content calendar)
```

Nodes:
1. **Daily Trigger** – runs every day at 09:00 (change the hour in the node).
2. **Config** – your niche, tone, platforms, affiliate link, and a `|`-separated topic list.
3. **Pick Topic & Build Prompt** – rotates through your topics so you never repeat the same day.
4. **Generate with Claude** – calls the Anthropic API and gets back structured content.
5. **Parse & Format** – turns Claude's JSON into `hook`, `post`, `hashtags`, `blog_intro`.
6. **Send Draft to Telegram** – you get the post on your phone to review and publish.
7. **Log to Google Sheet** – keeps a dated archive / content calendar.

---

## 1. Import the workflow

1. In n8n: **Workflows → top-right menu (⋯) → Import from File**.
2. Choose `n8n/ai-content-money-engine.json` from this repo.
3. You'll see 7 nodes. Some show a warning until you connect credentials — that's expected.

---

## 2. Add your Anthropic (Claude) key

1. Get a key at **console.anthropic.com → API Keys**. Add billing/credit.
2. In n8n: **Credentials → New → "Header Auth"** (`httpHeaderAuth`).
   - **Name:** `Anthropic API (x-api-key)`
   - **Header Name:** `x-api-key`
   - **Header Value:** your key (starts with `sk-ant-...`)
3. Open the **Generate with Claude** node → select this credential.

The workflow uses model `claude-opus-4-8` (highest quality). To cut cost, open the
node and in the JSON body change the model to `claude-sonnet-5` (cheaper) or
`claude-haiku-4-5` (cheapest). Everything else stays the same.

---

## 3. Add Telegram (to receive drafts)

1. In Telegram, message **@BotFather → /newbot**, follow prompts, copy the **bot token**.
2. Message your new bot once (say "hi") so it can message you back.
3. Get your **chat ID**: open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   in a browser after messaging the bot; find `"chat":{"id":...}`.
4. In n8n: **Credentials → New → "Telegram API"**, paste the bot token.
5. Open the **Send Draft to Telegram** node:
   - Select the credential.
   - Replace `REPLACE_WITH_YOUR_TELEGRAM_CHAT_ID` with your chat ID.

*Don't want Telegram?* Delete that node and connect **Parse & Format** to a Gmail /
Email node instead — same idea, drafts land in your inbox.

---

## 4. Add Google Sheets (optional archive)

1. Create a Google Sheet with a header row: `date | topic | hook | post | hashtags | blog_intro`.
2. In n8n: **Credentials → New → "Google Sheets OAuth2 API"** and connect your Google account.
3. Open the **Log to Google Sheet** node:
   - Select the credential.
   - Replace `REPLACE_WITH_GOOGLE_SHEET_ID` with your sheet's ID (the long string in its URL).

*Don't want Sheets?* Delete the node — the workflow still runs and sends Telegram drafts.

---

## 5. Configure your niche

Open the **Config** node and edit:
- `niche` – e.g. `home fitness for busy parents`
- `tone` – e.g. `friendly, science-backed`
- `platform` – where you post
- `affiliate_url` – your real affiliate/offer link (or leave the placeholder)
- `topics` – a `|`-separated list; add as many as you like, they rotate daily

---

## 6. Test, then activate

1. Click **Execute Workflow** (test run). Check that a draft reaches Telegram and a row lands in the sheet.
2. If Claude's output looks off, tweak the prompt in **Pick Topic & Build Prompt**.
3. When happy, toggle the workflow **Active** (top-right). It now runs every day at 9am.

---

## Turning output into income (the part that actually matters)

- **Post consistently.** The draft is ready daily — publish it. Consistency builds the audience.
- **One clear offer.** Affiliate product, your service, a digital product, or a newsletter. Put the link where it fits naturally.
- **Track what works.** Use the Google Sheet + your platform analytics to double down on top topics.
- **Scale later.** Add auto-posting nodes (X, LinkedIn, Instagram) only after you've confirmed the content quality manually for a couple of weeks.

## Cost & safety notes

- Each daily run is one Claude call (~a few cents on Opus, less on Sonnet/Haiku). Set a spend limit in the Anthropic console.
- The prompt tells Claude **not to invent statistics** — still review before posting; you are responsible for what you publish.
- Never hardcode your API key into the workflow JSON — keep it in n8n Credentials as described above.
