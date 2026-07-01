# Travel / Destination Research

## Table of Contents

1. Why YouTube for Travel Research
2. Video Discovery Strategy
3. Output Template

## Why YouTube for Travel Research

Travel vlogs and destination guides on YouTube provide visual, real-time information that text articles cannot match: actual street conditions, crowd levels, food quality, accommodation interiors, transportation logistics, and honest cost breakdowns. Vloggers often share failures, scams, and practical warnings that curated travel blogs omit.

## Video Discovery Strategy

Search for these video types in priority order:

| Video type | Search query pattern | What it provides |
|---|---|---|
| Recent travel vlogs | `[destination] travel vlog [year] YouTube` | Real conditions, honest impressions, visual preview |
| Local food guides | `[destination] food guide street food YouTube` | Restaurant recommendations, prices, must-try dishes |
| Budget/cost breakdowns | `[destination] travel cost budget how much YouTube` | Daily costs, accommodation prices, transport fares |
| Itinerary guides | `[destination] itinerary [N] days YouTube` | Route planning, time allocation, logistics |
| Local tips and warnings | `[destination] travel tips mistakes to avoid YouTube` | Scams, cultural norms, safety advice, local hacks |
| Accommodation reviews | `[destination] hotel hostel review YouTube` | Area recommendations, price-quality assessment |
| Transport guides | `[destination] how to get around transport YouTube` | Metro, bus, taxi, walking routes, passes |
| Seasonal/event content | `[destination] [season/event] YouTube` | Best time to visit, festival experiences |

For non-English destinations, also search in the local language for local creator content.

Run **2-3 search calls** with different query variants. Select **4-6 videos** covering different aspects (food, logistics, costs, itinerary).

> **Note on Analysis Prompts**: See `prompt-templates.md` for specific high-density prompts for general travel vlogs, food guides, budget breakdowns, and itineraries.

## Output Template

```markdown
# [Destination] Travel Research

## Quick Overview
[2-3 sentences: best time to visit, ideal trip length, overall vibe]

## Budget Estimate
| Category | Budget Range | Notes |
|---|---|---|
| Accommodation | $X-Y/night | [type recommendations] |
| Food | $X-Y/day | [street food vs. restaurant] |
| Transport | $X-Y/day | [main methods] |
| Activities | $X-Y/day | [key paid attractions] |
| **Daily Total** | **$X-Y** | |

## Recommended Itinerary
### Day 1: [Theme]
- [Activity with location and timing]

## Must-Try Food
| Spot | Dish | Price | Area | Source |
|---|---|---|---|---|

## Practical Tips
[Numbered list of actionable tips from video analysis]

## Warnings and Common Mistakes
[Things to avoid, scams, cultural faux pas]

## Source Videos
| # | Title | Creator | Date | URL | Focus |
|---|---|---|---|---|---|
```
