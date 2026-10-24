import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun
from app.models.email import Email
from app.models.response import Response


DEMO_CASES = [
    {
        "sender": "maya@northstar.example",
        "subject": "I was charged twice for my subscription",
        "body": (
            "Hello, I noticed two charges for my subscription this month. "
            "Could someone check the billing and let me know what happened?"
        ),
        "status": "escalated",
        "agent_run": {
            "intent": "billing_issue",
            "confidence": 0.97,
            "retrieved_context": (
                "Synthetic demo example: billing questions require checking "
                "the customer's account before confirming a refund."
            ),
            "draft_response": (
                "Hi Maya, thanks for contacting us. Our support team will "
                "review the billing activity and follow up with you. For your "
                "security, please do not send full payment-card details."
            ),
            "grounding_score": 0.92,
            "validation_passed": False,
            "validation_issues": [
                "Account-specific billing review is required."
            ],
            "review_required": True,
            "escalation_required": True,
            "escalation_reasons": [
                "A human must review the account before taking billing action."
            ],
        },
        "response_status": "draft",
    },
    {
        "sender": "leo@brightdesk.example",
        "subject": "Dashboard crashes when I upload a CSV",
        "body": (
            "The dashboard closes whenever I upload a CSV file. "
            "I tried twice and got the same result."
        ),
        "status": "needs_review",
        "agent_run": {
            "intent": "bug_report",
            "confidence": 0.91,
            "retrieved_context": (
                "Synthetic demo example: product troubleshooting guidance "
                "suggests collecting the steps to reproduce an issue."
            ),
            "draft_response": (
                "Hi Leo, sorry you ran into this. Could you share the "
                "approximate time of the upload and the CSV file size? "
                "Please remove any sensitive information before sharing a file."
            ),
            "grounding_score": 0.89,
            "validation_passed": True,
            "validation_issues": [],
            "review_required": True,
            "escalation_required": False,
            "escalation_reasons": [],
        },
        "response_status": "draft",
    },
    {
        "sender": "priya@cedarworks.example",
        "subject": "Can you confirm API access for our plan?",
        "body": (
            "Hi, can you help me confirm whether our current plan includes "
            "API access? I can share the plan name if needed."
        ),
        "status": "processed",
        "agent_run": {
            "intent": "product_question",
            "confidence": 0.96,
            "retrieved_context": (
                "Synthetic demo example: confirm plan-specific product "
                "availability before making a commitment."
            ),
            "draft_response": (
                "Hi Priya, thanks for reaching out. We can help confirm API "
                "availability for your plan. Please reply with your plan name; "
                "do not share your password or access tokens."
            ),
            "grounding_score": 0.94,
            "validation_passed": True,
            "validation_issues": [],
            "review_required": False,
            "escalation_required": False,
            "escalation_reasons": [],
        },
        "response_status": "sent_demo",
    },
    {
        "sender": "noah@mapleline.example",
        "subject": "Feature request: dark mode",
        "body": (
            "It would be great if the dashboard had a dark mode. "
            "Please consider it for a future update."
        ),
        "status": "new",
        "agent_run": None,
        "response_status": None,
    },
]


def seed_demo_inbox(db: Session) -> int:
    """Add sample cases once and repair saved sample intent values."""
    existing_emails = (
        db.query(Email)
        .filter(Email.source == "demo_seed")
        .all()
    )

    existing_by_pair = {
        (email.sender.lower(), email.subject.lower()): email
        for email in existing_emails
    }

    created_count = 0

    for case in DEMO_CASES:
        email_key = (
            case["sender"].lower(),
            case["subject"].lower(),
        )
        existing_email = existing_by_pair.get(email_key)
        run_data = case["agent_run"]

        if existing_email:
            # Repair an old saved intent if this case was already seeded.
            if run_data:
                saved_run = (
                    db.query(AgentRun)
                    .filter(AgentRun.email_id == existing_email.id)
                    .order_by(AgentRun.created_at.desc())
                    .first()
                )

                if saved_run:
                    saved_run.intent = run_data["intent"]

            continue

        email = Email(
            sender=case["sender"],
            recipient="support@apex.example",
            subject=case["subject"],
            body=case["body"],
            source="demo_seed",
            status=case["status"],
        )
        db.add(email)
        db.flush()

        if run_data:
            agent_run = AgentRun(
                email_id=email.id,
                intent=run_data["intent"],
                confidence=run_data["confidence"],
                retrieved_context=run_data["retrieved_context"],
                draft_response=run_data["draft_response"],
                grounding_score=run_data["grounding_score"],
                validation_passed=run_data["validation_passed"],
                validation_issues=json.dumps(
                    run_data["validation_issues"]
                ),
                review_required=run_data["review_required"],
                escalation_required=run_data["escalation_required"],
                escalation_reasons=json.dumps(
                    run_data["escalation_reasons"]
                ),
                status="completed",
            )
            db.add(agent_run)
            db.flush()

            response_status = case["response_status"]
            sent_at = (
                datetime.now(timezone.utc)
                if response_status == "sent_demo"
                else None
            )

            response = Response(
                email_id=email.id,
                agent_run_id=agent_run.id,
                content=run_data["draft_response"],
                status=response_status,
                approved_by=(
                    "Apex Demo Support Team"
                    if response_status == "sent_demo"
                    else None
                ),
                sent_at=sent_at,
            )
            db.add(response)

        existing_by_pair[email_key] = email
        created_count += 1

    db.commit()
    return created_count