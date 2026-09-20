# Stake Bonus Drop FAQ — Diagnostics & Troubleshooting

Companion deep-dive to the [README FAQ](../README.md#-faq--stake-bonus-drops).
Live validated answers 24/7: **[CodeStats.gg](https://codestats.gg)** ·
Telegram feed: [t.me/codestats2](https://t.me/codestats2)

## Why do Stake bonus codes fail?

The `ClaimConditionBonusCode` mutation returns machine-readable errors.
Ranked by real-world frequency across the CodeStats.gg claimer fleet:

| Rank | Error | Root cause | Fastest fix |
|---|---|---|---|
| 1 | `bonusCodeInactive` | Redemption cap exhausted — drops are multi-use but capped, first-come-first-served | Automate: [Standard Claimer](https://codestats.gg/autoclaimer) or [Cloud Claimer](https://codestats.gg/cloud) |
| 2 | weekly wager not met | 7-day play-through requirement below the drop's threshold | Check requirements *before* claiming; the codestats.gg feed shows them per drop |
| 3 | `alreadyClaimed` | Per-account one-time redemption | None — one per account |
| 4 | 10/day limit hit | Stake caps claims at 10 per UTC day | Budget claims; CodeStats dashboard counts remaining |
| 5 | `withdrawError` | Never deposited in the drop's currency | One small deposit unlocks that currency |
| 6 | `emailUnverified` / KYC | Account restrictions | Verify email / complete KYC |
| 7 | invalid Turnstile | Claim token expired (~150 s TTL) | Claimers pre-cache tokens in a LIFO pool — manual claims fail here most |

## What makes a "Stake code claimer fast response"?

Three engineering choices separate sub-second claimers from manual clicks:

1. **Direct GraphQL, no DOM** — posting `ClaimConditionBonusCode` straight
   to `/_api/graphql` skips modal navigation entirely (this is how the
   [Auto Reload claimer](https://greasyfork.org/en/scripts/546623-auto-reload-on-stake-com-codestats-edition)
   and CodeStats claimers work).
2. **Pre-cached Turnstile tokens** — tokens are browser-solved *ahead* of
   the drop and pooled (LIFO, ~150 s expiry), so claiming is a single POST.
3. **WebSocket push, not polling** — codes arrive as `code_drop` events the
   moment the feed validates them, instead of the client re-checking pages.

This repository deliberately ships *none* of the claiming machinery — it is
the free **Stake telegram drop monitor script** + history layer. Claiming
is the paid product: [codestats.gg/autoclaimer](https://codestats.gg/autoclaimer).

## How do I track Stake bonus drop history and stats?

- **This repo:** `python main.py watch` builds a local SQLite history and
  exports `data/drops.json` / `data/STATS.md` — or just fork it and let
  GitHub Actions build the dataset for you every 15 minutes.
- **Real-time:** the [codestats.gg history page](https://codestats.gg)
  keeps a rolling 36-hour window of validated drops with wagering
  requirements — free, no account.

## Are active Stake codes the same on stake.com and stake.us?

No — separate platforms, separate drop pools, often different currencies
(crypto vs sweeps). Codes are frequently platform-specific
(`stakecom…` / `stakeus…` prefixes are a strong hint). The tracker records
and validates both platforms independently.

## Do I need VIP status for bonus drops?

Most public bonus drops only require the stated weekly wager — not VIP
tier. VIP-specific perks (reload bonuses, rakeback, monthly bonuses) scale
with level; the free
[Stake reload claimer userscript](https://greasyfork.org/en/scripts/546623-auto-reload-on-stake-com-codestats-edition)
automates reloads at any tier. Stake VIP bonus drop analytics (tier
breakdown, value distributions) live on
[CodeStats.gg](https://codestats.gg).

## Is a Stake bonus drop bot safe to use?

Auto-claiming is a grey area: it operates inside your own logged-in
session and does not bypass security, but aggressive claim volume can be
flagged. Sensible guidance from the CodeStats.gg operators: normal play +
deposits alongside automation, don't run dozens of accounts from one IP.
Pure tracking/validation (this repo) is read-only and indistinguishable
from refreshing the promotions page.
