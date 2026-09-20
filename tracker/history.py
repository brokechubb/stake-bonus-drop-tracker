# -*- coding: utf-8 -*-
"""
Drop history store — "Stake bonus drop history and stats"
=========================================================

SQLite persistence of every code the tracker has ever observed, plus
JSON/CSV exporters that feed the public dataset committed to this repo by
GitHub Actions every 15 minutes. The exported `drops.json` is what makes
this repository a live, always-fresh Stake code drop tracker.

If you need the *full* 36-hour rolling history with real-time validation,
use the free feed at https://codestats.gg (history page: /history.html).
"""

from __future__ import annotations

import csv
import json
import os
import sqlite3
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS drops (
    code           TEXT NOT NULL,
    platform       TEXT NOT NULL,
    status         TEXT NOT NULL,
    bonus_value    REAL,
    multiplier     REAL,
    source_channel TEXT NOT NULL DEFAULT '',
    message_url    TEXT NOT NULL DEFAULT '',
    first_seen     TEXT NOT NULL,
    last_seen      TEXT NOT NULL,
    PRIMARY KEY (code, platform)
);
CREATE TABLE IF NOT EXISTS scans (
    ts         TEXT NOT NULL,
    channels   INTEGER NOT NULL,
    candidates INTEGER NOT NULL,
    active     INTEGER NOT NULL
);
"""


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class History:
    def __init__(self, path: str = "drops.db"):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)

    # ── writes ────────────────────────────────────────────────────────
    def upsert(self, code, platform, status, value=None, mult=None,
               channel="", url=""):
        now = utcnow()
        self.conn.execute(
            """INSERT INTO drops (code, platform, status, bonus_value,
                 multiplier, source_channel, message_url, first_seen, last_seen)
               VALUES (?,?,?,?,?,?,?,?,?)
               ON CONFLICT(code, platform) DO UPDATE SET
                 status=excluded.status,
                 bonus_value=excluded.bonus_value,
                 multiplier=excluded.multiplier,
                 last_seen=excluded.last_seen""",
            (code, platform, status, value, mult, channel, url, now, now),
        )

    def log_scan(self, channels, candidates, active):
        self.conn.execute(
            "INSERT INTO scans (ts, channels, candidates, active) VALUES (?,?,?,?)",
            (utcnow(), channels, candidates, active),
        )

    def seed_from_json(self, path: str) -> int:
        """Load a previously exported dataset (e.g. the one committed to this
        repo) into a fresh DB, so history accumulates across CI runs instead
        of resetting to the latest sweep. Existing rows are never overwritten.
        Returns the number of rows seeded."""
        if not os.path.isfile(path):
            return 0
        try:
            with open(path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            rows = payload.get("drops", [])
        except (ValueError, OSError):
            return 0
        seeded = 0
        for r in rows:
            cur = self.conn.execute(
                """INSERT OR IGNORE INTO drops (code, platform, status,
                     bonus_value, multiplier, source_channel, message_url,
                     first_seen, last_seen)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (r.get("code", ""), r.get("platform", ""),
                 r.get("status", "unverified"), r.get("bonus_value"),
                 r.get("multiplier"), r.get("source_channel", ""),
                 r.get("message_url", ""),
                 r.get("first_seen", utcnow()),
                 r.get("last_seen", utcnow())),
            )
            seeded += cur.rowcount
        if seeded:
            self.conn.commit()
        return seeded

    def commit(self):
        self.conn.commit()

    # ── reads ─────────────────────────────────────────────────────────
    def active_codes(self):
        cur = self.conn.execute(
            """SELECT code, platform, bonus_value, last_seen FROM drops
               WHERE status IN ('bonusCodeActive','available')
               ORDER BY last_seen DESC"""
        )
        return [dict(zip(("code", "platform", "value", "last_seen"), r))
                for r in cur.fetchall()]

    def recent(self, limit=50):
        cur = self.conn.execute(
            """SELECT code, platform, status, bonus_value, source_channel,
                      message_url, first_seen, last_seen
               FROM drops ORDER BY last_seen DESC LIMIT ?""", (limit,))
        cols = ("code", "platform", "status", "value", "channel", "url",
                "first_seen", "last_seen")
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def totals(self):
        cur = self.conn.execute("SELECT COUNT(*) FROM drops")
        total = cur.fetchone()[0]
        cur = self.conn.execute(
            "SELECT COUNT(*) FROM drops WHERE status IN "
            "('bonusCodeActive','available')")
        active = cur.fetchone()[0]
        return total, active

    # ── exports (the public dataset) ──────────────────────────────────
    def export_json(self, path):
        cur = self.conn.execute(
            """SELECT code, platform, status, bonus_value, multiplier,
                      source_channel, message_url, first_seen, last_seen
               FROM drops ORDER BY last_seen DESC""")
        cols = ("code", "platform", "status", "bonus_value", "multiplier",
                "source_channel", "message_url", "first_seen", "last_seen")
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        total, active = self.totals()
        payload = {
            "generator": "stake-bonus-drop-tracker (CodeStats.gg edition)",
            "homepage": "https://codestats.gg",
            "updated": utcnow(),
            "totals": {"codes_tracked": total, "active_now": active},
            "note": "Free dataset from the open-source Stake code drop "
                    "tracker. For real-time feeds and auto-claiming, visit "
                    "https://codestats.gg",
            "drops": rows,
        }
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        return payload

    def export_csv(self, path):
        rows = self.recent(limit=10_000)
        cols = ("code", "platform", "status", "value", "channel", "url",
                "first_seen", "last_seen")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(cols))
            w.writeheader()
            w.writerows(rows)

    def close(self):
        self.conn.close()
