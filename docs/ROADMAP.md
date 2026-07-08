# Maxforge Lab Roadmap

**Future development, planned improvements, and community contributions.**

---

## Phase 1: Foundation ✅ Complete

- ✅ Core 4 skills (research, analyze, plan, execute)
- ✅ Bootstrap (using-maxforge)
- ✅ Landing site with dark mode
- ✅ Eval methodology & test cases
- ✅ Documentation (README, setup, contrib)
- ✅ MIT license & open source

---

## Phase 2: Quality & Testing (In Progress)

### Dark Mode & Accessibility
- ✅ CSS variable system
- ✅ Dark mode implementation (prefers-color-scheme)
- ✅ WCAG AA contrast validation
- ✅ Testing checklist
- 🔄 Browser testing suite (all major browsers)
- 🔄 Automated contrast checking in CI/CD

### Documentation
- ✅ Setup guide
- ✅ Contributing guidelines
- ✅ CSS variables reference
- 🔄 Video tutorials
- 🔄 Skill development walkthrough

### Testing Infrastructure
- ✅ QA shell script
- 🔄 GitHub Actions workflow
- 🔄 Automated dark mode testing
- 🔄 Performance benchmarks

---

## Phase 3: Ecosystem Expansion (Planned Q3 2026)

### Additional Skills
- [ ] **verify-assumptions** — Challenge assertions before committing
- [ ] **escalate-decisions** — Route complex calls to human review
- [ ] **audit-trail** — Document all agent decisions for compliance
- [ ] **cost-optimization** — Minimize API/compute overhead

### Harness Compatibility
- [ ] Cursor AI validation
- [ ] GitHub Copilot CLI testing
- [ ] Open WebUI integration
- [ ] LM Studio support

### Pro Tier Features
- [ ] Domain-specific skill packs
- [ ] Custom eval harness
- [ ] Version management
- [ ] Model transition testing

---

## Phase 4: Lab Tier Services (Planned Q4 2026)

### Custom Deployments
- [ ] Bespoke skill development
- [ ] Hardening SLA
- [ ] Your-stack integration
- [ ] Pressure-tested workflows

---

## Community Contributions Welcome

### Easy Starting Points

1. **Browser Testing** — Test dark mode on your device, report issues
2. **Documentation** — Add examples, improve clarity, fix links
3. **Skills** — Propose new skills following the framework
4. **Toolkits** — Build optional tools (see `/toolkits/`)

### Contribution Process

1. Fork the repo
2. Create a branch: `git checkout -b your-contribution`
3. Follow [`CONTRIBUTING.md`](../CONTRIBUTING.md)
4. Submit a PR with eval test cases
5. Address review feedback

### What We're Looking For

✅ **High-quality contributions:**
- Follows the skill format exactly
- Includes eval test cases (RED→GREEN→REFACTOR)
- Tested on ≥4 scenarios
- Holds on both Opus- and Haiku-class

❌ **What we can't merge:**
- Hardcoded secrets or credentials
- Breaking existing skills
- Unsupported platforms (must work headless)
- Non-MIT-licensed code

---

## Known Limitations & Caveats

### Current

- Auto-trigger validated on Claude Code only (other harnesses need per-harness verification)
- Skills enforce **process**, not **judgment** — a weaker model gains discipline, not substantive skill
- No built-in model fallback (if Claude 4.5 Opus isn't available, you need to handle selection)
- Terminal styling is hardcoded (not yet CSS variable integrated)

### Future Fixes

- [ ] Support other harnesses (Cursor, Copilot CLI, etc.)
- [ ] Model fallback strategy & auto-detection
- [ ] Terminal theme CSS variables
- [ ] WebUI for skill management
- [ ] Real-time eval metrics dashboard

---

## Success Metrics

We measure success by:

1. **Reliability** — Do all 4 skills fire when they should? (Target: 100% on Claude Code)
2. **Cross-domain** — Do they hold across medicine, finance, legal, ML, ops, marketing? (Target: ✅ all 8+)
3. **Model-agnostic** — Do they work on both Opus- and Haiku-class? (Target: ✅ both)
4. **Community** — Are developers building with these? (Monitor via issues/PRs)
5. **Production** — Are real workflows using this? (Collect testimonials)

---

## Getting Involved

### Report a Bug

[Open an issue](https://github.com/mancaf779-boop/-Max-Geld-Generation/issues) with:
- What you were trying to do
- What happened
- What you expected
- Your model/harness (Claude Code, Cursor, etc.)

### Request a Feature

[Discuss in issues](https://github.com/mancaf779-boop/-Max-Geld-Generation/issues) or email mancaf779@gmail.com

### Work with Us (Pro/Lab Tiers)

For domain-tuned skills, custom workflows, or hardened deployments:

**Email:** mancaf779@gmail.com

---

## Timeline

| Phase | Target | Status |
|-------|--------|--------|
| Phase 1: Foundation | Q2 2026 | ✅ Complete |
| Phase 2: Quality & Testing | Q3 2026 | 🔄 In Progress |
| Phase 3: Ecosystem | Q4 2026 | 📋 Planned |
| Phase 4: Lab Services | 2027 | 📋 Planned |

---

**Last Updated:** 2026-07-08  
**Next Review:** 2026-08-15
