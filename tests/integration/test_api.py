import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


@pytest.fixture(scope="module")
def client():
    """Start the app once so its startup setup runs for these API tests."""
    with TestClient(app) as test_client:
        yield test_client


def sign_in(client: TestClient) -> str:
    """Sign in with the configured demo account and return its token."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": settings.DEMO_ADMIN_EMAIL,
            "password": settings.DEMO_ADMIN_PASSWORD,
        },
    )

    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_root_endpoint(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "SupportFlow AI"


def test_health_endpoint_is_public(client: TestClient):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_workspace_api_requires_login(client: TestClient):
    response = client.get("/api/v1/emails")

    assert response.status_code == 401


def test_demo_login_and_current_user(client: TestClient):
    access_token = sign_in(client)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == settings.DEMO_ADMIN_EMAIL


def test_demo_login_can_view_seeded_inbox(client: TestClient):
    access_token = sign_in(client)

    response = client.get(
        "/api/v1/emails",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    emails = response.json()
    assert len(emails) >= 4
    assert any(email.get("source") == "demo_seed" for email in emails)