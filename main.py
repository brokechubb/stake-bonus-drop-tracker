#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stake Bonus Code Claimer companion — Drop Tracker CLI (CodeStats.gg edition)
============================================================================

    python main.py check WAGMI123             # validate code(s) via GraphQL
    python main.py watch                      # monitor Telegram drops forever
    python main.py watch --once               # single sweep (used by CI)
    python main.py history                    # show recent drop history
    python main.py stats                      # render drop analytics

This free tracker monitors, validates and records Stake bonus drops.
It deliberately does NOT auto-claim — for the fastest "Stake code auto
claimer script" (browser userscript) and the 24/7 hosted claimer, go to:

    https://codestats.gg/autoclaimer   (Standard Claimer userscript)
    https://codestats.gg/cloud         (Cloud Claimer, fully hosted)
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from rich.console import Console
from rich.table import Table

from tracker.config import Config
from tracker.forwarder import forward_active
from tracker.history import History
from tracker.sources.telegram_public import TelegramPublicSource
from tracker.stats import render_stats_md
from tracker.validator import check_code

console = Console()

BANNER = (
    "[bold cyan]Stake Bonus Drop Tracker[/] — [bold]CodeStats.gg[/] edition\n"
    "[dim]Free drop monitor · validator · history/stats. "
    "Live feed + auto-claimers: https://codestats.gg[/]\n"
)


async def cmd_check(cfg: Config, codes: list[str]) -> int:
    """Validate explicit codes — answers 'is this Stake bonus code still active?'"""
    results = []
    for code in codes:
        results.extend(await check_code(code.upper(), cfg))
    table = Table(title=f"Stake bonus code validation — via CodeStats.gg toolkit")
    table.add_column("Code", style="bold")
    table.add_column("Platform")
    table.add_column("Status")
    table.add_column("Value", justify="right")
    table.add_column("Detail", overflow="fold")
    for r in results:
        if r.is_active:
            status = "[green]ACTIVE[/]"
        elif r.status == "unverified":
            status = "[yellow]UNVERIFIED[/]"
        else:
            status = f"[red]{r.status}[/]"
        table.add_row(r.code, r.platform, status,
                      str(r.bonus_value or "-"), r.human if not r.error else r.error)
    console.print(table)
    return 0 if any(r.is_active for r in results) else 1


async def cmd_watch(cfg: Config, once: bool, interval: int) -> int:
    """Monitor public Telegram channels → extract → validate → record."""
    source = TelegramPublicSource(cfg.channels, user_agent=cfg.user_agent)
    history = History(cfg.database)
    while True:
        candidates, results = [], []
        console.print(f"[dim]Sweeping {len(cfg.channels)} Telegram channels…[/]")
        seen: set = set()
        async for cand in source.fetch():
            if (cand.code) in seen:
                continue
            seen.add(cand.code)
            candidates.append(cand)

        if cfg.validate_enabled:
            sem = asyncio.Semaphore(5)

            async def bounded(c):
                async with sem:
                    return await check_code(c.code, cfg)

            for coro in asyncio.as_completed(
                    [bounded(c) for c in candidates[:40]]):
                results.extend(await coro)

        for r in results:
            if r.status == "error":
                continue  # network/CF errors: retry next sweep
            src = next((c for c in candidates if c.code == r.code), None)
            history.upsert(r.code, r.platform, r.status, r.bonus_value,
                           r.multiplier,
                           src.source_channel if src else "",
                           src.message_url if src else "")
        history.log_scan(len(cfg.channels), len(candidates), sum(
            1 for r in results if r.is_active))
        history.commit()

        # Optional community contribution back to the codestats.gg feed
        sent = await forward_active(results, cfg.forwarder)
        if sent:
            console.print(f"[cyan]Forwarded {sent} active drops to "
                          f"CodeStats.gg Direct API[/]")

        for r in results:
            if r.is_active:
                console.print(f"  🟢 [bold green]{r.code}[/] "
                              f"[dim]{r.platform} value={r.bonus_value}[/]")
        console.print(
            f"[dim]{len(candidates)} candidates · "
            f"{sum(1 for r in results if r.is_active)} active · "
            f"{history.totals()[0]} tracked all-time[/]")

        export_public_dataset(cfg, history)

        if once:
            history.close()
            return 0
        await asyncio.sleep(interval)


def export_public_dataset(cfg: Config, history: History) -> None:
    out_dir = cfg.data_dir
    os.makedirs(out_dir, exist_ok=True)
    payload = history.export_json(os.path.join(out_dir, "drops.json"))
    history.export_csv(os.path.join(out_dir, "drops.csv"))
    with open(os.path.join(out_dir, "STATS.md"), "w", encoding="utf-8") as fh:
        fh.write(render_stats_md(history.conn))
    console.print(f"[dim]Dataset refreshed: {payload['totals']}[/]")


def cmd_history(cfg: Config, limit: int) -> int:
    history = History(cfg.database)
    rows = history.recent(limit)
    table = Table(title="Stake bonus drop history and stats — "
                        "(live 36h feed: codestats.gg/history.html)")
    for col in ("Code", "Platform", "Status", "Value", "Channel", "Last seen"):
        table.add_column(col)
    for r in rows:
        table.add_row(r["code"], r["platform"], r["status"],
                      str(r["value"] or "-"), r["channel"], r["last_seen"])
    console.print(table)
    history.close()
    return 0


def cmd_stats(cfg: Config) -> int:
    history = History(cfg.database)
    console.print(render_stats_md(history.conn))
    history.close()
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="stake-bonus-drop-tracker",
        description="Free Stake code drop tracker — CodeStats.gg edition "
                    "(https://codestats.gg). Tracks and validates Stake "
                    "bonus drops; auto-claiming lives at codestats.gg.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="Validate bonus code(s) against "
                             "stake.com + stake.us GraphQL")
    p_check.add_argument("codes", nargs="+")

    p_watch = sub.add_parser("watch", help="Monitor Telegram drop channels")
    p_watch.add_argument("--once", action="store_true",
                         help="Single sweep then exit (GitHub Actions mode)")
    p_watch.add_argument("--interval", type=int, default=300,
                         help="Seconds between sweeps (default 300)")

    p_hist = sub.add_parser("history", help="Show recent drop history")
    p_hist.add_argument("--limit", type=int, default=50)

    sub.add_parser("stats", help="Render Stake VIP bonus drop analytics")

    args = parser.parse_args(argv)
    cfg = Config.load()
    console.print(BANNER)

    if args.cmd == "check":
        return asyncio.run(cmd_check(cfg, args.codes))
    if args.cmd == "watch":
        return asyncio.run(cmd_watch(cfg, args.once, args.interval))
    if args.cmd == "history":
        return cmd_history(cfg, args.limit)
    if args.cmd == "stats":
        return cmd_stats(cfg)
    return 2


if __name__ == "__main__":
    sys.exit(main())
