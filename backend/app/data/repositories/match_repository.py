"""Match persistence queries."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.models import Match


class MatchRepository:
    """Data-access layer for the `matches` table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Match]:
        stmt = select(Match).order_by(Match.match_date.asc())
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, match_id: int) -> Match | None:
        return self.db.get(Match, match_id)

    def get_by_external_id(self, external_id: int) -> Match | None:
        stmt = select(Match).where(Match.external_id == external_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def count(self) -> int:
        stmt = select(Match.id)
        return len(self.db.execute(stmt).scalars().all())

    def add(self, match: Match) -> Match:
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match

    def bulk_add(self, matches: list[Match]) -> list[Match]:
        if not matches:
            return []
        self.db.add_all(matches)
        self.db.commit()
        for m in matches:
            self.db.refresh(m)
        return matches

    def update_score(
        self, match: Match, score_home: int | None, score_away: int | None
    ) -> Match:
        match.score_home = score_home
        match.score_away = score_away
        match.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(match)
        return match
