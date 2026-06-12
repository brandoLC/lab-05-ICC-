"""Pydantic schemas for the `matches` resource."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MatchBase(BaseModel):
    external_id: int
    match_date: datetime
    status: str
    home_team: str
    home_team_crest: str | None = None
    away_team: str
    away_team_crest: str | None = None
    score_home: int | None = None
    score_away: int | None = None
    stage: str
    group_name: str | None = None


class MatchRead(MatchBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchListResponse(BaseModel):
    count: int
    matches: list[MatchRead]


class HealthResponse(BaseModel):
    status: str
    database: str
    environment: str = Field(default="development")
    matches_in_db: int = 0
