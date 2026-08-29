import os

import requests
import streamlit as st


st.set_page_config(
    page_title="SupportFlow AI",
    page_icon="📨",
    layout="wide",
)


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)


st.title("📨 SupportFlow AI")

st.caption(
    "Agentic Customer Support Email System"
)


try:
    response = requests.get(
        f"{BACKEND_URL}/api/v1/health",
        timeout=5,
    )

    backend_online = response.ok

except requests.RequestException:
    backend_online = False


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Backend",
        "Online" if backend_online else "Offline",
    )

with col2:
    st.metric(
        "Agent",
        "Scaffold",
    )

with col3:
    st.metric(
        "Email Provider",
        "Mock",
    )


st.divider()

st.subheader("Current Architecture")

st.code(
    """
Customer Email
      ↓
FastAPI
      ↓
Agent Service
      ↓
LangGraph
      ↓
Classification
      ↓
Retrieval
      ↓
Response Generation
      ↓
Validation
      ↓
Human Review
    """,
    language="text",
)


st.info(
    "Use the Test Agent page to create mock emails "
    "and execute the initial workflow."
)