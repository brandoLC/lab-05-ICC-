"""Prediction persistence queries."""
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.data.models import Prediction


class PredictionRepository:
    """Data-access layer for the `predictions` table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Prediction]:
        stmt = (
            select(Prediction)
            .options(joinedload(Prediction.match))
            .order_by(Prediction.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars().unique().all())

    def list_by_match(self, match_id: int) -> list[Prediction]:
        stmt = (
            select(Prediction)
            .options(joinedload(Prediction.match))
            .where(Prediction.match_id == match_id)
            .order_by(Prediction.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars().unique().all())

    def add(self, prediction: Prediction) -> Prediction:
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        return prediction
