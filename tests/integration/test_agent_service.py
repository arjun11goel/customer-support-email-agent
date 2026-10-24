import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.services.agent_service as agent_service_module
from app.core.config import settings
from app.database.connection import Base
from app.models.email import Email
from app.services.agent_service import AgentService
from app.services.response_service import ResponseService


@pytest.fixture
def db_session():
    """Create an isolated in-memory database for the test."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)

    test_session_factory = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )
    session = test_session_factory()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def test_agent_run_persists_eligible_simulated_send(
    db_session,
    monkeypatch,
):
    monkeypatch.setattr(settings, "AUTO_SEND_ENABLED", True)

    email = Email(
        sender="customer@example.com",
        recipient="support@example.com",
        subject="How do I invite a teammate?",
        body="Where can I invite a teammate?",
        source="mock",
        status="new",
    )
    db_session.add(email)
    db_session.commit()
    db_session.refresh(email)

    graph_result = {
        "intent": "product_question",
        "confidence": 0.96,
        "retrieved_context": [
            "Source: products.md\n"
            "Excerpt: Invite a teammate from workspace settings."
        ],
        "draft_response": (
            "You can invite a teammate from your workspace settings."
        ),
        "grounding_score": 0.8,
        "validation_passed": True,
        "validation_issues": [],
        "review_required": False,
        "escalation_required": False,
        "escalation_reasons": [],
        "auto_send_eligible": True,
        "auto_send_reason": "All configured demo checks passed.",
        "error": None,
        "status": "auto_sent_demo",
    }

    monkeypatch.setattr(
        agent_service_module.agent_graph,
        "invoke",
        lambda state: graph_result,
    )

    saved_run = AgentService(db_session).run(email.id)
    saved_response = ResponseService(db_session).get_for_agent_run(
        saved_run.id
    )
    db_session.refresh(email)

    assert saved_run.status == "auto_sent_demo"
    assert saved_run.review_required is False
    assert saved_response is not None
    assert saved_response.status == "sent_demo"
    assert saved_response.approved_by == (
        "SupportFlow AI (simulated auto-send)"
    )
    assert email.status == "processed"