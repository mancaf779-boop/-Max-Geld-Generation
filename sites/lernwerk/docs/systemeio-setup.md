# Lernwerk × FOKUS-OS — Systeme.io Setup (Copy-Paste-Bausteine)

> Alles feldweise zum direkten Einfügen. Reihenfolge folgt dem Aufbau in Systeme.io:
> Funnel → Opt-in-Seite → Danke-Seite → Automation (E-Mails).
> Platzhalter `[…]` vor dem Veröffentlichen ersetzen.

---

## FUNNEL ANLEGEN
- **Funnels → Create** → Ziel **"Build an audience"** (Opt-in)
- Name: `Lernwerk – 5 Fokus-Quickstarts`
- Der Funnel bekommt automatisch die Schritte **Squeeze Page** (Opt-in) und **Thank you** (Danke-Seite).

---

## 1) OPT-IN-SEITE (Landing Page)

**SEO / Seiteneinstellungen**
- Seitentitel (Meta Title): `Effektiv lernen & Konzentration steigern – Gratis-Guide | Lernwerk`
- Meta-Beschreibung: `Der kostenlose PDF-Guide zeigt dir 5 erprobte Lerntechniken für mehr Fokus und effektives Lernen – ohne stundenlanges Pauken.`

**Marken-Zeile (oben)**
```
LERNWERK
```
(darunter dezent, falls Platz:)
```
epubflow.xyz
```

**Eyebrow / kleine Vorzeile**
```
Gratis-Guide von Lernwerk
```

**Headline (H1)**
```
In 7 Tagen doppelt so fokussiert lernen – ohne stundenlanges Pauken
```

**Sub-Headline**
```
Der Guide zeigt dir 5 erprobte Lerntechniken, mit denen du deine Konzentration steigerst und effektiv lernst – auch wenn dir bisher nach 20 Minuten die Aufmerksamkeit wegbricht.
```

**Benefit-Bullets (3)**
```
• Schluss mit Ablenkung: so hältst du deinen Fokus über Stunden
• Mehr behalten in weniger Zeit – mit Active Recall & Spaced Repetition
• Ein einfacher Lernplan, der auch unter Prüfungsstress funktioniert
```

**Formular**
- Feld: E-Mail (Pflicht) — Platzhalter im Feld: `Deine E-Mail-Adresse`
- (Optional Vorname-Feld, wenn du personalisieren willst — Platzhalter: `Dein Vorname`)

**Button-Text**
```
Guide kostenlos sichern
```

**Micro-Copy (unter dem Button)**
```
Kostenlos · kein Spam · jederzeit abmeldbar
```

---

### Optionale Sektion darunter: „Was drin ist" (erhöht Vertrauen)

**Abschnitts-Überschrift**
```
Kein Motivations-Blabla. Fünf Techniken, die du sofort anwendest.
```

**Die 5 Punkte**
```
1 · Der 25-Minuten-Start — mühelos anfangen und dranbleiben
2 · Active Recall — mehr behalten, ohne öfter zu lesen
3 · Der 90-Sekunden-Reset — Konzentration zurückholen, wenn sie kippt
4 · Der Ein-Zettel-Lernplan — Schluss mit Last-Minute-Panik
5 · Das Handy-Problem lösen — Ablenkung fast unmöglich machen
```

**Trust-Zeile (Platzhalter, sobald du erste Rückmeldungen hast)**
```
„Ich lerne in der halben Zeit – und behalte tatsächlich mehr." — [Name, erste:r Nutzer:in]
```

**Zweiter CTA-Button (gleicher Text wie oben)**
```
Guide kostenlos sichern
```

---

## 2) DANKE-SEITE (Thank you)

**Überschrift**
```
Fast geschafft – hier ist dein Guide
```

**Text**
```
Dein PDF wartet auf dich. Klick unten zum Download – und schau auch in dein Postfach, dort schicke ich ihn dir gleich zur Sicherheit noch mal.

Kleiner Tipp: Nimm dir jetzt direkt Quickstart Nr. 1 vor und probier ihn beim nächsten Lernen aus.
```

**Download-Button**
- Text: `5 Fokus-Quickstarts herunterladen`
- Ziel: die hochgeladene Datei `5-Fokus-Quickstarts.pdf`
  (In Systeme.io das PDF unter **Contacts → Files** bzw. im Button als „File download" hinterlegen.)

---

## 3) DEINE EINE AUTOMATION (Gratis-Plan = 1 Regel)

**Aufbau:** Rule → **Trigger:** „Sign up to funnel" (dein Funnel) → **Actions** in dieser Reihenfolge:
1. E-Mail senden: **Mail 1** (sofort)
2. Wait 2 days → **Mail 2**
3. Wait 2 days → **Mail 3**
4. Wait 2 days → **Mail 4**
5. Wait 2 days → **Mail 5**
6. Wait 3 days → **Mail 6**

> Personalisierung: Systeme.io nutzt Merge-Tags wie `{{contact.first_name}}`. Wo unten `[Vorname]` steht, das entsprechende Tag einsetzen (oder weglassen, wenn du kein Vorname-Feld nutzt).
> Ersetze `[KOMPAKT-LINK]` und `[PRO-LINK]` durch deine Digistore24-Verkaufslinks und `[DATUM]` durch dein Launch-Enddatum.

---

## 4) DIE E-MAILS (Betreff + Text, copy-paste)

### ✉️ Mail 1 — sofort
**Betreff:** Da ist dein Guide 📩
```
Hi [Vorname],

hier ist er – deine 5 Fokus-Quickstarts als PDF:

👉 [Download-Link / Danke-Seiten-Link]

Kleiner Tipp, damit's nicht im Download-Ordner verstaubt: Nimm dir jetzt gleich einen der fünf Punkte vor und probier ihn beim nächsten Lernen aus. Am besten Nummer 1 – der 25-Minuten-Start. Der ist die Grundlage für alles andere.

In den nächsten Tagen schreibe ich dir noch ein paar Mails mit konkreten Lern-Tipps, die im PDF keinen Platz hatten. Kein Spam, versprochen – und du kannst jederzeit unten aussteigen.

Viel Erfolg beim Ausprobieren,
[Dein Name]
Lernwerk · epubflow.xyz
```

### ✉️ Mail 2 — nach 2 Tagen
**Betreff:** Der häufigste Lernfehler (fast jeder macht ihn)
```
Hi [Vorname],

kurze Frage: Wenn du für eine Prüfung lernst – liest du dir den Stoff mehrmals durch, bis er sich vertraut anfühlt?

Falls ja, bist du in guter Gesellschaft. Fast alle machen das. Und es ist trotzdem einer der größten Zeitfresser beim Lernen.

Der Grund: Vertrautheit ist nicht dasselbe wie Wissen. Ein Text, den du zum fünften Mal liest, fühlt sich an, als säße er. In der Prüfung merkst du dann, dass da ein Loch ist.

Was tatsächlich funktioniert, ist das genaue Gegenteil: den Stoff aus dem Kopf abrufen, statt ihn nochmal vor die Augen zu halten. Lesen, zuklappen, mit eigenen Worten wiedergeben. Wo du hängst, sitzt die Lücke – und genau die schließt du dann gezielt.

Klingt anstrengender? Ist es. Und genau deshalb wirkt es.

Probier's beim nächsten Lernen mal aus. Morgen zeige ich dir, wie du dafür sorgst, dass das Gelernte auch Wochen später noch da ist.

Bis dahin,
[Dein Name]
```

### ✉️ Mail 3 — nach 2 Tagen
**Betreff:** Warum du das meiste wieder vergisst (und was hilft)
```
Hi [Vorname],

hast du dich schon mal gefragt, warum du eine Woche nach der Prüfung kaum noch was vom Stoff weißt?

Das ist keine Schwäche – das ist Biologie. Dein Gehirn wirft aus, was es für unwichtig hält. Und „einmal gelernt und nie wieder angeschaut" schreit für dein Gehirn: unwichtig.

Der Ausweg ist erstaunlich effizient. Du musst nicht mehr wiederholen – du musst nur im richtigen Abstand wiederholen. Heute gelernt, morgen einmal kurz abrufen, dann nach drei Tagen, dann nach einer Woche. Jede Wiederholung dauert nur Minuten und schiebt den Stoff tiefer ins Langzeitgedächtnis.

Das ist der Unterschied zwischen Lernen für die Prüfung und Lernen fürs Behalten. Und ehrlich gesagt kostet es weniger Zeit als das Panik-Pauken am Abend vorher.

Wenn du merkst, dass dich das Thema Lernen wirklich weiterbringt – ich hab genau dafür was gebaut. Dazu morgen mehr.

[Dein Name]
```

### ✉️ Mail 4 — nach 2 Tagen
**Betreff:** Ich hab das ganze System aufgeschrieben
```
Hi [Vorname],

die letzten Mails waren einzelne Puzzleteile – anfangen, abrufen, wiederholen. Einzeln helfen sie schon. Zusammen ergeben sie ein System.

Genau das habe ich in FOKUS-OS Kompakt zusammengefasst: die sechs Methoden, die dich zuverlässig in den Fokus bringen und dafür sorgen, dass der Stoff sitzt. In einem Nachmittag gelesen, sofort anwendbar, mit einer Lernplan-Vorlage zum Loslegen.

Es kostet weniger als ein Kinobesuch – ich wollte es bewusst so halten, dass es für jeden drin ist, der wirklich besser lernen will.

👉 FOKUS-OS Kompakt ansehen: [KOMPAKT-LINK]

Kein Druck. Die kostenlosen Tipps bleiben kostenlos. Aber wenn du das komplette System an einem Ort haben willst, ist das der einfachste Weg.

[Dein Name]
```

### ✉️ Mail 5 — nach 2 Tagen
**Betreff:** „Reicht mir nicht das kostenlose PDF?"
```
Hi [Vorname],

berechtigte Frage. Das Gratis-PDF ist echt – es löst das häufigste Problem: überhaupt in den Fokus zu kommen.

Der Unterschied zu FOKUS-OS Kompakt: Da geht es auch ums Behalten. Der richtige Wiederhol-Rhythmus, ein Lernplan, der unter Prüfungsstress hält, und die Methoden so ausgearbeitet, dass du sie wirklich anwendest statt nur zu nicken.

Wenn du gerade auf eine Prüfung zusteuerst oder dich beim Lernen ständig verzettelst, spart dir das mehr Zeit, als es kostet.

👉 Zum Kompakt-Guide: [KOMPAKT-LINK]

Und falls du tiefer einsteigen willst – es gibt auch eine Pro-Version mit fortgeschrittenen Techniken, 30-Tage-Plan und Vorlagen: [PRO-LINK]

[Dein Name]

PS: Beide sind gerade noch zum Einführungspreis zu haben. Der steigt, sobald die Launch-Phase vorbei ist.
```

### ✉️ Mail 6 — nach 3 Tagen
**Betreff:** Der Einführungspreis läuft bald aus
```
Hi [Vorname],

kurze, ehrliche Nachricht: Der Einführungspreis für FOKUS-OS Kompakt und Pro gilt nur noch bis [DATUM]. Danach steigen beide auf ihren regulären Preis – kein künstlicher Countdown, das ist einfach der Plan.

Falls du sowieso überlegt hast: Jetzt ist der günstigste Zeitpunkt.

👉 Kompakt sichern: [KOMPAKT-LINK]
👉 Pro ansehen: [PRO-LINK]

Und wenn's gerade nicht passt – auch gut. Die Lern-Tipps bekommst du weiter, unabhängig davon.

[Dein Name]
```

---

## 5) DOMAIN VERBINDEN
- Systeme.io: **Settings → Custom domains → Add** → `epubflow.xyz`
- Die angezeigten DNS-Einträge bei **GoDaddy → Domain → DNS** eintragen.
- Danach im Funnel unter **Settings → Path** die Opt-in-Seite als Startseite setzen.
- Ergebnis: Dein Funnel läuft unter epubflow.xyz und ersetzt die alte Platzhalter-Vorlage.

---

## CHECKLISTE VOR DEM LIVE-GANG
- [ ] PDF hochgeladen und Download-Button auf der Danke-Seite getestet
- [ ] Automation aktiv, Testeintrag gemacht (kommt Mail 1 an?)
- [ ] `[KOMPAKT-LINK]` / `[PRO-LINK]` / `[DATUM]` / `[Dein Name]` überall ersetzt
- [ ] Absender-Domain authentifiziert (SPF/DKIM) — sonst Spam-Gefahr
- [ ] Impressum & Datenschutz verlinkt (Pflicht in DE)
- [ ] Domain verbunden, HTTPS aktiv
```
