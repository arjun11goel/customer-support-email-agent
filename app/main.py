import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.api.dependencies import get_current_user
from app.api.routes import (
    agent,
    auth,
    emails,
    health,
    knowledge_base,
    responses,
)
from app.core.config import settings
from app.core.logging import configure_logging
from app.database.connection import SessionLocal
from app.database.init_db import initialize_database
from app.services.auth_service import AuthService
from app.services.demo_seed_service import seed_demo_inbox
from app.services.knowledge_base_service import KnowledgeBaseService


configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database, demo account, sample inbox, and index."""
    initialize_database()

    with SessionLocal() as db:
        demo_user = AuthService(db).ensure_demo_user()
        demo_company_name = demo_user.company_name
        seeded_count = seed_demo_inbox(db)

    logger.info("Demo workspace ready for %s.", demo_company_name)
    logger.info("Added %s synthetic demo inbox cases.", seeded_count)

    index_result = KnowledgeBaseService().rebuild_index()
    logger.info(
        "Knowledge index rebuilt: %s chunks from %s files.",
        index_result["chunks_indexed"],
        index_result["documents_indexed"],
    )

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Authenticated AI-assisted customer support demo using "
        "synthetic email data, LangGraph, LangChain, and FAISS."
    ),
    lifespan=lifespan,
)


# Health stays public so hosting platforms can check the service.
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)

# Login is public. The /auth/me endpoint checks its own access token.
app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Authentication"],
)

# Workspace APIs require a valid login token.
protected_dependencies = [Depends(get_current_user)]

app.include_router(
    emails.router,
    prefix="/api/v1",
    tags=["Emails"],
    dependencies=protected_dependencies,
)

app.include_router(
    agent.router,
    prefix="/api/v1",
    tags=["Agent"],
    dependencies=protected_dependencies,
)

app.include_router(
    responses.router,
    prefix="/api/v1",
    tags=["Responses"],
    dependencies=protected_dependencies,
)

app.include_router(
    knowledge_base.router,
    prefix="/api/v1",
    tags=["Knowledge Base"],
    dependencies=protected_dependencies,
)


@app.get("/")
def root():
    """Return basic service information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }