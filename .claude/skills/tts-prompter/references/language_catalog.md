# TTS Language Catalog

The `Unit` and `Rate` columns are empirically measured speech rates for **video
off-screen narration** (documentary-style, steady pace). `Unit` is `chars` for
unspaced scripts (CJK, Thai, Lao, Burmese) and `words` for the rest. `Rate` is
the average number of units spoken per second of audio.

Under other delivery styles (excited announcer, ASMR whisper, news anchor,
etc.), actual rate can deviate by approximately ±25%. Voice choice has only a
minor effect (~±5%) on rate; pick the voice that best matches the role and do
not anchor on the calibration setup below.

*Calibration method (for reproducibility only, not a recommendation): TTS
engine default, voice `Charon`, prompt prefix "Read this as a documentary
narrator at a natural, steady conversational pace:", N=2 samples per language.*

See `../SKILL.md` section 4 ("Duration vs Faithfulness") for when to use these
rates and when to ignore them, and `scripts/narration_budget.py` for a
ready-made helper that applies the sizing formula and reconciliation ladder.

| Language | BCP-47 Code | Unit | Rate |
| :--- | :--- | :--- | :--- |
| Arabic (Egypt) | ar-EG | words | 1.3 |
| Bangla (Bangladesh) | bn-BD | words | 1.8 |
| Dutch (Netherlands) | nl-NL | words | 2.1 |
| English (India) | en-IN | words | 2.2 |
| English (United States) | en-US | words | 2.1 |
| French (France) | fr-FR | words | 2.2 |
| German (Germany) | de-DE | words | 2.1 |
| Hindi (India) | hi-IN | words | 2.1 |
| Indonesian (Indonesia) | id-ID | words | 1.6 |
| Italian (Italy) | it-IT | words | 1.9 |
| Japanese (Japan) | ja-JP | chars | 4.2 |
| Korean (South Korea) | ko-KR | chars | 3.8 |
| Marathi (India) | mr-IN | words | 1.6 |
| Polish (Poland) | pl-PL | words | 1.7 |
| Portuguese (Brazil) | pt-BR | words | 1.7 |
| Romanian (Romania) | ro-RO | words | 1.6 |
| Russian (Russia) | ru-RU | words | 1.5 |
| Spanish (Spain) | es-ES | words | 1.8 |
| Tamil (India) | ta-IN | words | 1.3 |
| Telugu (India) | te-IN | words | 1.3 |
| Thai (Thailand) | th-TH | chars | 7.2 |
| Turkish (Turkey) | tr-TR | words | 1.6 |
| Ukrainian (Ukraine) | uk-UA | words | 1.5 |
| Vietnamese (Vietnam) | vi-VN | words | 2.7 |
| Afrikaans (South Africa) | af-ZA | words | 2.0 |
| Albanian (Albania) | sq-AL | words | 2.1 |
| Amharic (Ethiopia) | am-ET | words | 1.2 |
| Arabic (World) | ar-001 | words | 1.3 |
| Armenian (Armenia) | hy-AM | words | 1.5 |
| Azerbaijani (Azerbaijan) | az-AZ | words | 1.6 |
| Basque (Spain) | eu-ES | words | 1.7 |
| Belarusian (Belarus) | be-BY | words | 1.5 |
| Bulgarian (Bulgaria) | bg-BG | words | 1.8 |
| Burmese (Myanmar) | my-MM | chars | 11.2 |
| Catalan (Spain) | ca-ES | words | 2.2 |
| Cebuano (Philippines) | ceb-PH | words | 1.9 |
| Chinese, Mandarin (China) | cmn-CN | chars | 2.8 |
| Chinese, Mandarin (Taiwan) | cmn-tw | chars | 2.7 |
| Croatian (Croatia) | hr-HR | words | 1.7 |
| Czech (Czech Republic) | cs-CZ | words | 1.8 |
| Danish (Denmark) | da-DK | words | 2.1 |
| English (Australia) | en-AU | words | 2.2 |
| English (United Kingdom) | en-GB | words | 2.1 |
| Estonian (Estonia) | et-EE | words | 1.6 |
| Filipino (Philippines) | fil-PH | words | 1.7 |
| Finnish (Finland) | fi-FI | words | 1.2 |
| French (Canada) | fr-CA | words | 2.2 |
| Galician (Spain) | gl-ES | words | 1.9 |
| Georgian (Georgia) | ka-GE | words | 1.4 |
| Greek (Greece) | el-GR | words | 1.6 |
| Gujarati (India) | gu-IN | words | 1.8 |
| Haitian Creole (Haiti) | ht-HT | words | 2.6 |
| Hebrew (Israel) | he-IL | words | 1.5 |
| Hungarian (Hungary) | hu-HU | words | 1.8 |
| Icelandic (Iceland) | is-IS | words | 1.4 |
| Javanese (Java) | jv-JV | words | 1.7 |
| Kannada (India) | kn-IN | words | 1.2 |
| Konkani (India) | kok-IN | words | 1.6 |
| Lao (Laos) | lo-LA | chars | 8.2 |
| Latin (Vatican City) | la-VA | words | 1.3 |
| Latvian (Latvia) | lv-LV | words | 1.4 |
| Lithuanian (Lithuania) | lt-LT | words | 1.4 |
| Luxembourgish (Luxembourg) | lb-LU | words | 2.0 |
| Macedonian (North Macedonia) | mk-MK | words | 1.7 |
| Maithili (India) | mai-IN | words | 2.1 |
| Malagasy (Madagascar) | mg-MG | words | 1.8 |
| Malay (Malaysia) | ms-MY | words | 1.6 |
| Malayalam (India) | ml-IN | words | 1.2 |
| Mongolian (Mongolia) | mn-MN | words | 1.6 |
| Nepali (Nepal) | ne-NP | words | 1.4 |
| Norwegian, Bokmål (Norway) | nb-NO | words | 1.7 |
| Norwegian, Nynorsk (Norway) | nn-NO | words | 1.6 |
| Odia (India) | or-IN | words | 1.5 |
| Pashto (Afghanistan) | ps-AF | words | 2.1 |
| Persian (Iran) | fa-IR | words | 1.5 |
| Portuguese (Portugal) | pt-PT | words | 1.6 |
| Punjabi (India) | pa-IN | words | 2.3 |
| Serbian (Serbia) | sr-RS | words | 1.7 |
| Sindhi (India) | sd-IN | words | 2.1 |
| Sinhala (Sri Lanka) | si-LK | words | 1.6 |
| Slovak (Slovakia) | sk-SK | words | 1.7 |
| Slovenian (Slovenia) | sl-SI | words | 1.6 |
| Spanish (Latin America) | es-419 | words | 1.7 |
| Spanish (Mexico) | es-MX | words | 1.8 |
| Swahili (Kenya) | sw-KE | words | 1.8 |
| Swedish (Sweden) | sv-SE | words | 1.8 |
| Urdu (Pakistan) | ur-PK | words | 2.2 |
