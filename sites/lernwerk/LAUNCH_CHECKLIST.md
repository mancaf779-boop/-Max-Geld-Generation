# Lernwerk / FOKUS-OS — Launch Checklist

This is the ordered list of everything left between "content exists" and "live and taking leads." Everything under **Done in this repo** is finished and committed. Everything under **You do this** requires logging into your own Systeme.io, GoDaddy, and Digistore24 accounts — I can't do these steps for you since they require your account credentials, but every field/value you need is either already written or clearly marked below.

## Done in this repo

- `index-de.html` / `index-en.html` — finalized bilingual landing pages (custom design, brand bar, footer with legal links, content preview, trust section, repeated CTA). Both now have a matching, fully-built structure.
- `impressum.html` / `datenschutz.html` — legal page skeletons with every `[Platzhalter]` marked. **Not legal advice** — you must fill these in and ideally have them checked (see Step 3 below) before the domain goes live and starts collecting emails.
- `assets/pdfs/` — all 4 lead magnet/product PDFs: `5-Fokus-Quickstarts.pdf`, `5-Focus-Quickstarts-EN.pdf`, `FOKUSOS-Kompakt.pdf`, `FOKUSOS-Pro.pdf`.
- `docs/` — the full research/copy backlog: funnel research + keyword lists, the Systeme.io field-by-field setup script, the email sequence, sales copy for all 4 paid tiers + Pinterest pins + Club content plan, and the Deluxe video scripts (for later, once you're ready to record).

## Step 1 — Connect the domain (GoDaddy → Systeme.io)

1. In Systeme.io: **Settings → Domains → Add a domain** → enter `epubflow.xyz`. Systeme.io will show you the exact DNS records to add (usually an A record + CNAME, or two CNAMEs — copy whatever it shows you, the values are account-specific and I can't predict them).
2. In GoDaddy: **My Products → epubflow.xyz → DNS → Manage DNS** → add the records Systeme.io gave you. Remove/replace any conflicting default GoDaddy parking records for the same host.
3. Wait for DNS propagation (Systeme.io will show "Verified" once it sees the records — can take a few minutes to a few hours).

## Step 2 — Build the funnel in Systeme.io

Follow `docs/systemeio-setup.md` for the funnel structure (Opt-in → Thank You → 6-email automation) and exact copy, with these two changes now that the custom pages exist:

1. **Opt-in page**: instead of Systeme.io's native text fields, add a **Raw HTML** element to the page and paste the full contents of `index-de.html` (or `index-en.html` for the English funnel — build these as two separate funnels/steps if you want both live, or start DE-only and add EN later per the phased plan in `docs/funnel-research.md`).
2. **Wire up the real form** (this is the one part that must happen in the Systeme.io UI, not in code):
   - Create a standalone opt-in form: **Settings → Forms** (or add an "Inline form" opt-in step), field: email only, connected to trigger the automation rule from `systemeio-setup.md`.
   - Open that form's **Share/Embed** panel → **"Copy as HTML code."**
   - In `index-de.html` / `index-en.html`, find the two `<!-- SYSTEME.IO: ... -->` comments (in the hero and in the final CTA section) and replace the placeholder `<div class="capture-row">...</div>` markup with the pasted embed code, keeping the outer `<div class="capture" id="cap1">` / `id="cap2"` wrapper.
   - Delete the `submitEmail()` placeholder function and its `onclick` attributes once the real embed is in — Systeme.io's form handles submission, the automation trigger, and can redirect to your Thank You page on its own.
   - The `.capture input` / `.capture button` CSS rules already target plain `<input>`/`<button>` tags, so Systeme.io's embed should inherit the design automatically. If Systeme.io wraps its form in its own class names that resist the styling, inspect the embedded markup once it's live and add a couple of override rules.
3. **Thank You page**: use the copy from `systemeio-setup.md` section 2, with the download button pointing at the matching PDF from `assets/pdfs/` (upload it under **Contacts → Files** or as a "File download" button target, per Systeme.io's own flow).
4. **Automation**: build the single rule (Sign up to funnel → Mail 1 immediately → wait/Mail 2..6) exactly as scripted in `docs/fokusos-email-sequenz.md` (more polished than the older draft in `systemeio-setup.md` — use the email-sequenz version as the source of truth). Leave `{{kompakt_link}}`, `{{pro_link}}`, `{{datum}}` as placeholders until Step 3 gives you real links.
5. Turn on **double opt-in** (legally required in Germany) — Settings for the funnel/form.

## Step 3 — Set up the paid products in Digistore24

Use the ready-made sales copy in `docs/fokusos-verkauf-abo-pinterest.md` (Teil 1) for each product's title/short description/sales text:

1. Create **FOKUS-OS Kompakt** (launch 7€ → regular 17€), **FOKUS-OS Pro** (launch 27€ → regular 47€), **FOKUS-OS Deluxe** (launch 67€ → regular 147€, hold this one until the 9 videos + 3 audios from `docs/fokusos-deluxe-videoskripte.md` are actually recorded), and the **FOKUS-OS Club** subscription (9€/mo founding price → 19€/mo).
2. Upload `assets/pdfs/FOKUSOS-Kompakt.pdf` and `assets/pdfs/FOKUSOS-Pro.pdf` as the deliverables for those two products.
3. Grab each product's real checkout/buy link from Digistore24 and go back into the Systeme.io automation to replace `{{kompakt_link}}` / `{{pro_link}}` (and `[KOMPAKT-LINK]` / `[PRO-LINK]` if you used the older setup doc's copy) with the real URLs. Set `{{datum}}` to your actual launch-price end date.

## Step 4 — Legal pages

1. Fill in every `[Platzhalter]` in `impressum.html` and `datenschutz.html` with your real name/address/contact, VAT status, and the actual list of processors you end up using (Systeme.io, Digistore24, and anything else like a Pinterest ad pixel).
2. Get them checked — a generator like e-recht24.de or a lawyer, not just this template — before the domain is live and collecting real emails. Incorrect Impressum/Datenschutz pages are a real *Abmahnung* (cease-and-desist) risk in Germany.
3. Upload both pages alongside the opt-in page in Systeme.io (or host them as simple pages in the same funnel/site) so the footer links in `index-de.html`/`index-en.html` resolve.
4. Replace `REPLACE_WITH_YOUR_EMAIL` in both landing pages' footers with your real contact address.

## Step 5 — Pinterest

1. Create/claim the Lernwerk Pinterest profile, verify `epubflow.xyz` for Rich Pins + analytics.
2. Set up the niche boards named in `docs/funnel-research.md` / `docs/fokusos-verkauf-abo-pinterest.md` (e.g. "Effektiv lernen", "Lerntipps für Prüfungen", "Konzentration & Fokus").
3. Design the 10 pins in Canva (1000×1500px) using the exact titles/descriptions in `docs/fokusos-verkauf-abo-pinterest.md` Teil 3 — every pin links to the **live opt-in page**, never the homepage.
4. Post 5–10/day into multiple relevant boards each.

## Step 6 — Go live

1. Confirm DNS is verified in Systeme.io (Step 1).
2. Set the opt-in page as the funnel's/domain's homepage (Settings → Path).
3. Submit a real test signup end-to-end: email arrives, download works, automation fires on schedule.
4. Flip the funnel live and start driving Pinterest traffic.

## After launch — use the SEO skills already built in this repo

- The `keyword-research` skill can build a full keyword workbook to replace the estimated volumes flagged in `docs/funnel-research.md` (only "zeitmanagement" was independently verified — verify the rest with Google Keyword Planner/Ubersuggest before investing heavily in a keyword).
- The `content-gap-analysis` and `seo-audit` skills are ready to plan and audit the long-tail blog articles recommended in `docs/funnel-research.md` (Mittelfristig, item 9) once you're ready to add a blog for organic SEO traffic alongside Pinterest.
