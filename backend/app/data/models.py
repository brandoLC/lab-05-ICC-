"""ORM models for the Mundial 2026 application."""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data.database import Base


class Match(Base):
    """A single World Cup 2026 match."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    match_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SCHEDULED")
    home_team: Mapped[str] = mapped_column(String(120), nullable=False)
    home_team_crest: Mapped[str | None] = mapped_column(Text, nullable=True)
    away_team: Mapped[str] = mapped_column(String(120), nullable=False)
    away_team_crest: Mapped[str | None] = mapped_column(Text, nullable=True)
    score_home: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_away: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stage: Mapped[str] = mapped_column(String(40), nullable=False, default="GROUP_STAGE")
    group_name: Mapped[str | None] = mapped_column(String(8), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    predictions: Mapped[list["Prediction"]] = relationship(
        "Prediction", back_populates="match", cascade="all, delete-orphan"
    )


class Prediction(Base):
    """A user prediction for a specific match."""

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    predicted_winner: Mapped[str] = mapped_column(String(8), nullable=False)
    predicted_score_home: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_score_away: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    match: Mapped[Match] = relationship("Match", back_populates="predictions")
