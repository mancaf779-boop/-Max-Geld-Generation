# Build-Prompt: Landing Page "Fokus & effektives Lernen" (DE + EN)

> Diesen kompletten Prompt 1:1 in Claude Code / einen Code-Agenten geben, um beide Landing Pages direkt zu bauen.

---

Du bist Design Lead an einem kleinen Studio, das für unverwechselbare visuelle Identitäten bekannt ist. Baue eine Lead-Magnet-Landing-Page (HTML/CSS/JS, ein File, kein Framework nötig) für ein PDF-Produkt zum Thema **Fokus & effektives Lernen**, in zwei Sprachversionen: `index-de.html` und `index-en.html` (identische Struktur, lokalisierte Copy, kein Sprachmix auf einer Seite).

## Subject & Zielgruppe
- Produkt: kostenloser PDF-Guide "Fokus & effektives Lernen" als Lead-Magnet
- Zielgruppe: Schüler, Studierende, Berufstätige mit Prüfungen/Lernpensum, die Konzentration & Lerneffizienz verbessern wollen
- Single Job der Seite: E-Mail-Adresse gegen PDF-Download — **ein Ziel, keine Navigation, keine konkurrierenden Links**

## Design-Auftrag (aus dem Frontend-Design-Skill)
- **Kein AI-Default:** Vermeide die drei Cluster-Looks (warmes Creme + Serif + Terracotta / Near-Black + Neon-Akzent / Broadsheet-Zeitungslayout). Triff eine Entscheidung, die aus dem Thema selbst kommt: Fokus, Klarheit, ruhiger Kopf, Struktur beim Lernen — nicht aus generischen SaaS-Mustern.
- **Hero als These:** Der Einstieg soll das Charakteristischste des Themas zeigen — z.B. eine visuelle Metapher für "vom Chaos zum Fokus" (unruhige/verstreute Elemente, die sich zu einer klaren Linie/einem Raster ordnen), statt einer generischen Badge+Überschrift+Screenshot-Struktur.
- **Typografie mit Persönlichkeit:** Eine markante Display-Schrift (mit Zurückhaltung eingesetzt) + eine ruhige, gut lesbare Fließtext-Schrift + ggf. eine Mono/Utility-Schrift für Zahlen/Labels. Bewusstes Paar, keine Standardkombination.
- **Struktur = Information:** Wenn du Nummerierung/Eyebrows/Dividers nutzt, müssen sie etwas Echtes codieren (z.B. die Schritte des Funnels, nicht dekorative 01/02/03).
- **Gezielte Bewegung:** Ein orchestrierter Moment (z.B. Scroll-Reveal des PDF-Mockups oder eine ruhige Lade-Sequenz) statt verstreuter Hover-Effekte überall.
- **Ein Wagnis, sonst diszipliniert:** Spare dir die Kühnheit für EIN Signature-Element auf, alles andere ruhig und aufgeräumt.
- Arbeite in zwei Durchgängen: erst kompaktes Token-System (Farbe: 4–6 benannte Hex-Werte; Type: 2–3 Rollen; Layout: ASCII-Wireframe; Signature-Element), kritisch gegen den generischen Default prüfen, DANN erst Code schreiben.
- Barrierefreiheit: mobil-responsiv, sichtbarer Keyboard-Focus, `prefers-reduced-motion` respektieren.

## Pflicht-Content-Struktur (aus dem Funnel-Research — nicht verhandelbar)
1. **Above the Fold:** Outcome-Headline (6–12 Wörter, Formel "How-to + Outcome + Timeframe" oder "Get [Benefit] without [Objection]") + Sub-Headline + 3 Benefit-Bullets + PDF-Mockup/Visual + ein auffälliger CTA-Button.
2. **Ein Formularfeld:** nur E-Mail (kein Name, kein Telefon). Micro-Copy darunter: "Kostenlos, kein Spam, jederzeit abmeldbar" / "Free, no spam, unsubscribe anytime".
3. **Trust-/Social-Proof-Block:** Platzhalter für Testimonial mit Name + Ergebnis + Foto-Slot, plus Downloadzähler-Platzhalter ("Schon von X Lernenden genutzt").
4. **Content-Vorschau:** 3–5 konkrete Inhalts-Häppchen aus dem PDF (was der Nutzer konkret lernt), keine vagen Versprechen.
5. **CTA-Wiederholung:** an mind. 2 weiteren Scroll-Punkten, immer identische Handlung/Wortwahl.
6. **Copy-Niveau:** einfache Sprache (5.–7. Klasse-Niveau), kurze Sätze, aktive Verben, keine Fachsprache — Text schreibst du selbst, passend zur Tonalität der Marke.
7. Keine Navigation, kein Footer mit externen Links, keine Ablenkung vom einzigen Ziel.

## Keyword-Integration (natürlich, nicht Keyword-Stuffing)
**DE-Version** — Haupt-Keywords in H1/H2, Meta-Title, Meta-Description, Alt-Texten unterbringen:
- Primär: "effektiv lernen", "Konzentration steigern", "lernen lernen"
- Sekundär: "Lerntechniken", "Prüfungsvorbereitung", "Konzentration verbessern"

**EN-Version** — analog:
- Primär: "how to focus better", "how to study effectively"
- Sekundär: "study techniques", "improve concentration while studying"

Liefere für beide Versionen fertige `<title>` und `<meta name="description">` Tags.

## Technische Anforderungen
- Ein HTML-File pro Sprache, CSS + JS inline (kein Build-Step nötig)
- Ladezeit-Priorität: keine schweren externen Assets, System-Fonts oder max. 1–2 Web-Fonts via `font-display: swap`
- Formular: `onSubmit` per JS abfangen, Platzhalter-Funktion für spätere E-Mail-Tool-Anbindung (Kit/MailerLite/Brevo), Kommentar im Code wo die echte API-Anbindung reinkommt
- Sauberes Semantic HTML (H1 einmal, sinnvolle H2-Struktur), Schema-freundlich
- Responsive: Mobile-first, teste gedanklich 375px/768px/1440px

## Prozess (bitte in dieser Reihenfolge)
1. Kurzes Design-Plan (Farbe/Type/Layout/Signature) formulieren und gegen generische Defaults prüfen — bei Bedarf revidieren, kurz begründen.
2. `index-de.html` bauen (vollständig, produktionsreif).
3. `index-en.html` bauen (gleiche Struktur, lokalisierte/übersetzte Copy, keine 1:1-Übersetzung sondern natürlicher englischer Ton).
4. Kurze Selbstkritik: einen Blick "im Spiegel" — ein Element streichen/vereinfachen, falls zu viel.

Liefere am Ende beide fertigen HTML-Dateien.
