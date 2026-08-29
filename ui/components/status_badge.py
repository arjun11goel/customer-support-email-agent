import streamlit as st


def show_status(status: str):
    status = status.lower()

    if status in {"sent", "approved", "processed"}:
        st.success(status.upper())

    elif status in {
        "needs_review",
        "awaiting_review",
        "escalated",
    }:
        st.warning(status.upper())

    elif status in {"failed", "error"}:
        st.error(status.upper())

    else:
        st.info(status.upper())