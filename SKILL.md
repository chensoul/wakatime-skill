---
name: wakatime
description: >-
  Queries WakaTime coding statistics using the bundled stdlib-only Python CLI (summaries, stats,
  projects, today status bar, all-time-since, health). Use when the user wants WakaTime metrics,
  coding time, daily/rolling summaries, or official wakatime.com API access from the agent.
  Requires WAKATIME_API_KEY. API host is fixed to wakatime.com.
homepage: https://github.com/chensoul/wakatime-skill
repository: https://github.com/chensoul/wakatime-skill
metadata: {"openclaw": {"requires": {"env": ["WAKATIME_API_KEY"]}, "primaryEnv": "WAKATIME_API_KEY"}}
---

# WakaTime

## Instructions

1. **Scope:** Official **[wakatime.com](https://wakatime.com)** only. The script does not read a configurable base URL.
2. **Secrets:** Require **`WAKATIME_API_KEY`** in the environment; never paste the key into chat.
3. **Run location:** From the **skill root** (directory containing this file), invoke **[`scripts/wakatime_query.py`](scripts/wakatime_query.py)** with **Python 3.10+** (stdlib only).
4. **Output:** Success → JSON on stdout (**`health`**: one compact `{"healthy": …}` line; others: indented). API HTTP errors on **`stats`** / **`summaries`** / **`projects`** / **`status-bar`** / **`all-time-since`** → JSON with **`http_status`** on **stderr**, exit **1**. **`health`** on HTTP/network failure → **`{"healthy": false}`** on **stdout**, exit **1** (not the stderr error shape). Other commands: network errors → stderr text, exit **2**. Summarize key numbers for the user.
5. **Deep API semantics** (paths, `stats` vs `summaries` ranges, timeouts, curl): read **[references/wakatime-api.md](references/wakatime-api.md)** when needed.

## Requirements

| Item | Detail |
|------|--------|
| **Runtime** | **Python 3.10+**, stdlib only (uses PEP 604 union types). |
| **Env** | **`WAKATIME_API_KEY`** — HTTP **Basic** with key only (see WakaTime account) |
| **Network** | HTTPS to **`https://wakatime.com`** |
| **Registry** | `metadata.openclaw.requires.env` includes **`WAKATIME_API_KEY`** |

## Subcommands

| Subcommand | Role |
|------------|------|
| **`health`** | Connectivity via **`GET …/users/current/projects`** → `{"healthy": true\|false}` |
| **`projects`** | Full project list (same URL as health) |
| **`status-bar`** | Today’s status bar JSON |
| **`all-time-since`** | All-time total since today |
| **`stats <range>`** | **`/stats/{range}`** — range is a **path** segment |
| **`summaries`** | Daily summaries: **`--range`** *or* **`--start` + `--end`**; optional filters per help |

**`stats`** and **`summaries`** use different “range” meanings — do not assume the same strings work for both; see **[references/wakatime-api.md](references/wakatime-api.md)**.

## Examples

```bash
export WAKATIME_API_KEY="…"

python3 scripts/wakatime_query.py --help
python3 scripts/wakatime_query.py summaries --help

python3 scripts/wakatime_query.py health
python3 scripts/wakatime_query.py projects
python3 scripts/wakatime_query.py status-bar
python3 scripts/wakatime_query.py summaries --range last_7_days
python3 scripts/wakatime_query.py summaries --range "Last 7 Days" --timezone America/New_York
python3 scripts/wakatime_query.py stats last_7_days
python3 scripts/wakatime_query.py stats all_time

# Debug: log request URLs to stderr
python3 scripts/wakatime_query.py -d projects
```

**Timeouts:** On **`health`** / **`projects`** / **`status-bar`** / **`all-time-since`**, **`--timeout`** is the **HTTP** socket (seconds). On **`stats`** / **`summaries`**, **`--timeout`** is the WakaTime **API** keystroke parameter (HTTP client stays 60s). Details: **[references/wakatime-api.md](references/wakatime-api.md)**.

## Troubleshooting

- Verify **`WAKATIME_API_KEY`** and reachability of **wakatime.com**.
- For **`summaries`**, supply **`--range`** *or* **`--start` and `--end`** (not both); see **`summaries --help`** for **`--project`**, **`--branches`**, **`--timezone`**, **`--writes-only`**, **`--timeout`**.
- Large ranges on free accounts may return stale stats — see WakaTime [Stats](https://wakatime.com/developers#stats) (`is_up_to_date`).

## Additional resources

- **[references/wakatime-api.md](references/wakatime-api.md)** — endpoints, auth, **`stats` vs `summaries`**, presets, full CLI and **curl** examples
