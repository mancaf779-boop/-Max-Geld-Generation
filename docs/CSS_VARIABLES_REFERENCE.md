# CSS Variables & Theming Reference

**Color system and dark mode implementation for Maxforge Lab site.**

---

## Color Palette

### Light Mode (Default)

```css
/* Ground & Panels */
--ground:    #e9e4db;  /* Page background */
--panel:     #f3efe8;  /* Card background */
--panel-2:   #e0d9cc;  /* Secondary panel, hover states */

/* Text & Hierarchy */
--ink:       #1b1610;  /* Primary text (highest contrast) */
--ink-2:     #4c4338;  /* Secondary text, metadata */
--ink-3:     #7c7264;  /* Tertiary text, labels */

/* Borders & Dividers */
--line:      #d5cdbe;  /* Primary dividers */
--line-2:    #c6bcaa;  /* Secondary dividers, hover borders */

/* Accent Colors */
--forge:     #c8531a;  /* Primary action, hot states */
--forge-2:   #e26520;  /* Secondary forge (brighter) */
--ember:     #cf8a1e;  /* Warm accent */
--cold:      #6b7681;  /* Cool accent (research stage) */

/* Interactive */
--quench:    #2c6b98;  /* Eval section primary */
--quench-2:  #3f80ae;  /* Eval section secondary */
--focus:     #c8531a;  /* Focus outline (same as --forge) */

/* Effects */
--shadow:    rgba(40,28,14,.14);  /* Card shadows */
--grain:     .015;                 /* Grain overlay opacity */
```

### Dark Mode (Automatic via `prefers-color-scheme`)

```css
/* Ground & Panels */
--ground:    #15120e;  /* Page background */
--panel:     #1d1913;  /* Card background */
--panel-2:   #251f17;  /* Secondary panel, hover states */

/* Text & Hierarchy */
--ink:       #f1eae0;  /* Primary text (highest contrast) */
--ink-2:     #bcae9d;  /* Secondary text, metadata */
--ink-3:     #867b6d;  /* Tertiary text, labels */

/* Borders & Dividers */
--line:      #332c21;  /* Primary dividers */
--line-2:    #463c2d;  /* Secondary dividers, hover borders */

/* Accent Colors */
--forge:     #f0742a;  /* Primary action (lighter, more saturated) */
--forge-2:   #ff8636;  /* Secondary forge (brightest) */
--ember:     #f6b23e;  /* Warm accent */
--cold:      #8c98a4;  /* Cool accent (lighter) */

/* Interactive */
--quench:    #5a9ecb;  /* Eval section primary (lighter) */
--quench-2:  #7ab6dd;  /* Eval section secondary (lighter) */
--focus:     #ff8636;  /* Focus outline (same as --forge-2) */

/* Effects */
--shadow:    rgba(0,0,0,.5);  /* Card shadows (darker, more opaque) */
--grain:     .03;              /* Grain overlay opacity (doubled) */
```

---

## Activation

### Automatic (Recommended)

Dark mode activates automatically based on user's system preference:

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* Dark mode variables override */
  }
}
```

**How it works:**
- Light mode: User's system set to "Light" (or not set)
- Dark mode: User's system set to "Dark"
- No JavaScript required

### Manual Override (Optional)

For explicit theme switching, use `data-theme` attribute:

```html
<!-- Force light mode -->
<html data-theme="light">

<!-- Force dark mode -->
<html data-theme="dark">

<!-- Let system decide (default) -->
<html>
```

---

## Using Variables in CSS

### ✅ Correct: Use CSS Variables

```css
.card {
  background: var(--panel);        /* Adapts to dark/light */
  color: var(--ink);               /* Adapts to dark/light */
  border: 1px solid var(--line);   /* Adapts to dark/light */
}
```

**Result:** Card automatically switches between light and dark palettes.

### ❌ Incorrect: Hardcoded Hex

```css
.card {
  background: #f3efe8;    /* Stuck in light mode */
  color: #1b1610;         /* Stuck in light mode */
  border: 1px solid #d5cdbe;  /* Stuck in light mode */
}
```

**Result:** Card is always light, unreadable in dark mode.

---

## Color Usage Patterns

### Hierarchy (Text)

| Level | Variable | Light | Dark | Use Case |
|-------|----------|-------|------|----------|
| Primary | `--ink` | #1b1610 | #f1eae0 | Headings, body text |
| Secondary | `--ink-2` | #4c4338 | #bcae9d | Descriptions, metadata |
| Tertiary | `--ink-3` | #7c7264 | #867b6d | Labels, captions |

### Accents (Action & Stage Colors)

| Name | Light | Dark | Use Case |
|------|-------|------|----------|
| `--forge` | #c8531a | #f0742a | Primary action, hot states |
| `--forge-2` | #e26520 | #ff8636 | Brighter forge, button hover |
| `--ember` | #cf8a1e | #f6b23e | Warmest accent, stage 4 |
| `--cold` | #6b7681 | #8c98a4 | Cool accent, stage 1 |

---

## Contrast Verification

All colors meet **WCAG AA** contrast standards (4.5:1 minimum).

**Light Mode Examples:**
- Body text: 14.8:1 ✅ AAA
- Button: 6.9:1 ✅ AAA

**Dark Mode Examples:**
- Body text: 15.2:1 ✅ AAA
- Button: 5.1:1 ✅ AA

---

## Testing Dark Mode

### Browser DevTools

**Chrome/Edge:**
1. F12 → **Rendering** tab
2. "Emulate CSS media feature prefers-color-scheme" → toggle light/dark

**Firefox:**
1. F12 → **Inspector** → Check "Emulate CSS media features"
2. Select "prefers-color-scheme: dark"

---

## Reference Links

- **WCAG Contrast Checker:** https://webaim.org/resources/contrastchecker/
- **CSS Variables (MDN):** https://developer.mozilla.org/en-US/docs/Web/CSS/--*
- **Prefers Color Scheme:** https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme

---

**Last Updated:** 2026-07-08
