# BALTER brand skill

The **BALTER Markenhandbuch 2.0** (Balter GmbH, Security division, balter.de) as one skill for AI
agents. One file, [`balter-brand/SKILL.md`](balter-brand/SKILL.md), holds every rule of the brand
book with a router by task, so the agent decides itself which part a job needs: logo, colour, type,
the frame with the rounded window, motion, components, charts, schemas, product images, social
posts and reels, video, Brevo newsletters, German copy, design tokens.

The folder also carries the logos (`assets/logo/`), the design tokens (`assets/tokens.css`), the
**device library** (`assets/devices/`: every device as real photo and as vector illustration, named
by article number, indexed in `devices.json`) and a generator that draws the technical wiring plan for EVO HD as an A3 sheet
(`scripts/wiring_plan.py`, Python 3, no packages).

## Install

**Any agent, one command** ([skills CLI](https://github.com/vercel-labs/skills); Claude Code,
Codex, Cursor and others):

```bash
npx skills add BalterMarketing/balter-brand-skill
```

**Claude Code**: for all projects (or copy into `.claude/skills/` of one project):

```bash
git clone https://github.com/BalterMarketing/balter-brand-skill /tmp/balter-brand-skill && cp -R /tmp/balter-brand-skill/balter-brand ~/.claude/skills/
```

**Codex CLI**: for all projects (or copy into `.agents/skills/` of one project):

```bash
git clone https://github.com/BalterMarketing/balter-brand-skill /tmp/balter-brand-skill && cp -R /tmp/balter-brand-skill/balter-brand ~/.codex/skills/
```

**Any other chat assistant:** paste `balter-brand/SKILL.md` into the chat and say
"Arbeite nach dem BALTER Markenhandbuch".

## Use

Ask in plain words. The agent loads the skill when the request is about Balter:

- „Baue einen Instagram-Post 4:5 für EVO HD Touch nach dem BALTER Markenhandbuch.“
- „Baue einen Verdrahtungsplan: EG bis 3.OG, je zwei Wohneinheiten, EVO-HD-8FAM, Türöffner intern.“
- „Prüfe diese Landingpage gegen das BALTER Markenhandbuch.“

## Updating

The source of truth is the brand book. This repository is published from it; change the rules
there first, then update `SKILL.md` here with a new `metadata.version`.

© Balter GmbH, Langenfeld. The BALTER name, logo and eagle mark are trademarks of Balter GmbH and
may only be used for work on behalf of Balter.
