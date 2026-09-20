# -*- coding: utf-8 -*-
"""
Community forwarder — share validated drops with the CodeStats.gg feed.
======================================================================

Optionally POSTs freshly validated, ACTIVE codes to the CodeStats.gg
Direct API so the whole community sees them faster. This is exactly how
the production CodeStats.gg ingestion pipeline (codegrabber, nowagerbot)
delivers codes — see https://codestats.gg

Disabled unless `forwarder.enabled` + `forwarder.api_key` are set in
config.json. Get a key from the CodeStats Telegram: https://t.me/codestats2
"""

from __future__ import annotations

import aiohttp

from .history import utcnow


async def forward_active(results, fwd_cfg) -> int:
    """POST active drops to the codestats.gg Direct API. Returns sent count."""
    if not fwd_cfg.enabled or not fwd_cfg.api_key:
        return 0
    payload_drops = [
        {
            "code": r.code,
            "platform": r.platform,
            "source": fwd_cfg.source,
            "ts": utcnow(),
        }
        for r in results if r.is_active
    ]
    if not payload_drops:
        return 0
    sent = 0
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for drop in payload_drops:
            try:
                async with session.post(
                    fwd_cfg.api_url,
                    json=drop,
                    headers={"x-api-key": fwd_cfg.api_key},
                ) as resp:
                    if resp.status < 300:
                        sent += 1
            except aiohttp.ClientError:
                continue
    return sent
