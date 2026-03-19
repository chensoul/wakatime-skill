# wakatime-skill

[![ClawHub](https://img.shields.io/badge/ClawHub-wakatime--skill-blue)](https://clawhub.ai/skills/wakatime-skill)
[![ClawHub version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fclawhub.ai%2Fapi%2Fv1%2Fskills%2Fwakatime-skill&query=%24.skill.tags.latest&label=clawhub&prefix=v&color=blue)](https://clawhub.ai/skills/wakatime-skill)
[![ClawHub downloads](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fclawhub.ai%2Fapi%2Fv1%2Fskills%2Fwakatime-skill&query=%24.skill.stats.downloads&label=clawhub%20downloads&color=blue)](https://clawhub.ai/skills/wakatime-skill)
[![GitHub stars](https://img.shields.io/github/stars/chensoul/wakatime-skill?style=flat&logo=github)](https://github.com/chensoul/wakatime-skill)
[![License](https://img.shields.io/github/license/chensoul/wakatime-skill)](./LICENSE)
[![Publish to ClawHub](https://github.com/chensoul/wakatime-skill/actions/workflows/clawhub-publish.yml/badge.svg)](https://github.com/chensoul/wakatime-skill/actions/workflows/clawhub-publish.yml)

WakaTime coding stats (summaries, projects, today status, totals) via a small Python CLI.

## Install

Copy or symlink this folder so your agent discovers **`SKILL.md`** at the skill root.

**Python:** **3.10+** required (stdlib only, no dependencies). GitHub Actions CI runs tests on **3.10**.

## Configuration

| Variable | Required | Purpose |
|----------|----------|---------|
| `WAKATIME_API_KEY` | Yes | Key from your WakaTime account (**HTTP Basic**, key only). |

API host is **fixed** in code to **`https://wakatime.com`** ([WakaTime](https://wakatime.com)); no `WAKATIME_URL`.

## Run CLI

From the skill root (directory containing `SKILL.md`):

```bash
export WAKATIME_API_KEY="your-key"

python3 scripts/wakatime_query.py --help
python3 scripts/wakatime_query.py health                              # connectivity via /projects
python3 scripts/wakatime_query.py summaries --range "Last 7 Days"    # Title Case preset
python3 scripts/wakatime_query.py summaries --range last_7_days      # snake_case preset (same query param)
```

Full examples: **[references/wakatime-api.md](references/wakatime-api.md)** · Agent workflow: **[SKILL.md](SKILL.md)**.

## Tests

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Docs

- Agent instructions: [`SKILL.md`](SKILL.md)
- API notes: [`references/wakatime-api.md`](references/wakatime-api.md)
