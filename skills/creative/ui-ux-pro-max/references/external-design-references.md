# External UI/UX Reference Libraries

Useful online services that complement the internal Hermes design skills with real-world screenshots, flows, and patterns. Most are **paid or freemium**; check subscription status before relying on them in a session.

## Why Use External References

Internal skills (`ui-ux-pro-max`, `popular-web-designs`, `claude-design`) provide:
- Design strategy and style direction
- Exact design-system tokens for well-known brands
- Process for turning a brief into a mockup

External reference libraries add:
- Real screenshots of specific screens and flows
- Current product UI from live apps/sites
- Visual examples of niche patterns not covered internally

Rule of thumb: **internal skills first** for strategy and tokens; **external libraries second** for concrete visual examples.

## Service Catalog

| Service | URL | Pricing | Best For | Hermes Pairing |
|---------|-----|---------|----------|----------------|
| **Refero** | https://refero.design/ | Paid (limited free) | Page types, flows, AI research mode, MCP | `claude-design`, `sketch`, `popular-web-designs` |
| **Mobbin** | https://mobbin.com/ | Paid | Mobile app patterns, iOS/Android screenshots | `sketch`, `claude-design` |
| **Page Collective** | https://pagecollective.com/ | Freemium | Landing page inspiration, SaaS marketing | `claude-design`, `popular-web-designs` |
| **Screenlane** | https://screenlane.com/ | Freemium | UI screenshots, components, email flows | `claude-design`, `sketch` |
| **SaaS Interface** | https://saasinterface.com/ | Paid | SaaS dashboard/component patterns | `ui-ux-pro-max`, `popular-web-designs` |
| **UX Archive** | https://uxarchive.com/ | Free | Mobile user flows, task completion | `sketch`, `claude-design` |
| **Godly** | https://godly.website/ | Free | Awwwards-style web design showcase | `popular-web-designs`, `claude-design` |
| **Awwwards** | https://www.awwwards.com/ | Freemium | Award-winning sites, trends, portfolios | `popular-web-designs`, `claude-design` |
| **UI Patterns** | https://ui-patterns.com/ | Free | Pattern definitions and usage rules | `ui-ux-pro-max` |
| **Little Big Details** | https://littlebigdetails.com/ | Free | Micro-interaction inspiration | `claude-design`, `popular-web-designs` |

## Refero — Quick Reference

- **What it is:** library of real product screens organized by page type, flow, component, and brand
- **AI research mode:** describe task → get analyzed references with reasoning
- **MCP integration:** can be connected to agents (requires subscription + API access)
- **Pricing:** paid; free plan is limited
- **Use when:** you need a concrete screenshot of a specific flow (e.g. "how do 5 products do onboarding?")
- **Don't use when:** the project already has an internal reference (e.g. pentajunior.ru for pentajunior-v2)

## Workflow

```
User: "Сделай onboarding для нового сервиса"
↓
Internal: ui-ux-pro-max → style + anti-patterns for SaaS onboarding
↓
Internal/External: popular-web-designs or Refero → concrete examples
↓
Internal: sketch / claude-design → throwaway mockups under our brand
↓
Implementation in repo
```

## Important Caveats

1. **Subscription required.** Most of these services are paid. Do not assume access unless the user confirms a subscription.
2. **Copyright and cloning.** References show how others solved problems; do not clone distinctive branded UI or proprietary flows.
3. **Internal reference wins.** For existing projects, always check the live site or current repo first. External libraries are inspiration, not the source of truth.
4. **Russia access.** Some services (Google Fonts, Awwwards assets) may be slow or blocked. Prefer self-hosted fonts and local screenshots when possible.

## Related

- `../SKILL.md` — main ui-ux-pro-max skill
- `references/ui-ux-pro-max-design-database.md` — detailed CSV database reference
- `~/obsidian-memory/Design/Refero — UI UX Reference Library.md` — Obsidian note for Refero
