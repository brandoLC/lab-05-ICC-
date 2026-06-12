"""Pydantic schemas for the `predictions` resource."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Winner = Literal["home", "away", "draw"]


class PredictionCreate(BaseModel):
    match_id: int = Field(..., gt=0)
    predicted_winner: Winner
    predicted_score_home: int = Field(..., ge=0, le=50)
    predicted_score_away: int = Field(..., ge=0, le=50)

    @model_validator(mode="after")
    def _winner_matches_score(self) -> "PredictionCreate":
        if self.predicted_winner == "draw" and self.predicted_score_home != self.predicted_score_away:
            raise ValueError("Winner 'draw' requires equal scores")
        if self.predicted_winner == "home" and self.predicted_score_home <= self.predicted_score_away:
            raise ValueError("Winner 'home' requires home score greater than away")
        if self.predicted_winner == "away" and self.predicted_score_away <= self.predicted_score_home:
            raise ValueError("Winner 'away' requires away score greater than home")
        return self


class PredictionRead(BaseModel):
    id: int
    match_id: int
    predicted_winner: str
    predicted_score_home: int
    predicted_score_away: int
    created_at: datetime
    match: "MatchNested | None" = None

    model_config = ConfigDict(from_attributes=True)


class MatchNested(BaseModel):
    id: int
    home_team: str
    home_team_crest: str | None = None
    away_team: str
    away_team_crest: str | None = None
    match_date: datetime
    stage: str
    group_name: str | None = None
    status: str
    score_home: int | None = None
    score_away: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PredictionListResponse(BaseModel):
    count: int
    predictions: list[PredictionRead]


PredictionRead.model_rebuild()
