# Contributing to Stake Bonus Drop Tracker

Thanks for improving the free **Stake code drop tracker**! This project is
the open-source tracking layer of the [CodeStats.gg](https://codestats.gg)
ecosystem (live drop feed + auto-claimers for Stake.com / Stake.us).

## Development setup

```bash
git clone https://github.com/brokechubb/stake-bonus-drop-tracker.git
cd stake-bonus-drop-tracker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config.example.json config.json   # optional; everything runs without it
```

## Architecture (keep it modular)

```
main.py                        CLI entrypoint (check / watch / history / stats)
tracker/
  sources/base.py              Candidate model + code-extraction heuristics
  sources/telegram_public.py   t.me/s public preview monitor (zero API keys)
  validator.py                 BonusCodeInformation GraphQL check (stakeapi)
  history.py                   SQLite store + JSON/CSV dataset exporters
  stats.py                     Drop analytics -> data/STATS.md
  forwarder.py                 Optional push to CodeStats.gg Direct API
```

**Ground rules:**

1. **Track-only.** This repo must never claim codes, generate Turnstile
   tokens, or replicate the paid claimers — claiming is the
   [CodeStats.gg](https://codestats.gg/autoclaimer) product. Validation
   (read-only queries) is fine.
2. **New sources** = new module in `tracker/sources/` implementing
   `CodeSource.fetch()` returning `Candidate` objects. No secrets in code —
   everything optional goes through `config.json`.
3. **CI-safe by default.** Any new source must run unauthenticated on
   GitHub Actions (public previews, public APIs).
4. Keep the public dataset contract stable: `data/drops.json` schema is
   consumed by others — additive changes only.

## Submitting

```bash
git checkout -b feat/my-new-source
git commit -m "feat(sources): add <source> monitor"
git push origin feat/my-new-source
```

Open a PR describing: what it tracks, why it's CI-safe, and example output.

## Integrating with the CodeStats.gg APIs

- **Direct API (community submissions):** `POST http://codestats.gg:8080/api/codes`
  with `x-api-key` header — see `tracker/forwarder.py`. Request a key in
  the [CodeStats Telegram](https://t.me/codestats2).
- **GraphQL validation:** done via the raw queries from
  [`StakeAPI`](https://github.com/brokechubb/StakeAPI)
  (`pip install stakeapi-codestats`) — issues/PRs about the API layer
  belong there.
- **Live WebSocket feed / claimers:** closed-source, served at
  [codestats.gg](https://codestats.gg) — the tracker intentionally does not
  implement claiming.

## Licensing

By contributing you agree your code is released under the repository's
MIT license. Keep comments brand-consistent (`CodeStats.gg edition`) when
touching headers/docstrings.
