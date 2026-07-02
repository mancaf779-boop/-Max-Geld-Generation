---
name: market-research
description: Research and rank the most-searched, best-monetizable topics in the epubflow.xyz house niches (Fokus/Lernen and Gesundheit/Fitness/Abnehmen, German market), write a dated report to research/, and name a winner. Used standalone or as Step 1 of the new-guide auto mode.
---

# Market-Research Workflow

Goal: a ranked, deduplicated list of guide topics with one clear winner.

## Steps

1. **Gather demand signals** (WebSearch, German market): per niche run 2–3
   searches for trending topics, search-volume mentions, Google-Trends
   coverage, and Digistore24/marketplace bestseller signals. Prefer recent
   sources. Note the source URL for every claim.
2. **Collect 6–10 candidates** across both niches.
3. **Dedup**: a topic is blocked if a guide for it exists in `dist/` or it
   won a previous report in `research/`. List blocked topics with the
   guide/report that blocks them.
4. **Score each candidate 1–5** on:
   - Nachfrage (search demand / trend direction)
   - Schmerz & Kaufbereitschaft (acute problem → pays for solution)
   - Markenpassung (fits FOKUS-OS or VITAL-OS, honest/evidence-based,
     no medical or income claims possible → if the topic can only be sold
     with Wunder-Versprechen, score 1 and flag it)
   - Frei (not covered by existing products; whitespace vs. competition)
   Weighted total = Nachfrage×0.35 + Schmerz×0.3 + Markenpassung×0.2 + Frei×0.15.
5. **Write the report** to `research/YYYY-MM-DD-report.md`: table of
   candidates with scores, the winner with a 3-sentence rationale,
   sources list. Commit it.
6. **Hand off**: in auto mode, the new-guide skill takes the winner and
   builds the guide. Standalone, end by telling the user the winner and
   the runner-up.

## House rules (always apply)

- German market, honest positioning, no guaranteed results.
- Health topics: no healing claims, ärztliche Abklärung hinweisen (HWG).
- Money topics: no income promises (UWG).
