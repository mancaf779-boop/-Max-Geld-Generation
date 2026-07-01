# Company Research / Due Diligence

## Table of Contents

1. Why YouTube for Company Research
2. The Top Leader Principle
3. Theme-Based Video Discovery Strategy
4. Quote-Rich Output Template

## Why YouTube for Company Research

Company research typically relies on press releases, earnings reports, and news articles — all filtered and polished. YouTube provides access to raw, unscripted moments: CEO interviews where body language and hesitation reveal confidence levels, earnings call Q&A where tough questions get real-time responses, keynotes where product vision is articulated directly, and employee vlogs that show actual company culture. These first-hand video sources are often more revealing than any written analysis.

## The Top Leader Principle

For company research, **always prioritize the top leader (CEO / founder / principal executive)**. The reasoning:

- The CEO's public statements define company direction more reliably than analyst speculation.
- Interview responses reveal strategic thinking, risk awareness, and leadership style.
- Keynote presentations show what the company considers its most important narrative.
- Podcast appearances often produce the most candid, long-form insights.
- Earnings call Q&A sections reveal how leadership handles pressure and uncertainty.

**Search the top leader first, then expand to other executives, employees, and third-party analysts.**

If the CEO/founder name is unknown, use web search to identify them before searching YouTube.

## Theme-Based Video Discovery Strategy

Decompose the company research into **5-7 research themes**, then search and assign 2-3 videos per theme.

### Standard Company Research Themes

| Theme | What to look for | Target video types |
|---|---|---|
| **Industry & macro context** | Market size, trends, tailwinds/headwinds, regulatory environment | Industry analyst panels, macro research talks, sector deep-dives |
| **Business model & technology** | How the company makes money, core product, technical moat | CEO keynotes, product demos, technical conference talks |
| **Financial health & valuation** | Revenue, margins, cash position, burn rate, valuation metrics | Earnings calls, financial analyst deep-dives, stock analysis |
| **Customers & partnerships** | Key customers, deal pipeline, strategic alliances | CEO interviews mentioning deals, partner announcements, customer testimonials |
| **Bull case & growth catalysts** | Why the stock could go up, upcoming milestones, competitive advantages | Bullish analyst videos, CEO vision talks, product roadmap presentations |
| **Bear case & risk factors** | Why the stock could go down, execution risks, red flags | Bearish analyst videos, short-seller presentations, critical reviews |
| **Leadership & culture** | Management quality, insider behavior, organizational health | CEO long-form interviews, employee vlogs, podcast appearances |

### Search Execution Plan

For each theme, run 1-2 search calls with theme-specific queries:

```
Theme: "Bear case & risk factors" for Oklo
  Search 1: "Oklo stock risks concerns bearish analysis YouTube"
  Search 2: "Oklo OKLO problems criticism short seller YouTube"
  → Select 2-3 most relevant critical videos
```

**Total search calls**: 7-14 (1-2 per theme × 5-7 themes)
**Total videos selected**: 12-20 (2-3 per theme × 5-7 themes)

### Video Selection Per Theme

| Priority | Signal | Example |
|---|---|---|
| Highest | First-person: subject/expert speaking directly | Keynote, interview, podcast guest appearance, conference talk |
| High | Expert or insider perspective | Industry analyst, practitioner, local guide, researcher |
| Medium | Third-party quality coverage | Documentary, in-depth review channel, news feature |
| Lower | Aggregated or secondhand content | Compilation, reaction video, news summary |

**Balance requirement**: For investment research, ensure at least 30% of total videos present bearish/critical perspectives.

> **Note on Analysis Prompts**: See `prompt-templates.md` for specific high-density prompts for CEO interviews, earnings calls, bearish analysis, and product demos.

## Quote-Rich Output Template

The final report MUST follow the quote-rich, detail-dense format specified in SKILL.md. Below is the company-specific adaptation:

```markdown
# [Company Name] Investment Research Report

## Executive Summary
[3-4 paragraphs: company overview, strategic direction, key strengths/risks, overall assessment.
MUST include at least 2 blockquotes from different video sources.]

## Industry & Macro Context
[2-3 paragraphs with blockquotes from industry analysts and CEO statements about market dynamics.
Include specific data: market size, growth rates, regulatory milestones.]

## Business Model & Technology
[3-4 paragraphs explaining how the company works, with CEO quotes about vision and technology.
Include technical details, competitive moat analysis, and supply chain specifics.]

## Financial Health & Valuation
[2-3 paragraphs with specific numbers from earnings calls and analyst videos.
Include blockquotes from both bullish and bearish analysts on valuation.]

## Customers & Commercial Progress
[2-3 paragraphs with deal-specific details: customer names, contract sizes, binding vs non-binding.
Include CEO quotes about pipeline and analyst quotes questioning pipeline quality.]

## Bull Case: Growth Catalysts & Competitive Advantages
[2-3 paragraphs presenting the optimistic view with supporting quotes from bullish analysts and CEO.
Include specific upcoming milestones and their potential impact.]

## Bear Case: Risk Factors & Red Flags
[2-3 paragraphs presenting the pessimistic view with supporting quotes from bearish analysts.
Include insider selling data, regulatory risks, cost concerns, and historical precedents.]

## Competitive Landscape
[Comparison table + 1-2 paragraphs with analyst quotes on competitive positioning.]

## Investment Conclusion
[2-3 paragraphs synthesizing bull and bear cases into an actionable assessment.
Include quotes from multiple sources representing different viewpoints.
Suggest key metrics/events to monitor going forward.]

## Source Videos Analyzed
| # | Title | Speaker/Creator | Stance | URL | Key Contribution |
|---|---|---|---|---|---|

## References
[1]: [Video/source title and URL]
[2]: [Video/source title and URL]
...
```

### Writing Quality Checklist

Before delivering the report, verify:

- [ ] Every major section has ≥2 blockquote citations
- [ ] Total blockquotes ≥ 1 per 300 words of body text
- [ ] No key finding is presented as a single-sentence bullet point
- [ ] Every finding paragraph includes: context → specifics → quote → implication
- [ ] Both bull and bear perspectives are represented with equal depth
- [ ] All blockquotes have numeric citations linking to References
- [ ] Speaker names and credentials are identified before their quotes
- [ ] Source Videos table is complete with stance classification
