# -*- coding: utf-8 -*-
"""
Stake Telegram Drop Monitor (public web preview edition)
========================================================

Watches public Telegram channels (t.me/s/<channel>) for Stake bonus drop
messages and extracts candidate codes — **no Telegram API keys, no bot
token, no userbot session required**, which makes it safe to run inside
GitHub Actions every 15 minutes.

This is the lightweight, open-source complement to the 24/7 monitoring
stack behind the CodeStats.gg live feed (Telethon + OCR pipeline). For the
real-time validated feed, wagering requirements and drop analytics, see
https://codestats.gg
"""

from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from typing import AsyncIterator

import aiohttp

from .base import Candidate, CodeSource, extract_codes, strip_html

# Chrome-like UA: t.me/s renders the full widget HTML for modern browsers.
DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/135.0.0.0 Safari/537.36"
)

_MESSAGE_BLOCK_RE = re.compile(
    r'<div class="tgme_widget_message_text js-message_text"[^>]*>(.*?)</div>',
    re.I | re.S,
)
_POST_META_RE = re.compile(r'data-post="([^"]+)"')
_TIME_RE = re.compile(r'<time datetime="([^"]+)"')


class TelegramPublicSource(CodeSource):
    """Monitor public Telegram channels for Stake bonus code drops."""

    name = "telegram_public"

    def __init__(self, channels: list[str], user_agent: str = ""):
        self.channels = [c.strip().lstrip("@") for c in channels if c.strip()]
        self.user_agent = user_agent or DEFAULT_UA

    async def fetch(self) -> AsyncIterator[Candidate]:
        timeout = aiohttp.ClientTimeout(total=25)
        async with aiohttp.ClientSession(
            timeout=timeout,
            headers={"User-Agent": self.user_agent,
                     "Accept-Language": "en-US,en;q=0.9"},
        ) as session:
            results = await asyncio.gather(
                *(self._fetch_channel(session, ch) for ch in self.channels),
                return_exceptions=True,
            )
        for result in results:
            if isinstance(result, Exception):
                continue  # one dead channel must not kill the sweep
            for cand in result:
                yield cand

    async def _fetch_channel(self, session, channel: str) -> list[Candidate]:
        url = f"https://t.me/s/{channel}"
        out: list[Candidate] = []
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return out
                body = await resp.text()
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return out

        # Pair each message body with its post permalink + timestamp.
        posts = list(_POST_META_RE.finditer(body))
        for m in _MESSAGE_BLOCK_RE.finditer(body):
            text = strip_html(m.group(1))
            for code in extract_codes(text):
                permalink, seen_at = "", ""
                for p in posts:
                    if p.start() > m.start():
                        permalink = f"https://t.me/{p.group(1)}"
                        break
                t = _TIME_RE.search(body, m.start())
                if t:
                    seen_at = t.group(1)
                if not seen_at:
                    seen_at = datetime.now(timezone.utc).isoformat()
                out.append(
                    Candidate(
                        code=code,
                        source_channel=channel,
                        message_url=permalink,
                        message_text=text[:400],
                        seen_at=seen_at,
                    )
                )
        return out
