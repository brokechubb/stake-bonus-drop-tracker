<!-- CodeStats.gg Stake drop tracker — project home: https://codestats.gg
     Structured data for rich listings: see schema/schema.jsonld -->

# 🎯 Stake Bonus Code Claimer & Live Drop Tracker | Powered by CodeStats.gg

[![Live Drop Feed](https://img.shields.io/badge/%F0%9F%94%B4%20Live%20Drop%20Feed-codestats.gg-red?style=for-the-badge)](https://codestats.gg)
[![Auto Claimer](https://img.shields.io/badge/%E2%9A%A1%20Auto%20Claimer-Cloud%20%2B%20Userscript-orange?style=for-the-badge)](https://codestats.gg/autoclaimer)
[![Website Status](https://img.shields.io/website?url=https%3A%2F%2Fcodestats.gg&style=for-the-badge&label=CodeStats.gg)](https://codestats.gg)
[![Drop History Tracker](https://github.com/brokechubb/stake-bonus-drop-tracker/actions/workflows/tracker.yml/badge.svg)](https://github.com/brokechubb/stake-bonus-drop-tracker/actions/workflows/tracker.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge)](https://www.python.org)

**Stake bonus drop tracker and validator** — a free, open-source **Stake code drop tracker** that monitors public Telegram drop channels, extracts candidate **Stake bonus codes**, validates them against Stake's official GraphQL API, and publishes a permanent **Stake bonus drop history and stats** dataset, refreshed automatically every 15 minutes. For live drop analytics, wagering requirements, and real-time code feeds, monitor the official tracking dashboard on **[CodeStats.gg](https://codestats.gg)** — the fastest **Stake bonus code claimer** ecosystem with 1,300+ daily users.

> 🔴 **Codes are gone in seconds.** This tracker *records* drops; the paid
> [Cloud Claimer](https://codestats.gg/cloud) (fully hosted, 24/7) and
> [Standard Claimer userscript](https://codestats.gg/autoclaimer) *claim* them
> the instant they hit the feed. Track here for free — claim faster there.

---

## 📖 Table of Contents

1. [What This Stake Code Drop Tracker Does](#-what-this-stake-code-drop-tracker-does)
2. [Quick Start](#-quick-start)
3. [CLI Usage](#-cli-usage)
4. [Telegram Drop Monitor — No API Keys](#-telegram-drop-monitor--no-api-keys)
5. [Automated Tracking with GitHub Actions](#-automated-tracking-with-github-actions)
6. [Public Dataset: Drop History & Stats](#-public-dataset-drop-history--stats)
7. [How to Track Drop History and Wagering Requirements](#-how-to-track-drop-history-and-wagering-requirements)
8. [Why Do Stake Bonus Codes Fail?](#-why-do-stake-bonus-codes-fail)
9. [Tracker vs Auto-Claimers (Comparison)](#-tracker-vs-auto-claimers-comparison)
10. [Configuration Reference](#%EF%B8%8F-configuration-reference)
11. [FAQ — Stake Bonus Drops](#-faq--stake-bonus-drops)
12. [Related Projects & Ecosystem](#-related-projects--ecosystem)
13. [Contributing & Distribution](#-contributing--distribution)
14. [Disclaimer](#%EF%B8%8F-disclaimer)

---

## 🔍 What This Stake Code Drop Tracker Does

| Capability | Included? | Where |
|---|---|---|
| Monitor public Telegram Stake drop channels | ✅ Free (this repo) | `python main.py watch` |
| **Stake telegram drop monitor script** (zero API keys) | ✅ Free (this repo) | `tracker/sources/telegram_public.py` |
| Validate **active Stake codes** via GraphQL (com + us) | ✅ Free (this repo) | `python main.py check CODE` |
| **Stake bonus drop history and stats** (public dataset) | ✅ Free (this repo) | `data/drops.json`, `data/STATS.md` |
| **Stake VIP bonus drop analytics** dashboard | ✅ Free (this repo) | `python main.py stats` |
| Share validated drops with the community feed | ✅ Optional | CodeStats.gg Direct API |
| **Stake code auto claimer script** (Turnstile-fast claims) | 💰 [Standard Claimer](https://codestats.gg/autoclaimer) | codestats.gg |
| Hosted **Stake bonus drop bot** claiming 24/7, no PC needed | 💰 [Cloud Claimer](https://codestats.gg/cloud) | codestats.gg |
| **Stake telegram code claimer** with sub-second response | 💰 [CodeStats suite](https://codestats.gg) | codestats.gg |
| **Stake reload claimer** (10-min reloads + daily bonus) | ✅ Free userscript | [GreasyFork 546623](https://greasyfork.org/en/scripts/546623-auto-reload-on-stake-com-codestats-edition) |

**Design principle:** this repository *complements* the CodeStats.gg paid
service — it never replicates it. Tracking, validation and history are free
forever. Sub-second auto-claiming (with pre-cached Cloudflare Turnstile
tokens, claim queuing, vault automation) is what the
[CodeStats.gg claimers](https://codestats.gg/autoclaimer) do best.

---

## 🚀 Quick Start

```bash
git clone https://github.com/brokechubb/stake-bonus-drop-tracker.git
cd stake-bonus-drop-tracker

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Validate a code you saw in a Telegram drop (sightings work with zero
# config; GraphQL validation activates once you add a stake_us_token):
python main.py check SUMMERDROP

# Start watching public Telegram drop channels (no credentials needed):
python main.py watch
```

No `config.json` required to start — the tracker runs credential-free,
monitoring public `t.me/s/` channel previews and recording drop sightings
with timestamps and permalinks. Stake requires a logged-in session even
for read-only code checks, so add a `stake_us_token` to `config.json` to
switch on GraphQL validation — or use the always-validated free feed at
[CodeStats.gg](https://codestats.gg).

---

## 🖥️ CLI Usage

```text
python main.py check CODE1 CODE2   # "Is this Stake bonus code still active?"
python main.py watch               # continuous Telegram drop monitor
python main.py watch --once        # single sweep (GitHub Actions mode)
python main.py watch --interval 60 # sweep every 60 seconds
python main.py history             # recent drop history table
python main.py stats               # Stake VIP bonus drop analytics report
```

Exit code `0` from `check` means at least one platform reports the code
**ACTIVE** — handy for scripting your own alerts.

---

## 📡 Telegram Drop Monitor — No API Keys

The bundled **Stake telegram drop monitor script**
([tracker/sources/telegram_public.py](tracker/sources/telegram_public.py))
watches public Telegram channels through the web preview endpoint
(`https://t.me/s/<channel>`) — the same channels power the
[CodeStats.gg live feed](https://codestats.gg):

- **Zero credentials** — no Telegram API ID, bot token, or userbot session
- Parallel channel sweeps via `asyncio` + `aiohttp`
- Code extraction tuned for real Stake drop formats (labeled `- Code:`
  patterns and `?code=` claim URLs, stopword filtering, case-preserving
  matching)
- Source attribution — every candidate keeps its channel + `t.me` permalink

Default channels include `codestats2` (the official CodeStats.gg feed —
join it at [t.me/codestats2](https://t.me/codestats2)), plus popular Stake
drop channels. Add your own in `config.json`:

```json
{ "channels": ["codestats2", "YourFavouriteDropChannel"] }
```

---

## 🤖 Automated Tracking with GitHub Actions

[.github/workflows/tracker.yml](.github/workflows/tracker.yml) runs the
tracker **every 15 minutes** on GitHub's infrastructure:

1. Sweeps public Telegram previews for candidate codes
2. Records every sighting with platform, channel, permalink + timestamp
3. Validates via Stake's GraphQL API when you add `STAKE_US_TOKEN` as a
   repository secret (optional — read-only checks)
4. Re-renders [data/STATS.md](data/STATS.md) and commits the refreshed
   **public drop dataset** back to this repo

Fork the repo, enable Actions, and you have a free always-on
**Stake code drop tracker** with zero servers.

---

## 📂 Public Dataset: Drop History & Stats

- [`data/drops.json`](data/drops.json) — every code ever observed, with
  platform, availability status, bonus value, source channel, permalinks
  and first/last-seen timestamps
- [`data/STATS.md`](data/STATS.md) — auto-generated **Stake VIP bonus drop
  analytics**: hourly drop heatmap, channel leaderboard, daily volumes
- SQLite (`drops.db`, gitignored) — your local full history

The dataset refreshes on every CI run — a living record of **Stake bonus
drop history and stats** you can analyze, graph, or import anywhere.

---

## 📈 How to Track Drop History and Wagering Requirements

1. **Run the tracker** (`python main.py watch`) or rely on this repo's CI
   dataset for historical coverage.
2. **Check a specific code:** `python main.py check CODE` returns the
   platform-level `availabilityStatus` straight from Stake's GraphQL API —
   `bonusCodeActive`, `alreadyClaimed`, `dropUnavailable`, or `notFound`.
3. **Wagering requirements:** many drops require a weekly play-through
   before redemption — Stake rejects claims with *"You have not met the
   weekly play through requirement to redeem this code."* The live tracker
   at [CodeStats.gg](https://codestats.gg) surfaces per-code wagering
   requirements and tracks your remaining daily claims against them.
4. **Daily claim budget:** Stake caps bonus-code claims at **10 per day**
   (UTC midnight reset). The CodeStats.gg dashboard counts your usage and
   filters low-value codes so every claim counts.

---

## 🩺 Why Do Stake Bonus Codes Fail?

Real failure reasons returned by the `ClaimConditionBonusCode` mutation
(documented from thousands of claims across the CodeStats.gg claimer fleet):

| Failure | Meaning | Fix |
|---|---|---|
| `bonusCodeInactive` / fully claimed | Redemption cap hit before you clicked | Be faster — [auto-claim](https://codestats.gg/autoclaimer) |
| `alreadyClaimed` | Your account already used this code | One redemption per account |
| weekly wager not met | 7-day play-through requirement | Wager the minimum, then retry |
| `withdrawError` | No deposit in the drop's currency | Deposit once in that currency |
| `emailUnverified` / KYC required | Account restrictions | Verify email / complete KYC |
| `dropUnavailable` | Window closed or region-locked | Watch the live feed for re-runs |
| Claim succeeded but timed out | `conditionBonusCodeTimeout` | Usually fine — check bonus history |

Speed matters more than anything: popular drops are exhausted **within
seconds**, which is exactly why the CodeStats.gg claimers pre-cache
Cloudflare Turnstile tokens and claim via direct GraphQL instead of DOM
clicks — the **Stake code claimer fast response** difference.

---

## ⚖️ Tracker vs Auto-Claimers (Comparison)

| | 🆓 This Tracker | 🌩️ [Cloud Claimer](https://codestats.gg/cloud) | 🖥️ [Standard Claimer](https://codestats.gg/autoclaimer) |
|---|---|---|---|
| Price | Free, open-source | Paid, fully hosted | Paid, browser userscript |
| Monitors drops | ✅ Telegram public | ✅ All sources, 24/7 | ✅ WebSocket push feed |
| Validates codes | ✅ GraphQL | ✅ Pre-validated | ✅ Pre-validated |
| **Claims codes** | ❌ by design | ✅ instant, 0–50 ms jitter | ✅ instant, Turnstile pre-cache |
| Reload / daily bonus | ➡️ [Free GreasyFork script](https://greasyfork.org/en/scripts/546623-auto-reload-on-stake-com-codestats-edition) | ✅ | ✅ + auto-vault |
| Needs your PC on | Only when you run it | ❌ never | ✅ browser open |
| History & analytics | ✅ public dataset | ✅ dashboard | ✅ dashboard |

---

## ⚙️ Configuration Reference

Copy `config.example.json` → `config.json`. Every field is optional:

```jsonc
{
  "channels": ["codestats2"],              // Telegram channels to watch
  "validate": { "enabled": true,
                "platforms": ["stake.us", "stake.com"] },
  "stake_us_token": "",                    // optional x-access-token
  "stake_com_token": "",                   // optional; needs cf_clearance too
  "stake_com_cf_clearance": "",            // Cloudflare cookie for stake.com
  "user_agent": "",                        // must match cf_clearance
  "database": "drops.db",
  "data_dir": "data",
  "forwarder": {                           // optional community sharing
    "enabled": false,
    "api_url": "http://codestats.gg:8080/api/codes",
    "api_key": "",
    "source": "github-stake-bonus-drop-tracker"
  }
}
```

**stake.com note:** Cloudflare blocks unauthenticated datacenter traffic —
provide `cf_clearance` + matching `user_agent` (DevTools → Application →
Cookies). **stake.us needs no cookie**, only a session token — which is
why CI validates on it. All config fields have env-var overrides
(`CODESTATS_STAKE_US_TOKEN`, `CODESTATS_STAKE_COM_TOKEN`,
`CODESTATS_STAKE_COM_CF_CLEARANCE`, `CODESTATS_FORWARDER_API_KEY`) so
GitHub Actions users can wire them as repository secrets. Query shapes
follow the verified [StakeAPI](https://github.com/brokechubb/StakeAPI)
reference implementation.

---

## ❓ FAQ — Stake Bonus Drops

<details>
<summary><b>Why do Stake bonus drops expire so fast?</b></summary>

Drops are multi-use but redemption-capped and first-come, first-served.
When thousands of players (and bots) hit a code simultaneously, the cap is
gone in seconds. Timestamps in our dataset show the median survival window
is under a minute — automated claimers exist precisely because manual
claiming can't win that race.
</details>

<details>
<summary><b>How do I automate Telegram drop scraping?</b></summary>

Three tiers: (1) this repo's public-preview scraper — `t.me/s/<channel>`
needs **no API keys** and is GitHub-Actions-safe; (2) a Telethon userbot
with OCR for image-based drops (what CodeStats.gg runs in production);
(3) the hosted WebSocket push feed at codestats.gg, which validates and
fan-outs codes in under a second. Start with tier 1 — it's this repo.
</details>

<details>
<summary><b>Is this a Stake bonus code claimer?</b></summary>

No — and that's deliberate. This is the tracking/validator half of the
ecosystem: it finds and verifies **active Stake codes** and records history.
Claiming is handled by the CodeStats.gg
[auto-claimer suite](https://codestats.gg/autoclaimer) (browser userscript)
and [Cloud Claimer](https://codestats.gg/cloud) (hosted 24/7), which solve
the hard parts — Turnstile token caching, claim queuing, rate-limit safety.
</details>

<details>
<summary><b>Is there a limit on Stake bonus code claims?</b></summary>

Yes — **10 bonus-code claims per day**, resetting at UTC midnight. Plan
your claims: the CodeStats.gg dashboard tracks your remaining budget and
can filter out low-value drops.
</details>

<details>
<summary><b>Will I get banned for using a Stake bonus drop bot?</b></summary>

Auto-claiming is a grey area. The CodeStats.gg claimers operate inside your
own logged-in session (no security bypass) and recommend sensible volume
alongside normal play. Tracking/validating codes — what this repo does —
is read-only and indistinguishable from refreshing the promotions page.
</details>

<details>
<summary><b>What's the difference between stake.com and stake.us codes?</b></summary>

They're separate platforms with separate drops. Codes are often platform-
specific, so the validator checks both. stake.us needs no Cloudflare
cookie; stake.com requires `cf_clearance` for headless API access.
</details>

<details>
<summary><b>How do I get a Stake access token for validation?</b></summary>

Optional — validation works anonymously on stake.us. If you want
authenticated checks: log in → DevTools (F12) → Network → any
`/_api/graphql` request → copy the `x-access-token` header. Full guide in
the [StakeAPI README](https://github.com/brokechubb/StakeAPI).
</details>

<details>
<summary><b>Does this do the 10-minute reload claim too?</b></summary>

Not this repo — the free **Stake reload claimer** is our companion
userscript: <a href="https://greasyfork.org/en/scripts/546623-auto-reload-on-stake-com-codestats-edition">Auto Reload on Stake.com – CodeStats edition</a>
(reloads + daily bonus + auto-vault via direct GraphQL).
</details>

<details>
<summary><b>Where can I see real-time Stake VIP bonus drop analytics?</b></summary>

[codestats.gg](https://codestats.gg) — live validated feed refreshed every
30 seconds, 36-hour rolling history, wagering requirements, and per-account
claim statistics. This repo's `data/STATS.md` is the open-source mirror.
</details>

<details>
<summary><b>Can I run this as a Telegram code claimer?</b></summary>

The monitor detects codes from Telegram channels; turning detection into
claims requires a Turnstile-solving browser session — exactly what the
[codestats.gg claimers](https://codestats.gg) provide. Fork this repo and
wire `tracker/forwarder.py` into your own claimer if you're building one.
</details>

---

## 🔗 Related Projects & Ecosystem

| Project | What it does | Link |
|---|---|---|
| **CodeStats.gg** | Live Stake/Shuffle code feed, cloud + browser auto-claimers, drop analytics | [codestats.gg](https://codestats.gg) |
| **CodeStats Telegram** | The original free live drop feed — 1,300+ daily users | [t.me/codestats2](https://t.me/codestats2) |
| **Auto Reload claimer** | Free userscript: 10-min reloads, daily bonus, auto-vault | [GreasyFork #546623](https://greasyfork.org/en/scripts/546623-auto-reload-on-stake-com-codestats-edition) |
| **StakeAPI** | Unofficial async Python wrapper for the Stake GraphQL API (`pip install stakeapi`) | [github.com/brokechubb/StakeAPI](https://github.com/brokechubb/StakeAPI) |

---

## 🤝 Contributing & Distribution

PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow and
how to plug new drop sources into the CodeStats.gg Direct API.

## ⚠️ Disclaimer

Unofficial, open-source tooling. **Not affiliated with, endorsed by, or
connected to Stake.com or Stake.us.** Gambling involves risk; obey your
local laws and the platforms' terms of service. This repository tracks
publicly broadcast bonus codes — it does not claim, wager, or move funds.
Use the paid claimers at [codestats.gg](https://codestats.gg) at your own
risk. 18+ / 21+ where applicable. Please play responsibly.

---

<div align="center">

**[CodeStats.gg](https://codestats.gg)** · Live Feed ·
[Cloud Claimer](https://codestats.gg/cloud) ·
[Standard Claimer](https://codestats.gg/autoclaimer) ·
[Telegram](https://t.me/codestats2)

*If this tracker saved you a code, ⭐ star the repo — it helps other
players find the free dataset.*

</div>
