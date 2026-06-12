"""HTTP routes for the `matches` resource."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.business.match_service import MatchService
from app.data.database import get_db
from app.schemas.match_schema import HealthResponse, MatchListResponse, MatchRead

router = APIRouter(prefix="/api", tags=["matches"])


@router.get("/matches", response_model=MatchListResponse)
def list_matches(db: Session = Depends(get_db)) -> MatchListResponse:
    service = MatchService(db)
    matches = service.list_matches()
    return MatchListResponse(count=len(matches), matches=[MatchRead.model_validate(m) for m in matches])


@router.get("/matches/{match_id}", response_model=MatchRead)
def get_match(match_id: int, db: Session = Depends(get_db)) -> MatchRead:
    match = MatchService(db).get_match(match_id)
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match {match_id} not found",
        )
    return MatchRead.model_validate(match)
