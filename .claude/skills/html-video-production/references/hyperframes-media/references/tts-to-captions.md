# TTS → Captions

> **[CLAUDE CODE NOTE]** The upstream two-path provider logic (HeyGen vs ElevenLabs/Kokoro) does not apply here. There is **one** path: synthesize with `npx hyperframes tts`, then transcribe for word timing. Never run `npx hyperframes tts` or call HeyGen/ElevenLabs.

When no recorded voiceover exists, generate one with local `npx hyperframes tts` and obtain word-level caption timing by transcribing the generated audio:

```bash
# 1) Produce narration.wav locally with `npx hyperframes tts` (Tier 1).
# 2) Transcribe for word boundaries (Tier 2):
npx hyperframes transcribe narration.wav --model small.en   # English; pick --model/--language to match
```

Or call the OpenAI Whisper API on `narration.wav` instead of `hyperframes transcribe`. Either way you get `[{ text, start, end }]` per word; normalize to the `[{ id, text, start, end }]` shape the captions pipeline consumes, then use the caption references in `captions/`. See [`../../../_claude-overrides/media-generation.md`](../../../_claude-overrides/media-generation.md).
