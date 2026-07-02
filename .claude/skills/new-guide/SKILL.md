---
name: new-guide
description: Research the most-searched topic in one of the epubflow.xyz niches (FOKUS-OS — focus/learning/concentration; VITAL-OS — Gesundheit/Fitness/Abnehmen; German market) and produce a new sellable PDF guide in the house brand style, plus a Leseprobe and a matching Digistore24 affiliate recommendation. Use when the user asks for a new guide, a new digital product, or "run the guide workflow".
---

# New-Guide Workflow: Research → Pick → Write → Build → Ship

## Auto mode

When asked to "run the guide workflow" (voll-automatisch): invoke the
`market-research` skill first (it writes `research/YYYY-MM-DD-report.md`
and names a winner), take the winner without asking, then run Steps 3–6
below to the finished PDF + Leseprobe, commit, push, and send the files.
Steps 1–2 below are the manual fallback when market-research is not used.
Guard: if the two existing products are not yet live/selling, remind the
user that launch beats a third product — build only if they confirm.

Produces a new digital PDF product for the FOKUS-OS brand (epubflow.xyz).

## Step 1 — Keyword research

Use WebSearch (German market focus) to find what people actually search for
in the niche: focus, concentration, learning, memory, productivity, and the
brand's audiences (students/learners, women 50+). Good query patterns:

- "meistgesuchte Keywords Konzentration Lernen Suchvolumen"
- "Google Trends Deutschland <topic-candidates>"
- "<candidate> Suchvolumen monatlich"
- Complement with English sources on search volume for German terms.

Collect 5–10 candidate topics with whatever demand signals you can find
(reported monthly search volumes, trend direction, competition notes).

## Step 2 — Pick the topic

Score candidates by: (1) search demand, (2) fit with the FOKUS-OS brand
(evidence-based focus/learning methods, no medical claims, no hype),
(3) willingness to pay (acute pain → paying customers), (4) not already
covered by an existing product in this repo. Tell the user which topic won
and why in one short paragraph. Do not ask for confirmation unless two
candidates are genuinely tied.

## Step 3 — Write the guide

Create `guide/<slug>.html`. Copy the brand CSS and page structure from
`guide/fokus-os-50plus.html` (the reference implementation). Brand rules:

- German, du-form. Honest, direct, warm. No hype, no guarantees.
  Tagline style: "Kein Motivations-Blabla."
- Navy cover (#141c30) with amber rail (#e9a23b), mono brandline
  "FOKUS-OS / epubflow.xyz", cream content pages (#f4f2ec).
- Numbered methods/hurdles with big amber numerals.
- Every section ends with an "→ SOFORT UMSETZEN" action box.
- 7–9 pages: cover, intro ("Kurz vorweg"), 4–6 numbered core sections,
  an action plan (14 or 30 days), closing page with upsell block (MERKE,
  points to epubflow.xyz + email link) and the standard disclaimer
  (erprobte Methoden, keine Erfolgsgarantie; keine medizinische Beratung
  if the topic touches health).

## Step 4 — Build and QA

- Build: `./guide/build-pdf.sh <slug>.html` → `dist/<slug>.pdf`.
- Verify the page count equals the number of `class="page"` divs
  (a mismatch means content overflowed; tighten spacing or cut text).
- Read the PDF once and check: no orphan pages, footers on every cream
  page, no text colliding with the footer.

## Step 5 — Leseprobe + ship

- Create a 4-page Leseprobe: cover (kicker prefixed "Leseprobe"),
  intro page, the strongest single section, then a dark CTA page listing
  what the full guide contains ("Das war X von Y") with the
  Einführungspreis pointer.
- Build both PDFs, commit HTML + PDFs, push, and send the PDFs to the
  user with SendUserFile.

## Step 6 — Matching marketplace product (Doppel-Angebot)

Research which Digistore24 product fits the guide's problem, so the user
can offer it alongside the PDF (affiliate). Selection criteria:

- German-language product matching the exact audience and problem.
- Reputable: no miracle-cure claims, no guaranteed weight/income results,
  no "Wirkung der Spritze als Kapsel" supplements — these are legal and
  reputation risks in the German health market (HWG/UWG).
- Economics: 40%+ commission, sensible price point relative to the PDF
  (PDF as 7–27 € front-end, affiliate product as 47–200 € deep-dive),
  low refund rate, professional sales page.
- Integration: recommend via the post-purchase email series ("passende
  Vertiefung"), not as links inside the PDF itself — keeps the product
  clean and the recommendation updatable. Affiliate links must be
  disclosed as Werbung/Affiliate.

The live marketplace requires a Digistore24 login, so name concrete
candidate categories/products from public research and give the user the
criteria to make the final pick in their account.
