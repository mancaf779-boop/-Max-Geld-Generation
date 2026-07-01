---
name: tts-prompter
description: MUST read this skill BEFORE entering generate mode for text-to-speech (TTS) tasks. Covers prompt crafting framework, separating spoken text from style instructions, using markup tags vs natural language for emotions and non-speech sounds, and sizing narration text to fit a time budget.
---

# TTS Prompter

This skill provides the definitive framework for crafting high-quality Text-to-Speech (TTS) prompts. You MUST follow these guidelines when generating speech to ensure natural, expressive, and predictable audio output.

## 1. The Ultimate TTS Formula

To generate perfect audio, always construct your single input string using this formula:

**`{Language, Accent, and Situational Style Instructions}: {Emotionally Aligned Text (with local action tags only if needed)}`**

The most critical rule in TTS prompting is physically separating **"Director Instructions"** (how to speak) from the **"Script"** (what to say) using a colon (`:`).

**Core Alignment Rule:** The style instructions, the text content, and any tags should all point in the same direction. A scared-sounding instruction works best with text that actually sounds alarming.

### Multi-speaker Conversations

For dialogues, use the colon to separate the global instructions from the script, and also to separate speaker names from their lines:

```text
TTS the following conversation between Joe and Jane:
Joe: How's it going today Jane?
Jane: Not too bad, how about you?
```

## 2. Part 1: Style Instructions (Before the Colon)

The Style Instructions section is your primary tool for controlling the overall performance. **This part is NEVER spoken.**

**Mandatory Rule:** You MUST write the Style Instructions entirely in English, regardless of the target language being spoken. The model follows English instructions most reliably.

**Tip 1: Don't overspecify.** The model fills in gaps naturally. Leaving some room often produces more natural results than controlling every detail.

**Tip 2: Avoid naming real brands or real-person identities.** Phrasing like "Chanel-style" or "like a TikTok creator promoting her favorite brand" is the most common trigger of policy blocks. Describe the desired *style* in generic terms instead.

**Tip 3: Steer clear of sensitive content cues.** Prompts that touch on violence, sexual content, hate, self-harm, or illegal activities (per [Google's policy](https://policies.google.com/terms/generative-ai/use-policy)) can be silently blocked. Soften descriptors and remove explicit cues.

### 2.1 Controlling Language, Emotion, Tone & Accent

Provide a specific, situational description. Because the Style Instructions carry the highest weight in the model's generation logic, you MUST explicitly state the target language and accent here to ensure correct output.

If the Spoken Text contains a mix of languages (e.g., Japanese with English words), you MUST explicitly state this mixed-language requirement in the Style Instructions so the model knows to switch pronunciation rules dynamically.

*   ❌ **Weak:** `Speak in a scared way: I think someone is in the house.`
*   ✅ **Strong:** `You are hiding in a dark closet. Speak in English with a terrified, trembling whisper as if you are afraid of being caught: I think someone is in the house.`
*   **Language & Accent Example:** `Speak in Brazilian Portuguese with a standard São Paulo accent: Bem-vindo ao nosso programa de hoje.`
*   **Mixed Language Example:** `Speak in a mix of Japanese and English, with a professional and confident tone: 私たちの新しい製品は強力な AI capabilities を備えており、既存の workflow にシームレスに統合できます。`

*(Note: If you mention a conflicting language here, e.g., "Read as a Japanese boy" but the text is Portuguese, the model will output Japanese.)*

### 2.2 Emotion & Tone

To coax the model into making natural sounds without relying on tags, set up the prompt and provide "breath markers" in the text.
*   **Laughing:** `React to the text with an amused, genuine laugh before speaking: Hahaha, I did NOT expect that. Can you believe it!`
*   **Sighing:** `You are exhausted and frustrated. Start the sentence with a heavy, tired sigh: Oh man... I can't do this anymore.`

### 2.3 Pacing & Volume

Use the Style Instructions to force physical delivery changes:
*   **Pacing:** `Read this disclaimer extremely fast, like a radio commercial voiceover rushing through the terms and conditions: Availability and terms may vary. Check our website for details.`
*   **Volume:** `You are trying not to wake a sleeping baby. Whisper this entire sentence as quietly as possible: I think he finally fell asleep.`

## 3. Part 2: Spoken Text (After the Colon)

The Spoken Text contains the actual words to be synthesized. **This part IS spoken.**

**Mandatory Rule: Match the target language.** The Spoken Text MUST be written in the exact language(s) you want the model to speak. If you want Japanese, write in Japanese characters; if you want a mix of Japanese and English, write the text exactly as a mix of Japanese and English. Do not rely on the model to translate on the fly.

**Tip: Punctuation matters.** Commas, periods, and semicolons create natural pauses. Use them to help the model breathe.

**Tip: Write the words a person would actually say.** When you are composing the Spoken Text yourself (not just relaying user-provided text), avoid the tells of AI-written copy: stock openers, hedged qualifiers, and evenly-balanced sentence pairs. Real speech has contractions, sentence fragments, and uneven rhythm — that reads as more natural once synthesized than polished, symmetrical prose.

### 3.1 Using Markup Tags

You may use **Markup Tags** (words enclosed in brackets like `[sigh]`) inside the Spoken Text to inject specific, localized actions or style modifications.

**Golden Rule: Tags for precision, instructions for tone.** Use tags inside the Spoken Text when you need a specific moment (a laugh, a pause, a whisper). Use the Style Instructions before the colon to set the overall feel.

*(Note: There is no exhaustive, hardcoded list of tags. The model interprets any descriptive word in brackets. However, you MUST follow the rules below.)*

#### DO Use Tags For:

Place these tags **inside the Spoken Text** (after the colon). They will not be read as words.

1.  **Non-speech sounds:** `[sigh]`, `[laughing]`, `[uhm]`, `[cough]`, `[gasp]`, `[snorts]`
    *   *Example:* `Say the following casually: Well, [uhm], let me think about it. [sigh] I guess we have no choice.`
2.  **Local style shifts:** `[shouting]`, `[whispering]`, `[extremely fast]`, `[sarcasm]`, `[asmr]`
    *   *Example:* `Narrate the following: He looked at me and said, [shouting] 'Get out!'`
3.  **Pacing and pauses:** `[short pause]` (~250ms), `[medium pause]` (~500ms), `[long pause]` (~1000ms+)
    *   *Example:* `Read this like a game show host: The winner is... [long pause] ...John!`

#### DO NOT Use Tags For:

**NEVER use emotional adjective tags** (e.g., `[scared]`, `[curious]`, `[bored]`, `[excitedly]`) inside the Spoken Text.
*   *Why?* The TTS engine will literally read the word aloud (e.g., it will say the word "scared" before the sentence), ruining the audio.
*   *Solution:* Move emotional descriptions to the Style Instructions (before the colon).

## 4. Duration vs Faithfulness

TTS output duration is **not deterministic**: the model speaks at a rate it chooses, and you cannot tightly control physical seconds via prompt wording or rate tags.

- **Standalone TTS tasks with no explicit time limit** (the user just wants audio of a text): ignore duration concerns. Optimize for **reading the text fully and accurately** in the requested style.
- **Time-constrained tasks** (e.g., narration in `video-generator`, dubbing to a fixed clip, ad spots): use `scripts/narration_budget.py` to size the text against the budget before generating, and to decide how to reconcile any overrun after generation. It implements the `Rate`/`Unit` lookup from `references/language_catalog.md` and the reconciliation ladder below.

**Reconciliation ladder** (after measuring actual duration with `ffprobe`):
1. Under budget → extend the clip with a brief held frame instead of stretching audio.
2. 0–5% over → no action needed.
3. 5–12% over → trim leading/trailing silence first; if still over, apply `ffmpeg atempo` ≤1.12x.
4. 12–20% over → regenerate once (TTS output varies between calls).
5. >20% over → rewrite the text shorter and re-plan.

## 5. References: Voice & Language Selection

The `language_code` parameter acts only as an auxiliary hint to select the correct regional voice model (e.g., `en-US` vs `en-GB`). It does NOT force the output language.

### 5.1 Voice Catalog

The following 30 prebuilt voices are available. Each voice has a distinct character and timbre. Use this catalog to select the most appropriate voice for your scenario.

| Voice Name | Gender | Character / Timbre |
| :--- | :--- | :--- |
| **Zephyr** | Female | Bright |
| **Puck** | Male | Upbeat |
| **Charon** | Male | Informative |
| **Kore** | Female | Firm |
| **Fenrir** | Male | Excitable |
| **Leda** | Female | Youthful |
| **Orus** | Male | Firm |
| **Aoede** | Female | Breezy |
| **Callirrhoe** | Female | Easy-going |
| **Autonoe** | Female | Bright |
| **Enceladus** | Male | Breathy |
| **Iapetus** | Male | Clear |
| **Umbriel** | Male | Easy-going |
| **Algieba** | Male | Smooth |
| **Despina** | Female | Smooth |
| **Erinome** | Female | Clear |
| **Algenib** | Male | Gravelly |
| **Rasalgethi** | Male | Informative |
| **Laomedeia** | Female | Upbeat |
| **Achernar** | Female | Soft |
| **Alnilam** | Male | Firm |
| **Schedar** | Male | Even |
| **Gacrux** | Female | Mature |
| **Pulcherrima** | Female | Forward |
| **Achird** | Male | Friendly |
| **Zubenelgenubi** | Male | Casual |
| **Vindemiatrix** | Female | Gentle |
| **Sadachbia** | Male | Lively |
| **Sadaltager** | Male | Knowledgeable |
| **Sulafat** | Female | Warm |

### 5.2 Supported Languages

Read `references/language_catalog.md` for the full table of ~90 supported languages with their BCP-47 code, counting `Unit` (chars vs words), and empirically measured `Rate` (units/second). Use `scripts/narration_budget.py` rather than eyeballing the table when a hard duration budget is involved.

## 6. Resources

### scripts/narration_budget.py

Sizes narration text against a time budget and applies the reconciliation ladder from Section 4:

```bash
python3 scripts/narration_budget.py max-units en-US 12.5
python3 scripts/narration_budget.py count "This is my narration text" --language-code en-US
python3 scripts/narration_budget.py fits en-US 12.5 "This is my narration text"
python3 scripts/narration_budget.py reconcile 13.8 12.5
```

Can also be imported directly: `from narration_budget import max_text_units, count_units, reconcile`.
