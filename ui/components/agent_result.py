import streamlit as st


def show_agent_result(result: dict):
    st.subheader("Agent Output")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Intent",
            result.get("intent") or "Not classified",
        )

    with col2:
        confidence = result.get("confidence")

        if confidence is not None:
            st.metric(
                "Confidence",
                f"{confidence:.0%}",
            )
        else:
            st.metric(
                "Confidence",
                "N/A",
            )

    st.write(
        "**Escalation:** "
        f"{'Required' if result.get('escalation_required') else 'No'}"
    )

    st.write("### Draft Response")

    st.text_area(
        "Generated response",
        value=result.get("draft_response") or "",
        height=180,
        key="agent_draft",
    )