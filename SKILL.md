---
name: wakatime
description: >-
  Wakatime coding stats (summaries, projects, today status, totals) via a small Python CLI.
homepage: https://github.com/chensoul/wakatime-skill
repository: https://github.com/chensoul/wakatime-skill
metadata: {"openclaw": {"requires": {"env": ["WAKATIME_API_KEY"]}, "primaryEnv": "WAKATIME_API_KEY"}}
---

# WakaTime

## When to use

The user wants **WakaTime**’s **official** service: stats, status bar, summaries, etc. All requests go to **[wakatime.com](https://wakatime.com)** — host is **not** configurable in this skill.

## Requirements

| Category | Detail |
|----------|--------|
| **Runtime** | **Python 3**, **stdlib only**. [`scripts/wakatime_query.py`](scripts/wakatime_query.py). Run from the **skill root**. |
| **Environment** | **`WAKATIME_API_KEY`** — from [WakaTime](https://wakatime.com); **HTTP Basic**, key only. |
| **Network** | Outbound **HTTPS** to **`https://wakatime.com`**. |
| **Registry** | **`metadata.openclaw.requires.env`** = **`["WAKATIME_API_KEY"]`**. |

No other environment variables are read by the CLI.

## Subcommands at a glance

| Subcommand | What it does |
|------------|----------------|
| **`health`** | **`GET …/users/current/projects`**; prints JSON `healthy: true/false` (connectivity; no separate public health URL in this CLI) |
| **`projects`** | Full JSON project list (same path as health check) |
| **`status-bar`** | Today’s status bar JSON |
| **`all-time-since`** | All-time total since today |
| **`stats <range>`** | **`/stats/{range}`** — `{range}` is a **path** segment (snake_case / `YYYY` / `YYYY-MM` / `all_time`) |
| **`summaries`** | Daily summaries: **`--range`** *or* **`--start` + `--end`**; optional **`--project`**, **`--branches`**, **`--timezone`**, **`--timeout`** (API), **`--writes-only`** |

**`stats`** vs **`summaries`:** different “range” semantics — see **[references/wakatime-api.md](references/wakatime-api.md)**.

## Prerequisites

1. Set **`WAKATIME_API_KEY`**.
2. Do **not** paste the key into chat.

## Usage

Run from the skill root.

```bash
# API key required for every subcommand (host is fixed to wakatime.com in the script).
export WAKATIME_API_KEY="…"

# --- Help: global and summaries-specific flags ---
python3 scripts/wakatime_query.py --help
python3 scripts/wakatime_query.py summaries --help

# --- health / projects: same URL; health only checks HTTP 200 → {"healthy": ...} ---
# --timeout here = HTTP socket seconds (health defaults 15s, others 60s).
python3 scripts/wakatime_query.py health
python3 scripts/wakatime_query.py health --timeout 30
python3 scripts/wakatime_query.py projects
python3 scripts/wakatime_query.py projects --timeout 120

# --- status-bar / all-time-since: today’s line + cumulative total ---
python3 scripts/wakatime_query.py status-bar
python3 scripts/wakatime_query.py all-time-since

# --- stats: <range> is a PATH segment (not the same as summaries --range) ---
python3 scripts/wakatime_query.py stats last_7_days      # rolling window
python3 scripts/wakatime_query.py stats last_30_days
python3 scripts/wakatime_query.py stats last_6_months
python3 scripts/wakatime_query.py stats last_year
python3 scripts/wakatime_query.py stats all_time
python3 scripts/wakatime_query.py stats last_7_days --timeout 300   # --timeout = API keystroke param, not HTTP
# Calendar stats: YYYY-MM works. For YYYY alone, prefer a *completed* year — stats for the *current* calendar year can return HTTP 400.
python3 scripts/wakatime_query.py stats 2025
python3 scripts/wakatime_query.py stats 2026-03 --writes-only true

# --- summaries --range: QUERY param range= (Title Case and/or snake_case) ---
# Today / yesterday
python3 scripts/wakatime_query.py summaries --range Today
python3 scripts/wakatime_query.py summaries --range today
python3 scripts/wakatime_query.py summaries --range Yesterday
python3 scripts/wakatime_query.py summaries --range yesterday
# Calendar week / month
python3 scripts/wakatime_query.py summaries --range "This Week"
python3 scripts/wakatime_query.py summaries --range "Last Week"
python3 scripts/wakatime_query.py summaries --range "This Month"
python3 scripts/wakatime_query.py summaries --range this_month
python3 scripts/wakatime_query.py summaries --range "Last Month"
python3 scripts/wakatime_query.py summaries --range last_month
# Rolling day windows
python3 scripts/wakatime_query.py summaries --range "Last 7 Days"
python3 scripts/wakatime_query.py summaries --range last_7_days
python3 scripts/wakatime_query.py summaries --range "Last 7 Days from Yesterday"
python3 scripts/wakatime_query.py summaries --range "Last 14 Days"
python3 scripts/wakatime_query.py summaries --range last_14_days
python3 scripts/wakatime_query.py summaries --range "Last 30 Days"
python3 scripts/wakatime_query.py summaries --range last_30_days

# --- summaries: optional filters (also valid with --start/--end) ---
# Maps to query: project, branches, timezone, timeout (API), writes_only.
python3 scripts/wakatime_query.py summaries --range last_7_days --timezone America/New_York
python3 scripts/wakatime_query.py summaries --range "Last 7 Days" --project "my-app" --branches main,develop
python3 scripts/wakatime_query.py summaries --range Today --timezone Europe/London
python3 scripts/wakatime_query.py summaries --range last_30_days --writes-only true --timeout 300

# --- summaries: explicit dates (cannot combine with --range) ---
python3 scripts/wakatime_query.py summaries --start 2026-03-01 --end 2026-03-07
python3 scripts/wakatime_query.py summaries --start 2026-03-01 --end 2026-03-07 --timezone America/New_York
python3 scripts/wakatime_query.py summaries --start 2026-03-01 --end 2026-03-07 --branches main,develop
# Single calendar day → same --start and --end
python3 scripts/wakatime_query.py summaries --start 2026-03-18 --end 2026-03-18 --project "my-app" --writes-only false

# --- Debug: log each request URL to stderr ---
python3 scripts/wakatime_query.py -d projects
```

Official allowed values for **`stats`** / **`summaries`**: [WakaTime Developers](https://wakatime.com/developers). Large ranges on **free** accounts may return **`is_up_to_date: false`** — retry later per [Stats](https://wakatime.com/developers#stats) docs.

## Interpreting output

Responses are JSON on stdout. Summarize totals and human-readable fields for the user.

On HTTP/API errors the CLI prints a JSON object to **stderr** (e.g. `http_status`, `error`) and exits non-zero — surface that to the user. **`health`** only returns a small **`{"healthy": …}`** object (connectivity), not full project JSON.

## If something fails

Check **`WAKATIME_API_KEY`** and network to **wakatime.com**. For **`summaries`**, use **`--range`** *or* **`--start` / `--end`**, and optionally **`--project`**, **`--branches`**, **`--timezone`**, **`--timeout`** (API), **`--writes-only`**. Run **`summaries --help`** for the full list.

Debug: **`-d`** / **`--debug`**. **`--timeout`** on `health` / `projects` / `status-bar` / `all-time-since` = **HTTP socket** time. On **`stats`** / **`summaries`**, **`--timeout`** = **API** keystroke parameter (HTTP **60** s).
