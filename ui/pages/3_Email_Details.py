import os

import requests
import streamlit as st

from ui.components.agent_result import (
    show_agent_result,
)


st.set_page_config(
    page_title="Email Details",
    page_icon="✉️",
    layout="wide",
)


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)


email_id = st.session_state.get(
    "selected_email_id"
)


st.title("✉️ Email Details")


if not email_id:

    st.warning(
        "No email selected."
    )

    st.info(
        "Open an email from the Inbox page."
    )

    st.stop()


try:

    email_response = requests.get(
        f"{BACKEND_URL}/api/v1/emails/{email_id}",
        timeout=10,
    )

    email_response.raise_for_status()

    email = email_response.json()

except requests.RequestException as exc:

    st.error(
        f"Could not load email: {exc}"
    )

    st.stop()


st.subheader(email["subject"])

st.caption(
    f"From: {email['sender']}"
)

st.caption(
    f"To: {email['recipient']}"
)

st.divider()

st.write(email["body"])

st.divider()

st.subheader("AI Agent Analysis")


try:

    agent_response = requests.get(
        f"{BACKEND_URL}/api/v1/agent/runs/{email_id}",
        timeout=10,
    )

    agent_response.raise_for_status()

    agent_result = agent_response.json()

except requests.RequestException:

    agent_result = None


if not agent_result:

    st.info(
        "This email has not been processed by "
        "the AI agent yet."
    )

    if st.button(
        "Run AI Agent",
        type="primary",
    ):

        try:

            run_response = requests.post(
                f"{BACKEND_URL}/api/v1/agent/run/{email_id}",
                timeout=60,
            )

            run_response.raise_for_status()

            st.success(
                "Agent execution completed."
            )

            st.rerun()

        except requests.RequestException as exc:

            st.error(
                f"Agent execution failed: {exc}"
            )

else:

    show_agent_result(agent_result)

    st.divider()

    st.subheader(
        "Retrieved Knowledge"
    )

    context = agent_result.get(
        "retrieved_context",
        [],
    )

    if context:

        for item in context:
            st.info(item)

    else:

        st.caption(
            "No knowledge retrieved yet."
        )

    st.divider()

    st.subheader(
        "Human Review"
    )

    st.info(
        "Human approval workflow will be "
        "connected after the core agent is implemented."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.button(
            "Approve Response",
            disabled=True,
        )

    with col2:

        st.button(
            "Send Response",
            disabled=True,
        )