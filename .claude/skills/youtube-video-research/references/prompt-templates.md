# Prompt Templates for manus-analyze-video

## Table of Contents

1. High-Density Prompt Engineering Principles
2. Universal High-Density Templates
3. Travel-Specific Templates
4. Company-Specific Templates
5. Person-Specific Templates
6. Content-Type Templates

## High-Density Prompt Engineering Principles

A/B testing confirms that `manus-analyze-video` output quality is **entirely determined by prompt design**. A structured, quote-demanding prompt yields 2.4x more content, 12 direct quotes vs 0, and 18 precise data points vs 6 vague mentions — on the exact same video. Follow these rules for every prompt:

**Mandatory elements in every prompt:**

1. **Demand direct quotes**: "Extract at least 8-10 near-exact quotes from the speaker, preserving their original wording in quotation marks."
2. **Demand exhaustive data**: "Include ALL numbers, dollar amounts, percentages, dates, deadlines, company names, person names, and metrics mentioned."
3. **Request structured sections**: Use labeled sections (A/B/C/D/E/F) so output is organized and parseable.
4. **Request sentiment rating**: "Rate the speaker's overall stance and note where they express uncertainty vs conviction."
5. **Explicitly permit long output**: "Be exhaustive. Length is not a concern — information density is. Do not summarize when you can quote directly."

**Anti-patterns to avoid:**

| Bad prompt | Why it fails | Better alternative |
|---|---|---|
| "Summarize this video" | Produces thin, quote-free bullet points | Use the full structured template below |
| "What are the key points?" | No quotes, no data, no structure | "Extract ALL data points and at least 8 direct quotes..." |
| "Tell me about [topic]" | Too vague, no extraction targets | Specify exactly what categories to extract |

## Universal High-Density Templates

### Maximum-detail extraction (default for all videos)

```
Extract MAXIMUM detail from this video about [topic]. For every claim the
speaker makes, capture their near-exact wording as a direct quote in quotation
marks. Include ALL numbers, dates, dollar amounts, percentages, company names,
and person names mentioned.

Structure output as:
(A) SPEAKER PROFILE: Name, credentials, disclaimers, sponsors.
(B) DIRECT QUOTES: At least 8 verbatim or near-verbatim quotes with topic labels.
(C) ALL DATA POINTS: Every number, metric, date, name as a numbered list.
(D) KEY ARGUMENTS: Main thesis broken into sub-arguments with supporting quotes.
(E) COUNTER-ARGUMENTS / RISKS: Every risk, caveat, or opposing view with quotes.
(F) SENTIMENT: Overall stance rating and confidence level.

Be exhaustive. Length is not a concern — information density is.
Do not summarize when you can quote directly.
```

### Factual extraction with quotes

```
Extract all specific facts from this video: names, numbers, dates, places,
organizations, and URLs mentioned. For each major claim, include the speaker's
near-exact wording as a direct quote. List each fact as a numbered item.
Include at least 8 direct quotes from the speaker(s).
```

### Opinion and stance mapping with quotes

```
Identify every opinion, prediction, recommendation, or value judgment expressed
in this video. For each, provide: (1) who said it, (2) their near-exact words
as a direct quote, (3) how confident they seemed, (4) what evidence they cited.
Distinguish facts from opinions. Include ALL names, numbers, and dates mentioned.
```

### Comparison extraction with quotes

```
This video compares or discusses multiple [options/companies/products]. Extract
a comparison matrix with specific data points. For each dimension compared,
include the speaker's near-exact wording as a direct quote. Note the speaker's
final recommendation and their reasoning with supporting quotes.
Include ALL numbers, metrics, and specific claims mentioned.
```

## Travel-Specific Templates

See [travel-research.md](travel-research.md) for full context.

### All-in-one travel vlog

```
Extract MAXIMUM practical detail from this travel vlog about [destination].
For every recommendation, capture the creator's near-exact wording as a quote.

Structure output as:
(A) CREATOR PROFILE: Name, travel style, audience, credibility signals.
(B) PLACES VISITED: Name, location, description, creator's quote about each.
(C) FOOD & DINING: Every restaurant/food spot with name, dishes, prices, creator's reaction quote.
(D) TRANSPORT: Methods, costs, tips — with creator's exact advice quotes.
(E) ACCOMMODATION: Details, prices, pros/cons with quotes.
(F) BUDGET: Every cost mentioned as a numbered list. Calculate implied daily budget.
(G) TIPS & WARNINGS: Practical advice with creator's exact phrasing.

Be exhaustive. Include ALL prices, names, and locations mentioned.
```

### Cost-focused

```
Extract every cost and price mentioned in this video about [destination].
For each price, include the creator's near-exact wording. Organize into:
accommodation, food, transport, activities, and miscellaneous.
Calculate implied daily budget. Include at least 5 direct quotes about value/cost.
```

## Company-Specific Templates

See [company-research.md](company-research.md) for full context.

### CEO/founder interview — maximum extraction

```
Extract MAXIMUM detail from this interview with [CEO/founder name] of [company].
For every strategic claim, capture their near-exact wording as a direct quote.
Include ALL numbers, dates, metrics, company names, and person names mentioned.

Structure output as:
(A) SPEAKER PROFILE: Name, title, background, communication style assessment.
(B) DIRECT QUOTES: At least 8-10 near-verbatim quotes with topic labels covering:
    strategy, metrics, competition, culture, predictions, and any evasive moments.
(C) ALL DATA POINTS: Every number, metric, date, partnership, product name as a list.
(D) STRATEGIC VISION: Main thesis with supporting quotes.
(E) RISKS & RED FLAGS: Contradictions, vague answers, deflections, acknowledged challenges.
(F) LEADERSHIP ASSESSMENT: Communication style (visionary/operational/defensive/candid).

Be exhaustive. Length is not a concern — information density is.
Do not summarize when you can quote directly.
```

### Earnings call — maximum extraction

```
Extract MAXIMUM detail from this earnings call for [company].
Capture management's near-exact wording for every financial claim and forward
guidance statement. Include ALL reported metrics, analyst questions, and
management responses.

Structure output as:
(A) KEY FINANCIAL METRICS: Revenue, growth, margins, cash, guidance — as numbered list.
(B) MANAGEMENT QUOTES: At least 8 near-verbatim quotes from prepared remarks and Q&A.
(C) ANALYST QUESTIONS: Each question summarized with management's quoted response.
(D) STRATEGIC PRIORITIES: What management emphasized, with supporting quotes.
(E) RISKS & OMISSIONS: Challenges acknowledged, topics avoided, tone shifts.
(F) FORWARD GUIDANCE: Specific numbers and timelines with exact quoted language.

Be exhaustive. Separate prepared remarks from Q&A insights.
```

### Bearish / critical analysis — maximum extraction

```
Extract MAXIMUM detail from this critical/bearish analysis of [company].
Capture the analyst's near-exact wording for every negative claim and risk factor.
Include ALL numbers, comparisons, and historical precedents cited.

Structure output as:
(A) ANALYST PROFILE: Name, credentials, track record, disclosed conflicts of interest.
(B) DIRECT QUOTES: At least 8 near-verbatim quotes covering the core bear thesis.
(C) ALL DATA POINTS: Every number, valuation metric, insider transaction, date mentioned.
(D) CORE BEAR THESIS: Main argument broken into sub-points with supporting quotes.
(E) SPECIFIC RED FLAGS: Each risk factor with the analyst's exact framing.
(F) COUNTER-ARGUMENTS: Any bull case points the analyst acknowledges but dismisses.
(G) HISTORICAL COMPARISONS: Failed companies or precedents cited, with quotes.

Be exhaustive. Length is not a concern — information density is.
```

### Product/demo analysis

```
Extract MAXIMUM detail from this product launch or demo video from [company].
Capture presenter's near-exact wording for every product claim.

Structure output as:
(A) PRESENTER PROFILE: Name, role, credibility.
(B) DIRECT QUOTES: At least 6 near-verbatim quotes about product capabilities.
(C) FEATURES & SPECS: Every feature, metric, and technical claim as a numbered list.
(D) MARKET POSITIONING: Target market, competitive claims, pricing — with quotes.
(E) TIMELINE: Availability dates, rollout plans.
(F) GAPS: What was NOT mentioned that competitors offer.
(G) AUTHENTICITY ASSESSMENT: Real capability vs. marketing polish.

Be exhaustive. Include ALL technical specifications and numbers.
```

## Person-Specific Templates

See [person-research.md](person-research.md) for full context.

### Interview personality profile — maximum extraction

```
Extract MAXIMUM detail from this interview to build a profile of [person].
Capture their near-exact wording for every significant statement.

Structure output as:
(A) SUBJECT PROFILE: Name, title, background, interview context.
(B) DIRECT QUOTES: At least 8-10 near-verbatim quotes revealing beliefs, values, style.
(C) CORE BELIEFS: Values and philosophy articulated, with supporting quotes.
(D) PERSONAL ANECDOTES: Stories shared, lessons drawn, with quoted phrasing.
(E) INFLUENCES: Mentors, books, experiences credited — with quotes.
(F) COMMUNICATION STYLE: How they handle tough questions, humor, vulnerability.
(G) AUTHENTICITY ASSESSMENT: Genuine vs. performed moments.

Be exhaustive. Preserve the subject's voice and distinctive phrasing.
```

### Career narrative extraction

```
Extract the complete career narrative from this video about [person].
Capture their near-exact wording for every milestone and turning point.

Structure output as:
(A) CAREER TIMELINE: Key milestones as a chronological numbered list.
(B) DIRECT QUOTES: At least 6 near-verbatim quotes about career decisions.
(C) TURNING POINTS: Pivotal moments with the subject's own framing.
(D) FAILURES & LESSONS: Setbacks discussed, with quoted reflections.
(E) INFLUENCES: Mentors, role models credited — with quotes.
(F) WHAT THEY EMPHASIZE vs. SKIP: Notable inclusions and omissions.

Be exhaustive. Include ALL names, dates, companies, and roles mentioned.
```

## Content-Type Templates

### Conference talk / keynote — maximum extraction

```
Extract MAXIMUM detail from this conference talk/keynote.
Capture the speaker's near-exact wording for every key argument and prediction.

Structure output as:
(A) SPEAKER PROFILE: Name, role, expertise, event context.
(B) DIRECT QUOTES: At least 8 near-verbatim quotes covering the central thesis.
(C) CENTRAL THESIS: Main argument with supporting evidence and quotes.
(D) DATA & EVIDENCE: Every statistic, case study, and example cited.
(E) PREDICTIONS & CALLS TO ACTION: Forward-looking statements with exact wording.
(F) CREDIBILITY ASSESSMENT: Thought leadership quality, audience engagement.

Be exhaustive. Length is not a concern — information density is.
```

### Panel discussion — maximum extraction

```
Extract MAXIMUM detail from this panel discussion.
For EACH panelist, capture their near-exact wording for key positions.

Structure output as:
(A) PANELIST PROFILES: Name, role, expertise for each participant.
(B) DIRECT QUOTES: At least 2-3 near-verbatim quotes PER panelist.
(C) KEY DEBATE POINTS: Where panelists agree vs. disagree, with quotes from each side.
(D) UNIQUE INSIGHTS: Novel points made by individual panelists.
(E) DATA CITED: Every number, study, or example referenced by any panelist.
(F) CONSENSUS vs. DIVERGENCE: Summary of where the panel lands.

Be exhaustive. Distinguish each panelist's voice and position.
```

### Documentary / long-form feature

```
Extract MAXIMUM detail from this documentary or feature video.
Capture near-exact quotes from key subjects and narration.

Structure output as:
(A) PRODUCTION CONTEXT: Creator, publication, apparent perspective/bias.
(B) DIRECT QUOTES: At least 8 near-verbatim quotes from subjects and narration.
(C) CENTRAL NARRATIVE: The argument or story arc with supporting quotes.
(D) KEY CHARACTERS: Each person featured, their role, their quoted statements.
(E) EVIDENCE PRESENTED: Data, documents, visuals cited.
(F) EDITORIAL FRAMING: How the creator shapes the narrative — separate from facts.

Be exhaustive. Separate factual claims from editorial framing.
```
