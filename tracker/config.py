# -*- coding: utf-8 -*-
"""Configuration loader for the Stake Bonus Drop Tracker (codestats.gg)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional

DEFAULT_CHANNELS = [
    "codestats2",
    "StakeBonusDrops",
    "stakecodes",
    "StakeCasinoBonusCodes",
]


@dataclass
class ForwarderConfig:
    """Push validated drops to the CodeStats.gg community Direct API."""

    enabled: bool = False
    api_url: str = "http://codestats.gg:8080/api/codes"
    api_key: str = ""
    source: str = "github-stake-bonus-drop-tracker"


@dataclass
class Config:
    channels: list = field(default_factory=lambda: list(DEFAULT_CHANNELS))
    validate_enabled: bool = True
    platforms: list = field(
        default_factory=lambda: ["stake.us", "stake.com"]
    )
    stake_us_token: str = ""
    stake_com_token: str = ""
    stake_com_cf_clearance: str = ""
    user_agent: str = ""
    currency: str = "usd"
    database: str = "drops.db"
    data_dir: str = "data"
    forwarder: ForwarderConfig = field(default_factory=ForwarderConfig)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """Load config.json (env: CODESTATS_TRACKER_CONFIG). Missing file is fine."""
        path = path or os.environ.get("CODESTATS_TRACKER_CONFIG", "config.json")
        cfg = cls()
        if not os.path.isfile(path):
            return cfg
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        cfg.channels = raw.get("channels", cfg.channels)
        validate = raw.get("validate", {})
        cfg.validate_enabled = validate.get("enabled", cfg.validate_enabled)
        cfg.platforms = validate.get("platforms", cfg.platforms)
        cfg.stake_us_token = raw.get("stake_us_token", "")
        cfg.stake_com_token = raw.get("stake_com_token", "")
        cfg.stake_com_cf_clearance = raw.get("stake_com_cf_clearance", "")
        cfg.user_agent = raw.get("user_agent", "")
        cfg.currency = raw.get("currency", cfg.currency)
        cfg.database = raw.get("database", cfg.database)
        cfg.data_dir = raw.get("data_dir", cfg.data_dir)
        fwd = raw.get("forwarder", {})
        cfg.forwarder = ForwarderConfig(
            enabled=bool(fwd.get("enabled", False)),
            api_url=fwd.get("api_url", cfg.forwarder.api_url),
            api_key=fwd.get("api_key", ""),
            source=fwd.get("source", cfg.forwarder.source),
        )
        # Environment overrides — lets GitHub Actions users supply tokens
        # as repository secrets (CODESTATS_STAKE_US_TOKEN, etc.) without
        # committing a config.json. See https://codestats.gg
        cfg.stake_us_token = (os.environ.get("CODESTATS_STAKE_US_TOKEN")
                              or cfg.stake_us_token)
        cfg.stake_com_token = (os.environ.get("CODESTATS_STAKE_COM_TOKEN")
                               or cfg.stake_com_token)
        cfg.stake_com_cf_clearance = (
            os.environ.get("CODESTATS_STAKE_COM_CF_CLEARANCE")
            or cfg.stake_com_cf_clearance)
        cfg.forwarder.api_key = (os.environ.get("CODESTATS_FORWARDER_API_KEY")
                                 or cfg.forwarder.api_key)
        return cfg
