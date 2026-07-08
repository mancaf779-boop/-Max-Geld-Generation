# Testing Checklist — Maxforge Lab

## Dark Mode Verification ✅

### Browser Testing
- [ ] **Chrome/Edge** — Light mode looks correct
- [ ] **Chrome/Edge** — Dark mode (prefers-color-scheme) looks correct  
- [ ] **Firefox** — Light mode looks correct
- [ ] **Firefox** — Dark mode looks correct
- [ ] **Safari** — Light mode looks correct
- [ ] **Safari** — Dark mode looks correct
- [ ] **Mobile Chrome** — Light mode (default)
- [ ] **Mobile Chrome** — Dark mode (system dark preference)
- [ ] **Mobile Safari** — Light mode 
- [ ] **Mobile Safari** — Dark mode

### Color Consistency Checks (Fixed elements)
- [ ] **Stage indicator (line 429)** — Color changes from light (#c8531a) → dark (#f0742a) ✅ Now using `var(--forge)`
- [ ] **"Open" tier heatgauge (line 607)** — Gradient adapts correctly ✅ Now using `var(--cold),var(--forge)`
- [ ] **"Pro" tier heatgauge (line 614)** — Gradient adapts correctly ✅ Now using `var(--forge),var(--forge-2)`
- [ ] **Bar fill gradient (line 291)** — Cold bar adapts ✅ Now using `var(--cold)`

### Accessibility Tests
- [ ] **Contrast ratio** — Light mode text/background meets WCAG AA (4.5:1)
- [ ] **Contrast ratio** — Dark mode text/background meets WCAG AA (4.5:1)
- [ ] **Focus indicators** — All interactive elements have visible focus states
- [ ] **Keyboard navigation** — All links/buttons reachable via Tab
- [ ] **Screen reader** — Headings properly structured (h1 → h2 → h3)
- [ ] **Screen reader** — Form inputs have proper labels
- [ ] **Color dependency** — Don't rely solely on color; shapes/icons also distinguish states

### Responsive Design
- [ ] **Desktop (1080px+)** — 3-column tier layout displays correctly
- [ ] **Tablet (760px-1080px)** — Cards and tiers stack appropriately
- [ ] **Mobile (< 760px)** — Single column, readable, navigable
- [ ] **Mobile nav** — .navlink items hidden, navigation still works
- [ ] **Retina displays** — Graphics render crisply (no pixelation)

### Animation & Motion
- [ ] **Forge animation** — .forgeline animation plays smoothly (7s loop)
- [ ] **Button hover** — Transform and shadow transitions feel smooth
- [ ] **prefers-reduced-motion** — Animation disabled when set; no jumpy layout shifts

## Skills & Functionality ✅

### Plugin Installation
- [ ] **Headless test** — `claude -p "..." --plugin-dir .` works
- [ ] **Agent behavior** — analyzing-data skill auto-triggers on data questions
- [ ] **Bootstrap** — using-maxforge loads at session start
- [ ] **All 4 skills** — Can manually invoke each if needed

### Documentation
- [ ] **README.md** — Quickstart command runs without errors
- [ ] **docs/research-to-execution-workflow.md** — Exists and describes pipeline
- [ ] **docs/eval-report.md** — Present with eval methodology and results
- [ ] **Skill files** — Each .md has proper YAML frontmatter (name, description)

## Performance ✅

- [ ] **Page load time** — < 2s on 3G throttle
- [ ] **CSS size** — Inline styles don't exceed 50KB
- [ ] **DOM depth** — No excessive nesting (> 15 levels)
- [ ] **Render blocking** — Critical CSS loaded before paint

## Security ✅

- [ ] **No hardcoded secrets** — API keys, tokens not visible in HTML/JS
- [ ] **Links sanitized** — External links use HTTPS where applicable
- [ ] **XSS risk** — No user input rendered without escaping (N/A for static site)

---

## Tester Sign-Off

| Test Area | Status | Notes |
|-----------|--------|-------|
| Dark Mode | ⏳ Pending | Run on real devices |
| Accessibility | ⏳ Pending | Use axe DevTools or Lighthouse |
| Responsive | ⏳ Pending | Test at 320px, 768px, 1440px |
| Skills | ⏳ Pending | Verify eval suite runs |
| Performance | ⏳ Pending | Check WebPageTest.org |
| Security | ⏳ Pending | Review for credentials |

---

## How to Test Locally

### Dark Mode Toggle (Chrome DevTools)
1. Open DevTools (`F12`)
2. Click three dots → More tools → **Rendering**
3. Scroll to **Emulate CSS media feature prefers-color-scheme**
4. Switch between "prefers-color-scheme: light" and "dark"

### Accessibility Audit (Lighthouse)
1. DevTools → **Lighthouse** tab
2. Select **Accessibility**
3. Run audit
4. Fix any reported contrast or ARIA issues

### Responsive Testing
1. DevTools → **Toggle device toolbar** (`Ctrl+Shift+M`)
2. Test at: 320px (mobile), 768px (tablet), 1440px (desktop)

### Performance
1. DevTools → **Network** tab
2. Throttle to **Slow 3G**
3. Reload page
4. Check "Largest Contentful Paint" (target: < 2.5s)

---

**Last Updated:** 2026-07-08  
**Next Review:** After production deployment
