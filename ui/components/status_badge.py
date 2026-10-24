import streamlit as st


def show_status(status: str) -> None:
    """Display a status using a matching Streamlit color."""
    normalized_status = (status or "unknown").lower()

    if normalized_status in {
        "sent",
        "sent_demo",
        "approved",
        "processed",
    }:
        st.success(normalized_status.upper())

    elif normalized_status in {
        "needs_review",
        "awaiting_review",
        "escalated",
    }:
        st.warning(normalized_status.upper())

    elif normalized_status in {
        "failed",
        "error",
        "classification_failed",
        "retrieval_failed",
        "generation_failed",
    }:
        st.error(normalized_status.upper())

    else:
        st.info(normalized_status.upper())