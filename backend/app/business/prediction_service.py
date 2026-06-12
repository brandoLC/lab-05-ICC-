"""Business logic for the `predictions` domain."""
from sqlalchemy.orm import Session

from app.data.models import Prediction
from app.data.repositories.match_repository import MatchRepository
from app.data.repositories.prediction_repository import PredictionRepository
from app.schemas.prediction_schema import PredictionCreate


class PredictionServiceError(Exception):
    """Raised when a business rule forbids the operation."""


class PredictionService:
    """Orchestrates prediction creation and retrieval."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PredictionRepository(db)
        self.match_repo = MatchRepository(db)

    def list_predictions(self) -> list[Prediction]:
        return self.repo.list_all()

    def create_prediction(self, payload: PredictionCreate) -> Prediction:
        match = self.match_repo.get_by_id(payload.match_id)
        if match is None:
            raise PredictionServiceError(
                f"Match {payload.match_id} does not exist"
            )
        entity = Prediction(
            match_id=payload.match_id,
            predicted_winner=payload.predicted_winner,
            predicted_score_home=payload.predicted_score_home,
            predicted_score_away=payload.predicted_score_away,
        )
        return self.repo.add(entity)
