import os

import requests
import streamlit as st


st.set_page_config(
    page_title="Test Agent",
    page_icon="🤖",
    layout="wide",
)


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)


st.title("🤖 Test Customer Support Agent")

st.write(
    "Create a mock customer email and run the "
    "LangGraph agent workflow."
)


with st.form("mock_email_form"):

    sender = st.text_input(
        "Customer Email",
        value="customer@example.com",
    )

    recipient = st.text_input(
        "Support Email",
        value="support@example.com",
    )

    subject = st.text_input(
        "Subject",
        value="I was charged twice",
    )

    body = st.text_area(
        "Email Body",
        value=(
            "I was charged twice for my subscription. "
            "Can you please check this?"
        ),
        height=180,
    )

    submitted = st.form_submit_button(
        "Create & Run Agent",
        type="primary",
    )


if submitted:

    payload = {
        "sender": sender,
        "recipient": recipient,
        "subject": subject,
        "body": body,
    }

    try:

        create_response = requests.post(
            f"{BACKEND_URL}/api/v1/emails/mock",
            json=payload,
            timeout=30,
        )

        create_response.raise_for_status()

        email = create_response.json()

        st.success(
            f"Email created: {email['id']}"
        )

        run_response = requests.post(
            f"{BACKEND_URL}/api/v1/agent/run/{email['id']}",
            timeout=60,
        )

        run_response.raise_for_status()

        result = run_response.json()

        st.divider()

        st.subheader("Agent Execution")

        st.json(result)

    except requests.RequestException as exc:

        st.error(
            f"Backend request failed: {exc}"
        )