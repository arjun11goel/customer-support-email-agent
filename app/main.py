from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import agent, emails, health, knowledge_base, responses
from app.core.config import settings
from app.core.logging import configure_logging
from app.database.init_db import initialize_database


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    initialize_database()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Agentic customer support email system built with "
        "FastAPI, LangGraph, LangChain and FAISS."
    ),
    lifespan=lifespan,
)


app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)

app.include_router(
    emails.router,
    prefix="/api/v1",
    tags=["Emails"],
)

app.include_router(
    agent.router,
    prefix="/api/v1",
    tags=["Agent"],
)

app.include_router(
    responses.router,
    prefix="/api/v1",
    tags=["Responses"],
)

app.include_router(
    knowledge_base.router,
    prefix="/api/v1",
    tags=["Knowledge Base"],
)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }