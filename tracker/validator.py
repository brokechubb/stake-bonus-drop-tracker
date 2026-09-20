# -*- coding: utf-8 -*-
"""
Stake bonus code validator
==========================

Checks candidate codes against Stake's official GraphQL API
(`BonusCodeInformation` query) on stake.us and stake.com in parallel —
a minimal, dependency-free aiohttp client implementing the same verified
query used by the `stakeapi` wrapper from the CodeStats.gg ecosystem
(https://github.com/brokechubb/StakeAPI).

NOTE: Stake requires authentication even for read-only code checks
(`notAuthenticated`). Configure `stake_us_token` (and optionally
`stake_com_token` + `stake_com_cf_clearance`) in config.json to enable
validation. Without tokens the tracker still records drop *sightings* —
the free live feed at https://codestats.gg does instant validation.

Cloudflare notes (verified, see StakeAPI docs):
  * stake.us  → works with plain aiohttp, no cf_clearance needed.
  * stake.com → requires a cf_clearance cookie + matching User-Agent.

This tracker is READ-ONLY — it never claims codes. Auto-claiming
(Turnstile-gated `claimConditionBonusCode`) is the domain of the hosted
CodeStats.gg claimers: https://codestats.gg/autoclaimer
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import aiohttp

# stake.us needs no Cloudflare cookie; stake.com 403s without one.
PLATFORMS = {
    "stake.us": {"needs_cf": False},
    "stake.com": {"needs_cf": True},
}

GRAPHQL_PATH = "/_api/graphql"

BONUS_CODE_INFORMATION = """
query BonusCodeInformation($code: String!, $couponType: CouponType!) {
  bonusCodeInformation(code: $code, couponType: $couponType) {
    availabilityStatus
    bonusValue
    cryptoMultiplier
    __typename
  }
}
"""

STATUS_HINTS = {
    "bonusCodeActive": "ACTIVE — claimable right now",
    "available": "ACTIVE — claimable right now",
    "bonusCodeInactive": "INACTIVE / fully claimed cap reached",
    "alreadyClaimed": "ALREADY CLAIMED by your account",
    "dropUnavailable": "UNAVAILABLE (exhausted or window closed)",
    "notFound": "NOT FOUND — code does not exist",
    "unverified": "sighting recorded — add stake_us_token to config.json "
                  "for GraphQL validation (or use the free live feed at "
                  "codestats.gg)",
}

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/135.0.0.0 Safari/537.36"
)


@dataclass
class ValidationResult:
    code: str
    platform: str
    status: str          # availabilityStatus | unverified | skipped | error
    bonus_value: float | None = None
    multiplier: float | None = None
    error: str = ""

    @property
    def is_active(self) -> bool:
        return self.status in ("bonusCodeActive", "available")

    @property
    def human(self) -> str:
        return STATUS_HINTS.get(self.status, self.status)


def _token_for(platform: str, cfg) -> str:
    return cfg.stake_us_token if platform == "stake.us" else cfg.stake_com_token


async def check_code(code: str, cfg) -> list[ValidationResult]:
    """Validate one code across every configured platform, in parallel."""
    tasks = [
        _check_on_platform(code, platform, cfg)
        for platform in cfg.platforms if platform in PLATFORMS
    ]
    if not tasks:
        return []
    return await asyncio.gather(*tasks)


async def _check_on_platform(code: str, platform: str, cfg) -> ValidationResult:
    needs_cf = PLATFORMS[platform]["needs_cf"]
    token = _token_for(platform, cfg)

    if needs_cf and not cfg.stake_com_cf_clearance:
        return ValidationResult(
            code=code, platform=platform, status="unverified",
            error="stake.com needs cf_clearance in config.json "
                  "(stake.us validates with just a session token) — "
                  "sighting recorded, not yet verified",
        )
    if not token:
        # No credentials → record the sighting, skip live validation.
        return ValidationResult(code=code, platform=platform,
                                status="unverified")

    headers = {
        "Content-Type": "application/json",
        "User-Agent": cfg.user_agent or DEFAULT_UA,
        "X-Language": "en",
        "X-Operation-Name": "BonusCodeInformation",
        "X-Operation-Type": "query",
        "X-Access-Token": token,
        "Origin": f"https://{platform}",
        "Referer": f"https://{platform}/",
    }
    payload = {
        "query": BONUS_CODE_INFORMATION,
        "variables": {"code": code, "couponType": "drop"},
    }
    timeout = aiohttp.ClientTimeout(total=20)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"https://{platform}{GRAPHQL_PATH}",
                json=payload, headers=headers,
            ) as resp:
                if resp.status in (403, 429):
                    return ValidationResult(
                        code=code, platform=platform, status="error",
                        error=f"HTTP {resp.status} — Cloudflare/rate limit; "
                              f"provide cf_clearance + matching user_agent")
                body = await resp.json(content_type=None)
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as exc:
        return ValidationResult(code=code, platform=platform, status="error",
                                error=f"{type(exc).__name__}: {exc}")

    errors = body.get("errors") or []
    if errors:
        etype = errors[0].get("errorType", "")
        msg = errors[0].get("message", "")[:200]
        if etype == "notAuthenticated":
            return ValidationResult(code=code, platform=platform,
                                    status="unverified",
                                    error=f"token rejected: {msg}")
        return ValidationResult(code=code, platform=platform,
                                status="error", error=msg)

    info = (body.get("data") or {}).get("bonusCodeInformation") or {}
    return ValidationResult(
        code=code, platform=platform,
        status=info.get("availabilityStatus", "notFound"),
        bonus_value=info.get("bonusValue"),
        multiplier=info.get("cryptoMultiplier"),
    )
