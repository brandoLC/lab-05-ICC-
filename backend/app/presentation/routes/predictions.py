"""HTTP routes for the `predictions` resource."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.business.prediction_service import PredictionService, PredictionServiceError
from app.data.database import get_db
from app.schemas.prediction_schema import (
    PredictionCreate,
    PredictionListResponse,
    PredictionRead,
)

router = APIRouter(prefix="/api", tags=["predictions"])


@router.get(
    "/predictions",
    response_model=PredictionListResponse,
    summary="List all registered predictions",
)
def list_predictions(db: Session = Depends(get_db)) -> PredictionListResponse:
    service = PredictionService(db)
    predictions = service.list_predictions()
    return PredictionListResponse(
        count=len(predictions),
        predictions=[PredictionRead.model_validate(p) for p in predictions],
    )


@router.post(
    "/predictions",
    response_model=PredictionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new prediction",
)
def create_prediction(
    payload: PredictionCreate, db: Session = Depends(get_db)
) -> PredictionRead:
    service = PredictionService(db)
    try:
        entity = service.create_prediction(payload)
    except PredictionServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PredictionRead.model_validate(entity)
