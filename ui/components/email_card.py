import streamlit as st


def show_email_card(email: dict):
    with st.container(border=True):
        st.write(f"**{email.get('subject', 'No subject')}**")
        st.caption(
            f"From: {email.get('sender', 'Unknown')}"
        )

        st.write(
            email.get("body", "")[:200]
            + (
                "..."
                if len(email.get("body", "")) > 200
                else ""
            )
        )

        st.caption(
            f"Status: {email.get('status', 'unknown')}"
        )