import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database.connection import Base
from app.models.agent_run import AgentRun
from app.models.email import Email
from app.services.response_service import ResponseService


@pytest.fixture
def db_session():
    """Create an isolated in-memory database for each test."""
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


def create_email_and_agent_run(db_session):
    """Create the records required to save a response draft."""
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

    agent_run = AgentRun(
        email_id=email.id,
        status="completed",
    )
    db_session.add(agent_run)
    db_session.commit()
    db_session.refresh(agent_run)

    return email, agent_run


def test_auto_send_demo_records_sent_status_and_processes_case(
    db_session,
    monkeypatch,
):
    monkeypatch.setattr(settings, "AUTO_SEND_ENABLED", True)
    email, agent_run = create_email_and_agent_run(db_session)
    response_service = ResponseService(db_session)

    draft = response_service.create_draft(
        email_id=email.id,
        agent_run_id=agent_run.id,
        content="You can invite a teammate from your workspace settings.",
    )

    sent_response = response_service.auto_send_demo(draft.id)

    db_session.refresh(email)

    assert sent_response.status == "sent_demo"
    assert sent_response.approved_by == (
        "SupportFlow AI (simulated auto-send)"
    )
    assert sent_response.sent_at is not None
    assert email.status == "processed"


def test_auto_send_demo_is_rejected_when_disabled(
    db_session,
    monkeypatch,
):
    monkeypatch.setattr(settings, "AUTO_SEND_ENABLED", False)
    email, agent_run = create_email_and_agent_run(db_session)
    response_service = ResponseService(db_session)

    draft = response_service.create_draft(
        email_id=email.id,
        agent_run_id=agent_run.id,
        content="A support agent will review your question.",
    )

    with pytest.raises(
        ValueError,
        match="Simulated auto-send is disabled",
    ):
        response_service.auto_send_demo(draft.id)

    db_session.refresh(email)

    assert draft.status == "draft"
    assert email.status == "new"