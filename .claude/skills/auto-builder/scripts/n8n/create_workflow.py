#!/usr/bin/env python3
"""Generate an importable n8n workflow JSON from a small spec.

Emits the proven money-engine pattern:
  schedule -> config -> pick topic -> Claude (HTTP Request) -> parse -> Telegram

Usage:
  python3 create_workflow.py --spec spec.json --out my-workflow.json
  python3 create_workflow.py --out my-workflow.json   # uses defaults

Spec fields (all optional except nothing is required):
  name, niche, tone, platform, affiliate_url, topics (list[str]),
  model, trigger_hour, telegram_chat_id
"""
import argparse
import json
import sys
import uuid


def _id() -> str:
    return str(uuid.uuid4())


def build(spec: dict) -> dict:
    name = spec.get("name", "AI Content Money Engine")
    niche = spec.get("niche", "personal finance and side hustles")
    tone = spec.get("tone", "practical, motivating, no hype")
    platform = spec.get("platform", "X/Twitter and LinkedIn")
    affiliate = spec.get("affiliate_url", "https://your-affiliate-link.example/offer")
    model = spec.get("model", "claude-opus-4-8")
    hour = int(spec.get("trigger_hour", 9))
    chat_id = spec.get("telegram_chat_id", "REPLACE_WITH_YOUR_TELEGRAM_CHAT_ID")
    topics = spec.get("topics") or [
        "How to start a side hustle with $0",
        "Budgeting apps that actually work",
        "Passive income myths vs reality",
        "Turning a skill into freelance income",
    ]
    topics_str = " | ".join(topics)

    n_trigger, n_config, n_pick, n_gen, n_parse, n_tg = (
        _id(), _id(), _id(), _id(), _id(), _id()
    )

    prompt_js = (
        "const cfg = $input.first().json;\n"
        "const topics = String(cfg.topics || '').split('|').map(t => t.trim()).filter(Boolean);\n"
        "const dayIndex = Math.floor(Date.now() / 86400000);\n"
        "const topic = topics.length ? topics[dayIndex % topics.length] : 'a useful tip';\n"
        "const prompt = `You are a content writer for the niche: ${cfg.niche}.\\n`\n"
        "  + `Tone: ${cfg.tone}. Platforms: ${cfg.platform}.\\n`\n"
        "  + `Topic for today: \"${topic}\".\\n\\n`\n"
        "  + `Write original, non-generic content. Do NOT invent statistics.\\n`\n"
        "  + `If you reach a call-to-action you may reference: ${cfg.affiliate_url}\\n\\n`\n"
        "  + `Return ONLY valid minified JSON with keys: `\n"
        "  + `{\"hook\":\"\",\"post\":\"120-220 words\",\"hashtags\":\"5-8 tags\",\"blog_intro\":\"2-3 sentences\"}`;\n"
        "return [{ json: { topic, niche: cfg.niche, affiliate_url: cfg.affiliate_url, prompt } }];"
    )

    parse_js = (
        "const res = $input.first().json;\n"
        "let text = '';\n"
        "try { text = res.content[0].text; } catch (e) { text = ''; }\n"
        "text = text.trim().replace(/^```(?:json)?/i, '').replace(/```$/, '').trim();\n"
        "let data;\n"
        "try { data = JSON.parse(text); } catch (e) { data = { hook:'', post:text, hashtags:'', blog_intro:'' }; }\n"
        "const topic = $('Pick Topic & Build Prompt').first().json.topic;\n"
        "const date = new Date().toISOString().slice(0,10);\n"
        "return [{ json: { date, topic, hook:data.hook||'', post:data.post||'', hashtags:data.hashtags||'', blog_intro:data.blog_intro||'' } }];"
    )

    json_body = (
        "={{ JSON.stringify({ model: \"" + model + "\", max_tokens: 2000, "
        "messages: [ { role: \"user\", content: $json.prompt } ] }) }}"
    )

    return {
        "name": name,
        "nodes": [
            {
                "parameters": {"rule": {"interval": [{"field": "days", "triggerAtHour": hour}]}},
                "id": n_trigger,
                "name": f"Daily Trigger ({hour}:00)",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [-320, 300],
            },
            {
                "parameters": {
                    "assignments": {"assignments": [
                        {"id": "a1", "name": "niche", "value": niche, "type": "string"},
                        {"id": "a2", "name": "tone", "value": tone, "type": "string"},
                        {"id": "a3", "name": "platform", "value": platform, "type": "string"},
                        {"id": "a4", "name": "affiliate_url", "value": affiliate, "type": "string"},
                        {"id": "a5", "name": "topics", "value": topics_str, "type": "string"},
                    ]},
                    "options": {},
                },
                "id": n_config,
                "name": "Config",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3.4,
                "position": [-100, 300],
            },
            {
                "parameters": {"jsCode": prompt_js},
                "id": n_pick,
                "name": "Pick Topic & Build Prompt",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [120, 300],
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "https://api.anthropic.com/v1/messages",
                    "authentication": "genericCredentialType",
                    "genericAuthType": "httpHeaderAuth",
                    "sendHeaders": True,
                    "headerParameters": {"parameters": [
                        {"name": "anthropic-version", "value": "2023-06-01"},
                        {"name": "content-type", "value": "application/json"},
                    ]},
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": json_body,
                    "options": {},
                },
                "id": n_gen,
                "name": "Generate with Claude",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [340, 300],
                "credentials": {"httpHeaderAuth": {"id": "REPLACE_WITH_CREDENTIAL_ID", "name": "Anthropic API (x-api-key)"}},
            },
            {
                "parameters": {"jsCode": parse_js},
                "id": n_parse,
                "name": "Parse & Format",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [560, 300],
            },
            {
                "parameters": {
                    "chatId": chat_id,
                    "text": "=📅 {{ $json.date }} — {{ $json.topic }}\n\n{{ $json.hook }}\n\n{{ $json.post }}\n\n{{ $json.hashtags }}",
                    "additionalFields": {"parse_mode": "Markdown"},
                },
                "id": n_tg,
                "name": "Send Draft to Telegram",
                "type": "n8n-nodes-base.telegram",
                "typeVersion": 1.2,
                "position": [800, 300],
                "credentials": {"telegramApi": {"id": "REPLACE_WITH_CREDENTIAL_ID", "name": "Telegram Bot"}},
            },
        ],
        "connections": {
            f"Daily Trigger ({hour}:00)": {"main": [[{"node": "Config", "type": "main", "index": 0}]]},
            "Config": {"main": [[{"node": "Pick Topic & Build Prompt", "type": "main", "index": 0}]]},
            "Pick Topic & Build Prompt": {"main": [[{"node": "Generate with Claude", "type": "main", "index": 0}]]},
            "Generate with Claude": {"main": [[{"node": "Parse & Format", "type": "main", "index": 0}]]},
            "Parse & Format": {"main": [[{"node": "Send Draft to Telegram", "type": "main", "index": 0}]]},
        },
        "settings": {"executionOrder": "v1"},
        "pinData": {},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate an n8n money workflow JSON.")
    ap.add_argument("--spec", help="Path to a JSON spec file (optional).")
    ap.add_argument("--out", required=True, help="Output workflow JSON path.")
    args = ap.parse_args()

    spec = {}
    if args.spec:
        with open(args.spec, encoding="utf-8") as f:
            spec = json.load(f)

    wf = build(spec)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    print(f"Wrote {args.out} ({len(wf['nodes'])} nodes).")
    print("Next: validate it, then Import from File in n8n or run deploy_workflow.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
