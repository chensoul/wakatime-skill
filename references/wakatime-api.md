# WakaTime API (this skill)

Companion to **[SKILL.md](../SKILL.md)** — base URL, auth, **`stats`** vs **`summaries`**, presets, **curl**, timeouts.

## What this skill calls

[WakaTime](https://wakatime.com) is a **hosted (SaaS)** product. The CLI uses a fixed origin (**[`WAKATIME_ORIGIN` in `scripts/wakatime_query.py`](../scripts/wakatime_query.py)** = `https://wakatime.com`).

## Environment

| Variable | Required | Notes |
|----------|----------|--------|
| **`WAKATIME_API_KEY`** | Yes | Secret API key; **HTTP Basic** (key only, base64). |

## Official documentation

- Developers: <https://wakatime.com/developers>
- API overview: <https://wakatime.com/api/>

## Base URL

All paths in this CLI:

```text
https://wakatime.com/api/v1/...
```

## Authentication

```http
Authorization: Basic <base64(api_key)>
Accept: application/json
```

[WakaTime Developers — Authentication](https://wakatime.com/developers#authentication) expects the secret API key **base64-encoded as the payload** (then prefixed with `Basic `), not `username:password` form. OAuth / `api_key` query parameters also exist in their docs; **this CLI uses Basic only**.

## CLI output (matches `wakatime_query.py`)

| Case | Stream | Notes |
|------|--------|--------|
| Success | stdout | JSON; most subcommands use **indented** JSON. **`health`** prints one-line **`{"healthy": …}`**. |
| HTTP/API error (non-`health`) | stderr | JSON with **`http_status`** / **`error`**; exit **1**. |
| HTTP/network error (`health` only) | stdout then exit **1** | Prints **`{"healthy": false}`** on stdout (does **not** use the stderr JSON shape above). **`URLError`** same. |
| Network / URL error (other commands) | stderr | Text message; exit **2**. |
| Non-JSON success body (other commands) | stderr | Plain-text parse error; exit **1**. |

## Endpoints used by this CLI (GET)

| Subcommand | Path | Notes |
|------------|------|--------|
| `health` / `projects` | `/api/v1/users/current/projects` | `health`: HTTP **200** → healthy JSON |
| `status-bar` | `/api/v1/users/current/statusbar/today` | |
| `all-time-since` | `/api/v1/users/current/all_time_since_today` | |
| `stats <range>` | `/api/v1/users/current/stats/{range}` | `{range}` = **path** segment |
| `summaries` | `/api/v1/users/current/summaries` | `start`+`end` **or** query `range=` |

### Two different “range” concepts

| Command | Meaning | Example |
|---------|---------|--------|
| **`stats <range>`** | **Path** after `/stats/` — [documented values](https://wakatime.com/developers#stats): `last_7_days`, `last_30_days`, `last_6_months`, `last_year`, `all_time`, `YYYY`, `YYYY-MM` | `stats last_7_days` |
| **`summaries`** | **Query** `range=` — [Summaries](https://wakatime.com/developers#summaries): **Title Case** presets and **snake_case** forms (e.g. **`last_7_days`**, **`this_month`**) are both accepted by the API | `summaries --range "Last 7 Days"` or `summaries --range last_7_days` |

**Path vs query:** **`stats`** still needs the **path** segment form (e.g. `last_7_days`), not a spaced Title Case string — e.g. **`stats "Last 7 Days"`** is wrong. For that window use **`summaries --range "Last 7 Days"`** or **`summaries --range last_7_days`**.

### Stale stats (free plan)

For **stats** (and similar), WakaTime notes that on the **free** plan, ranges **≥ ~1 year** may be computed asynchronously — check **`is_up_to_date`** and **retry** if stale. See [Stats](https://wakatime.com/developers#stats).

## Stats: path `{range}`

Sent as **`/api/v1/users/current/stats/{range}`** (percent-encoded when needed). Confirm current list in [WakaTime — Stats](https://wakatime.com/developers#stats).

**Calendar `YYYY`:** If the year is still **in progress**, **`/stats/{YYYY}`** may respond with **400** `Invalid time range` (observed on wakatime.com). Prefer **`YYYY-MM`**, rolling presets (`last_7_days`, …), or a **completed** year.

**CLI flags:**

| Flag | Query | Meaning |
|------|-------|--------|
| `--timeout N` | `timeout` | Keystroke timeout (**API**), not HTTP socket (**HTTP stays 60 s**) |
| `--writes-only true\|false` | `writes_only` | |

## Summaries: query `range` presets

Per [Summaries](https://wakatime.com/developers#summaries), the `range` query parameter accepts documented presets. The API accepts common forms in **Title Case** (often with spaces) and **snake_case**, for example:

- **Title Case:** `Today`, `Yesterday`, `Last 7 Days`, `Last 7 Days from Yesterday`, `Last 14 Days`, `Last 30 Days`, `This Week`, `Last Week`, `This Month`, `Last Month`
- **snake_case (examples):** `today`, `yesterday`, `last_7_days`, `last_14_days`, `last_30_days`, `this_month`, `last_month` — no shell quotes when there are no spaces

CLI: **`--range "Last 7 Days"`** or **`--range last_7_days`**. **`--range`** and **`--start`/`--end`** are **mutually exclusive**.

**Optional query flags (CLI)** — valid with **either** **`--range`** **or** **`--start`/`--end`** (combine as needed):

| CLI flag | Query param | Notes |
|----------|-------------|--------|
| `--project NAME` | `project` | Filter by project name |
| `--branches A,B` | `branches` | Comma-separated branch names |
| `--timezone TZ` | `timezone` | IANA TZ (e.g. `America/New_York`) |
| `--timeout N` | `timeout` | Keystroke timeout (**API**); HTTP client stays **60** s |
| `--writes-only true\|false` | `writes_only` | |

Examples with **`--range`** + optional filters:

```bash
# timezone → query param timezone=
python3 scripts/wakatime_query.py summaries --range last_7_days --timezone America/New_York
# project + branches → filter result set
python3 scripts/wakatime_query.py summaries --range "Last 14 Days" --project "my-app" --branches main,develop
# writes_only + timeout → API query params (HTTP client still 60s)
python3 scripts/wakatime_query.py summaries --range last_30_days --writes-only true --timeout 300
```

## Full CLI examples

Canonical copy-paste examples for the bundled CLI (SKILL.md keeps a short subset and links here).

```bash
export WAKATIME_API_KEY="…"

# --- CLI help ---
python3 scripts/wakatime_query.py --help
python3 scripts/wakatime_query.py summaries --help

# --- health / projects / status-bar / all-time (see Endpoints table) ---
python3 scripts/wakatime_query.py health
python3 scripts/wakatime_query.py health --timeout 30          # HTTP socket timeout (seconds)
python3 scripts/wakatime_query.py projects
python3 scripts/wakatime_query.py projects --timeout 120
python3 scripts/wakatime_query.py status-bar
python3 scripts/wakatime_query.py all-time-since

# --- stats: path /users/current/stats/{range} ---
python3 scripts/wakatime_query.py stats last_7_days
python3 scripts/wakatime_query.py stats last_30_days
python3 scripts/wakatime_query.py stats last_6_months
python3 scripts/wakatime_query.py stats last_year
python3 scripts/wakatime_query.py stats all_time
python3 scripts/wakatime_query.py stats 2025
python3 scripts/wakatime_query.py stats 2025-03 --writes-only true
python3 scripts/wakatime_query.py stats last_7_days --timeout 300   # API query timeout, not HTTP

# --- summaries --range: query ?range=... (Title Case and/or snake_case) ---
# Today / yesterday
python3 scripts/wakatime_query.py summaries --range Today
python3 scripts/wakatime_query.py summaries --range today
python3 scripts/wakatime_query.py summaries --range Yesterday
python3 scripts/wakatime_query.py summaries --range yesterday
# Week / month presets
python3 scripts/wakatime_query.py summaries --range "This Week"
python3 scripts/wakatime_query.py summaries --range "Last Week"
python3 scripts/wakatime_query.py summaries --range "This Month"
python3 scripts/wakatime_query.py summaries --range this_month
python3 scripts/wakatime_query.py summaries --range "Last Month"
python3 scripts/wakatime_query.py summaries --range last_month
# Rolling N-day windows
python3 scripts/wakatime_query.py summaries --range "Last 7 Days"
python3 scripts/wakatime_query.py summaries --range last_7_days
python3 scripts/wakatime_query.py summaries --range "Last 7 Days from Yesterday"
python3 scripts/wakatime_query.py summaries --range "Last 14 Days"
python3 scripts/wakatime_query.py summaries --range last_14_days
python3 scripts/wakatime_query.py summaries --range "Last 30 Days"
python3 scripts/wakatime_query.py summaries --range last_30_days

# --- summaries --range + filters ---
python3 scripts/wakatime_query.py summaries --range last_7_days --timezone America/New_York
python3 scripts/wakatime_query.py summaries --range "Last 7 Days" --project "my-app" --branches main,develop
python3 scripts/wakatime_query.py summaries --range Today --timezone Europe/London
python3 scripts/wakatime_query.py summaries --range yesterday --writes-only true
python3 scripts/wakatime_query.py summaries --range last_30_days --writes-only true --timeout 300

# --- summaries: --start + --end (fixed YYYY-MM-DD window) ---
python3 scripts/wakatime_query.py summaries --start 2025-03-01 --end 2025-03-07
python3 scripts/wakatime_query.py summaries --start 2025-03-01 --end 2025-03-07 --timezone America/New_York
python3 scripts/wakatime_query.py summaries --start 2025-03-01 --end 2025-03-07 --branches main,develop
python3 scripts/wakatime_query.py summaries --start 2025-03-18 --end 2025-03-18 --project "my-app" --writes-only false

# --- Debug ---
python3 scripts/wakatime_query.py -d projects
```

Preset spellings are defined by [WakaTime Summaries](https://wakatime.com/developers#summaries); if a **snake_case** value errors, use the **Title Case** string from the docs for the same window.

## CLI vs HTTP timeouts

| Subcommand | HTTP client |
|------------|-------------|
| `health` / `projects` / `status-bar` / `all-time-since` | **`--timeout`** = socket; default **15** s (`health`) or **60** s |
| `stats` / `summaries` | HTTP **60** s; **`--timeout`** = **API** keystroke parameter |

## curl examples

```bash
# Build Authorization header per WakaTime: base64(API_KEY) only (see developers#authentication)
API_KEY='your-api-key'
B64=$(printf '%s' "$API_KEY" | base64 | tr -d '\n')
BASE='https://wakatime.com/api/v1/users/current'

# GET .../projects (same resource the CLI uses for health)
curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$BASE/projects"

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$BASE/statusbar/today"

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$BASE/all_time_since_today"

# Stats: range is a path segment
curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$BASE/stats/last_7_days"

# Summaries: preset via query ?range=
curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode 'range=Today' \
  "$BASE/summaries"

curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode 'range=yesterday' \
  "$BASE/summaries"

curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode 'range=Last 7 Days' \
  "$BASE/summaries"

curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode 'range=last_7_days' \
  "$BASE/summaries"

# Summaries: range + optional query params
curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode 'range=last_7_days' \
  --data-urlencode 'timezone=America/New_York' \
  --data-urlencode 'project=my-app' \
  --data-urlencode 'branches=main,develop' \
  --data-urlencode 'timeout=300' \
  --data-urlencode 'writes_only=true' \
  "$BASE/summaries"

# Summaries: fixed window ?start=&end=
curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode 'start=2025-03-01' \
  --data-urlencode 'end=2025-03-07' \
  --data-urlencode 'timezone=America/New_York' \
  "$BASE/summaries"

curl -sS -G -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  --data-urlencode 'range=Last 14 Days' \
  --data-urlencode 'project=my-app' \
  "$BASE/summaries"
```

## Future endpoints

Teams, leaderboards, etc. can be added under the same skill (**`name: wakatime`**) over time.
