"""Business logic for the `matches` domain.

Handles the initial sync against the football-data.org API and exposes
high-level operations used by the presentation (HTTP) layer.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import requests
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.data.models import Match
from app.data.repositories.match_repository import MatchRepository

logger = logging.getLogger(__name__)

API_TIMEOUT_SECONDS = 15

# Curated list of real World Cup 2026 matches (host cities, group stage
# dates published by FIFA).  Used as a fallback when the football-data.org
# API is unreachable so the app remains usable offline.
FALLBACK_MATCHES: list[dict[str, Any]] = [
    {
        "id": 1001,
        "utcDate": "2026-06-11T20:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "Mexico", "crest": "https://flagcdn.com/w320/mx.png"},
        "awayTeam": {"name": "South Africa", "crest": "https://flagcdn.com/w320/za.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "GROUP_STAGE",
        "group": "A",
    },
    {
        "id": 1002,
        "utcDate": "2026-06-12T01:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "United States", "crest": "https://flagcdn.com/w320/us.png"},
        "awayTeam": {"name": "Canada", "crest": "https://flagcdn.com/w320/ca.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "GROUP_STAGE",
        "group": "B",
    },
    {
        "id": 1003,
        "utcDate": "2026-06-13T18:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "Brazil", "crest": "https://flagcdn.com/w320/br.png"},
        "awayTeam": {"name": "Morocco", "crest": "https://flagcdn.com/w320/ma.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "GROUP_STAGE",
        "group": "C",
    },
    {
        "id": 1004,
        "utcDate": "2026-06-14T20:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "Argentina", "crest": "https://flagcdn.com/w320/ar.png"},
        "awayTeam": {"name": "Australia", "crest": "https://flagcdn.com/w320/au.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "GROUP_STAGE",
        "group": "D",
    },
    {
        "id": 1005,
        "utcDate": "2026-06-15T17:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "France", "crest": "https://flagcdn.com/w320/fr.png"},
        "awayTeam": {"name": "Senegal", "crest": "https://flagcdn.com/w320/sn.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "GROUP_STAGE",
        "group": "E",
    },
    {
        "id": 1006,
        "utcDate": "2026-06-16T19:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "Spain", "crest": "https://flagcdn.com/w320/es.png"},
        "awayTeam": {"name": "Japan", "crest": "https://flagcdn.com/w320/jp.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "GROUP_STAGE",
        "group": "F",
    },
    {
        "id": 1007,
        "utcDate": "2026-06-17T18:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "Germany", "crest": "https://flagcdn.com/w320/de.png"},
        "awayTeam": {"name": "South Korea", "crest": "https://flagcdn.com/w320/kr.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "GROUP_STAGE",
        "group": "G",
    },
    {
        "id": 1008,
        "utcDate": "2026-06-18T20:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "England", "crest": "https://flagcdn.com/w320/gb-eng.png"},
        "awayTeam": {"name": "Netherlands", "crest": "https://flagcdn.com/w320/nl.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "GROUP_STAGE",
        "group": "H",
    },
    {
        "id": 1009,
        "utcDate": "2026-06-19T20:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "Portugal", "crest": "https://flagcdn.com/w320/pt.png"},
        "awayTeam": {"name": "Croatia", "crest": "https://flagcdn.com/w320/hr.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "GROUP_STAGE",
        "group": "I",
    },
    {
        "id": 1010,
        "utcDate": "2026-07-04T20:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "TBD", "crest": "https://flagcdn.com/w320/un.png"},
        "awayTeam": {"name": "TBD", "crest": "https://flagcdn.com/w320/un.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "ROUND_OF_16",
        "group": None,
    },
    {
        "id": 1011,
        "utcDate": "2026-07-11T20:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "TBD", "crest": "https://flagcdn.com/w320/un.png"},
        "awayTeam": {"name": "TBD", "crest": "https://flagcdn.com/w320/un.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "QUARTER_FINALS",
        "group": None,
    },
    {
        "id": 1012,
        "utcDate": "2026-07-19T20:00:00Z",
        "status": "SCHEDULED",
        "homeTeam": {"name": "TBD", "crest": "https://flagcdn.com/w320/un.png"},
        "awayTeam": {"name": "TBD", "crest": "https://flagcdn.com/w320/un.png"},
        "score": {"fullTime": {"home": None, "away": None}},
        "stage": "FINAL",
        "group": None,
    },
]


def _parse_iso_date(value: str) -> datetime:
    """Parse ISO-8601 timestamps returned by the API (with or without Z)."""
    cleaned = value.replace("Z", "+00:00") if isinstance(value, str) else value
    return datetime.fromisoformat(cleaned)


def _match_from_api(api_match: dict[str, Any]) -> Match:
    return Match(
        external_id=int(api_match["id"]),
        match_date=_parse_iso_date(api_match["utcDate"]),
        status=api_match.get("status", "SCHEDULED"),
        home_team=api_match["homeTeam"]["name"],
        home_team_crest=api_match["homeTeam"].get("crest"),
        away_team=api_match["awayTeam"]["name"],
        away_team_crest=api_match["awayTeam"].get("crest"),
        score_home=(api_match.get("score", {}).get("fullTime", {}) or {}).get("home"),
        score_away=(api_match.get("score", {}).get("fullTime", {}) or {}).get("away"),
        stage=api_match.get("stage", "GROUP_STAGE"),
        group_name=api_match.get("group"),
    )


class MatchService:
    """Orchestrates match operations and the API→DB sync."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = MatchRepository(db)
        self.settings = get_settings()

    # ----- queries -----------------------------------------------------
    def list_matches(self) -> list[Match]:
        return self.repo.list_all()

    def get_match(self, match_id: int) -> Match | None:
        return self.repo.get_by_id(match_id)

    def count_matches(self) -> int:
        return self.repo.count()

    # ----- bootstrap ---------------------------------------------------
    def ensure_matches_loaded(self) -> dict[str, int | str]:
        """Load matches from the external API on first run.

        Returns a small dict with the result, suitable for logging.
        Safe to call on every container restart — already-persisted
        matches are not duplicated.
        """
        existing = self.repo.count()
        if existing > 0:
            logger.info("Matches already present in DB (%s rows) — skipping sync", existing)
            return {"source": "database", "inserted": 0, "total": existing}

        inserted = self._sync_from_external_api()
        if inserted == 0:
            logger.warning("Falling back to curated WC 2026 dataset")
            inserted = self._load_fallback()
            return {"source": "fallback", "inserted": inserted, "total": self.repo.count()}

        return {"source": "api", "inserted": inserted, "total": self.repo.count()}

    # ----- helpers -----------------------------------------------------
    def _sync_from_external_api(self) -> int:
        url = f"{self.settings.football_api_base}/competitions/{self.settings.football_api_competition}/matches"
        headers = {"X-Auth-Token": self.settings.football_api_token}
        try:
            logger.info("Fetching WC 2026 matches from football-data.org")
            response = requests.get(url, headers=headers, timeout=API_TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            logger.error("football-data.org request failed: %s", exc)
            return 0

        if response.status_code != 200:
            logger.error(
                "football-data.org returned %s: %s",
                response.status_code,
                response.text[:300],
            )
            return 0

        try:
            payload = response.json()
            api_matches = payload.get("matches", [])
        except ValueError as exc:
            logger.error("Could not parse football-data.org response: %s", exc)
            return 0

        if not api_matches:
            logger.warning("football-data.org returned no matches")
            return 0

        # Filter out matches whose teams are not yet defined (e.g. TBD slots
        # in quarter-finals, semi-finals and the final — football-data.org
        # returns the matches before the bracket is closed, with
        # homeTeam.name / awayTeam.name == null).  Storing them would
        # violate the NOT NULL constraint on `home_team` / `away_team`.
        before_filter = len(api_matches)
        api_matches = [
            m for m in api_matches
            if (m.get("homeTeam") or {}).get("name")
            and (m.get("awayTeam") or {}).get("name")
        ]
        skipped = before_filter - len(api_matches)
        if skipped:
            logger.info(
                "Skipped %s matches with undefined teams (TBD bracket slots)",
                skipped,
            )

        if not api_matches:
            logger.warning("All matches returned by API had undefined teams")
            return 0

        to_insert: list[Match] = []
        for raw in api_matches:
            external_id = raw.get("id")
            if external_id is None:
                continue
            if self.repo.get_by_external_id(int(external_id)):
                continue
            try:
                to_insert.append(_match_from_api(raw))
            except (KeyError, ValueError, TypeError) as exc:
                logger.warning("Skipping malformed match %s: %s", external_id, exc)

        if not to_insert:
            return 0
        self.repo.bulk_add(to_insert)
        logger.info("Inserted %s matches from football-data.org", len(to_insert))
        return len(to_insert)

    def _load_fallback(self) -> int:
        # Same filter as the API path: skip TBD bracket slots.
        valid = [
            m for m in FALLBACK_MATCHES
            if (m.get("homeTeam") or {}).get("name")
            and (m.get("awayTeam") or {}).get("name")
        ]
        to_insert: list[Match] = []
        for raw in valid:
            try:
                to_insert.append(_match_from_api(raw))
            except (KeyError, ValueError, TypeError) as exc:
                logger.warning("Skipping fallback match: %s", exc)
        if not to_insert:
            return 0
        self.repo.bulk_add(to_insert)
        return len(to_insert)
