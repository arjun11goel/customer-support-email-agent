import os

import requests
import streamlit as st


API_PREFIX = "/api/v1"


def get_backend_url() -> str:
    """Read the backend URL from Streamlit secrets or environment variables."""
    try:
        secret_url = st.secrets.get("BACKEND_URL")
    except Exception:
        secret_url = None

    backend_url = secret_url or os.getenv(
        "BACKEND_URL",
        "http://127.0.0.1:8000",
    )
    return backend_url.rstrip("/")


def api_request(
    method: str,
    endpoint: str,
    *,
    include_auth: bool = True,
    **kwargs,
) -> requests.Response:
    """Send a request to the backend and attach the session token."""
    endpoint = endpoint.lstrip("/")
    url = f"{get_backend_url()}{API_PREFIX}/{endpoint}"

    headers = dict(kwargs.pop("headers", {}))
    token = st.session_state.get("access_token")

    if include_auth and token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        **kwargs,
    )

    if response.status_code == 401 and include_auth:
        st.session_state.pop("access_token", None)
        st.session_state.pop("current_user", None)
        st.session_state["auth_message"] = (
            "Your session expired. Please sign in again."
        )
        st.rerun()

    return response


def sign_in(email: str, password: str) -> dict:
    """Sign in and save the returned token in the Streamlit session."""
    response = api_request(
        "POST",
        "auth/login",
        include_auth=False,
        json={
            "email": email,
            "password": password,
        },
        timeout=20,
    )
    response.raise_for_status()

    login_data = response.json()
    st.session_state["access_token"] = login_data["access_token"]
    st.session_state["current_user"] = login_data.get(
        "user",
        {"email": email},
    )
    return login_data


def sign_out() -> None:
    """Clear the signed-in user from this browser session."""
    st.session_state.pop("access_token", None)
    st.session_state.pop("current_user", None)


def require_login() -> None:
    """Stop a protected page when the user has not signed in."""
    if not st.session_state.get("access_token"):
        st.warning("Sign in from the SupportFlow home page to continue.")
        st.stop()


def get_error_detail(exc: requests.RequestException) -> str:
    """Use the backend's message when an API request fails."""
    response = getattr(exc, "response", None)

    if response is not None:
        try:
            detail = response.json().get("detail")
            if detail:
                return str(detail)
        except (ValueError, AttributeError):
            pass

    return str(exc)