# -*- coding: utf-8 -*-
"""Base classes for drop sources (Telegram monitors, site scrapers, etc.)."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Iterable

# Stake drop codes are CASE-SENSITIVE (verified against live drops) and are
# almost always announced with a label ("- Code: WAGMI12") or embedded in a
# claim URL ("...?code=hgetdgnl"). Labeled extraction preserves case and
# avoids the noise of naive ALL-CAPS token scraping.
LABEL_RE = re.compile(
    r"\bcode\b\s*[:=\-\u2013\u2014]*\s*[\"'\u201c\u2018]*\s*([A-Za-z0-9]{3,32})\b",
    re.I,
)
URL_CODE_RE = re.compile(r"[?&]code=([A-Za-z0-9]{3,32})")

# Words that follow the word "code" but are never the code itself.
BADWORDS = {
    "stake", "stakes", "shuffle", "codestats", "thrill", "https", "http",
    "here", "below", "above", "drop", "drops", "bonus", "the", "a", "an",
    "in", "on", "to", "and", "is", "are", "was", "get", "use", "enter",
    "your", "our", "new", "not", "no", "alert", "alerts", "post", "sent",
    "link", "page", "us", "com", "gg", "www", "type", "value", "claim",
    "code", "codes", "attached", "below", "above",
}


@dataclass
class Candidate:
    """A candidate Stake bonus code seen in the wild, before validation."""

    code: str
    source_channel: str
    message_url: str = ""
    message_text: str = ""
    seen_at: str = ""          # ISO-8601 UTC
    brand: str = "unknown"     # casino the drop targets (stake/shuffle/thrill)
    platforms: list = field(default_factory=list)  # filled by validator

    def __post_init__(self):
        self.code = (self.code or "").strip()

    @property
    def is_plausible(self) -> bool:
        c = self.code
        if not 3 <= len(c) <= 32:
            return False
        if not c.isalnum():
            return False
        if c.lower() in BADWORDS:
            return False
        return True


def detect_brand(text: str) -> str:
    """Classify which casino a drop message targets.

    Mixed channels (like the CodeStats feed) broadcast drops for several
    casinos — Shuffle, Thrill, Stake — and their codes are NOT
    interchangeable. Non-stake mentions win over stake so cross-branded
    boilerplate never leaks a foreign code into the Stake dataset.
    """
    t = (text or "").lower()
    if "thrill" in t:
        return "thrill"
    if "shuffle" in t:
        return "shuffle"
    if "stake" in t:
        return "stake"
    return "unknown"


def extract_codes(text: str) -> list[str]:
    """Extract plausible Stake bonus drop codes from a message body."""
    found: list[str] = []
    seen: set[str] = set()
    for pattern in (URL_CODE_RE, LABEL_RE):
        for m in pattern.finditer(text or ""):
            cand = Candidate(code=m.group(1), source_channel="")
            if cand.is_plausible and cand.code not in seen:
                found.append(cand.code)
                seen.add(cand.code)
    return found


def strip_html(raw: str) -> str:
    """Normalize a Telegram web-preview message body to plain text."""
    txt = re.sub(r"<br\s*/?>", "\n", raw or "", flags=re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    return re.sub(r"[ \t]+", " ", txt).strip()


class CodeSource:
    """Interface: async iterate candidates from some origin."""

    name = "source"

    async def fetch(self) -> Iterable[Candidate]:  # pragma: no cover
        raise NotImplementedError
