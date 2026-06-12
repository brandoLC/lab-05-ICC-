"""FastAPI application entry point."""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.business.match_service import MatchService
from app.core.config import get_settings
from app.data.database import Base, SessionLocal, engine
from app.presentation.routes import matches as matches_routes
from app.presentation.routes import predictions as predictions_routes
from app.schemas.match_schema import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mundial")

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application startup/shutdown.

    Creates tables (idempotent) and triggers the football-data.org sync
    in a background thread so the API stays responsive.
    """
    logger.info("Starting Mundial 2026 backend (env=%s)", settings.environment)
    retries = 30
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except SQLAlchemyError as exc:
            logger.warning(
                "DB not ready (attempt %s/%s): %s", attempt, retries, exc
            )
            time.sleep(2)
    else:
        logger.error("Database never became available; continuing anyway")

    # Create tables on every startup (idempotent).
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:
        logger.error("Could not create tables: %s", exc)

    # Best-effort initial sync.  Never block the API if it fails.
    try:
        with SessionLocal() as session:
            result = MatchService(session).ensure_matches_loaded()
            logger.info("Initial match sync result: %s", result)
    except Exception as exc:  # noqa: BLE001
        logger.error("Initial match sync failed: %s", exc)

    yield
    logger.info("Shutting down Mundial 2026 backend")


app = FastAPI(
    title="Mundial 2026 API",
    description="REST API for the FIFA World Cup 2026 match & prediction app.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["meta"], include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "app": "Mundial 2026 API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    """Return service health and database connectivity status."""
    db_status = "down"
    matches_in_db = 0
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
            db_status = "up"
            matches_in_db = MatchService(session).count_matches()
    except SQLAlchemyError as exc:
        logger.error("Health check DB error: %s", exc)
        db_status = f"down: {exc.__class__.__name__}"

    overall = "ok" if db_status == "up" else "degraded"
    return HealthResponse(
        status=overall,
        database=db_status,
        environment=settings.environment,
        matches_in_db=matches_in_db,
    )


app.include_router(matches_routes.router)
app.include_router(predictions_routes.router)
