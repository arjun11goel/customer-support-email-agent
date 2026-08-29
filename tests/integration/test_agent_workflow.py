from app.ai.workflow.graph import agent_graph


def test_agent_graph_runs():
    state = {
        "email_id": "test-email",
        "sender": "customer@example.com",
        "recipient": "support@example.com",
        "subject": "Test email",
        "body": "I have a question.",
        "status": "started",
    }

    result = agent_graph.invoke(state)

    assert result["email_id"] == "test-email"
    assert "status" in result
    assert "draft_response" in result