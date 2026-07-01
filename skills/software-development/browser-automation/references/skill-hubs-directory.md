# Hermes Skill Hubs Directory

URLs and characteristics of skill marketplaces compatible with Hermes Agent. Discovered during search session 2026-05-03.

## Official / Verified

### 1. Hermes Skills Hub (Nous Research)
- **URL:** https://hermes-agent.nousresearch.com/docs/skills/
- **Type:** Official registry
- **Size:** 670 skills from 4 registries
- **Install:** `hermes skills install <name>` or `hermes hub search <keyword>`
- **Trust:** Official, maintained by Nous Research

### 2. HermesHub (Security-Scanned)
- **URL:** https://www.hermeshub.xyz/
- **Type:** Community marketplace with security scan
- **Features:** Each skill undergoes security review before listing
- **Trust:** Community-curated + automated security checks

### 3. HermesHub (Vercel Mirror)
- **URL:** https://hermes-skills-hub.vercel.app/
- **Type:** Alternative UI for HermesHub
- **Same registry as hermeshub.xyz, different frontend**

### 4. AgentSkills.io
- **URL:** https://agentskills.io
- **Type:** Universal skill standard (SKILL.md format)
- **Compatibility:** Hermes is AgentSkills-compatible
- **Features:** Open format, cross-agent portability
- **Standard:** `SKILL.md` + `scripts/` + `references/` + `assets/` directory layout

## Community / Curated

### 5. Awesome Hermes Agent
- **URL:** https://github.com/0xNyk/awesome-hermes-agent
- **Type:** GitHub awesome-list
- **Content:** Curated list of skills, tools, integrations, resources
- **Usage:** Browse README, follow links to individual repos

## Partially Compatible

### 6. ClawHub
- **URL:** https://clawhub.ai
- **Type:** OpenClaw marketplace
- **Compatibility:** ⚠️ Partial
- **Issue:** OpenClaw is Node.js/TypeScript-based; skills may need porting to Python/Hermes format
- **Migration:** Some skills transferable with adaptation; not drop-in

## Search Tips

To find skills on a topic via web search:
```
hermes agent skills <topic> github
```

Example queries that yield good results:
- `hermes agent skills docker github`
- `hermes agent skills testing github`
- `hermes agent skills database github`

## Installation

```bash
# From official hub
hermes skills install <skill-name>

# Search first
hermes hub search <keyword>

# From GitHub repo directly
hermes skills install github:user/repo
```

## Notes

- Prefer official Nous Research hub for security-critical skills
- Community hubs (hermeshub.xyz, awesome-list) good for specialized tools
- Always review `SKILL.md` before installing from unknown sources
- ClawHub skills require manual adaptation — not recommended for quick tasks
