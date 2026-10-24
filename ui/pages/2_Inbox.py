import requests
import streamlit as st

from ui.api_client import api_request, get_error_detail, require_login


st.set_page_config(
    page_title="Inbox | SupportFlow AI",
    page_icon="📥",
    layout="wide",
)

require_login()


st.markdown(
    """
    <style>
        .stApp {
            background: #f4f7fb;
        }

        .block-container {
            max-width: 1400px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .sf-eyebrow {
            color: #4263a0;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.13em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .sf-title {
            color: #152238;
            font-size: clamp(2rem, 4vw, 2.7rem);
            font-weight: 780;
            letter-spacing: -0.055em;
            line-height: 1.08;
            margin-bottom: 0.3rem;
        }

        .sf-caption {
            color: #66758b;
            margin-bottom: 1.2rem;
        }

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #e5eaf2;
            padding: 1rem 1.1rem;
            border-radius: 15px;
            box-shadow: 0 3px 12px rgba(20, 38, 65, 0.04);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #e5eaf2 !important;
            border-radius: 15px !important;
            background: white;
        }

        div.stButton > button {
            border-radius: 10px;
            font-weight: 650;
            min-height: 2.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="sf-eyebrow">Customer support workspace</div>'
    '<div class="sf-title">Support inbox</div>'
    '<div class="sf-caption">'
    "Search cases, check their status, and open the agent workflow."
    "</div>",
    unsafe_allow_html=True,
)


if st.button("Refresh inbox", icon="🔄"):
    st.rerun()


try:
    response = api_request(
        "GET",
        "emails",
        timeout=30,
    )
    response.raise_for_status()
    emails = response.json()

except requests.RequestException as exc:
    st.error(f"Could not load the inbox: {get_error_detail(exc)}")
    st.info("Check that the SupportFlow backend is running.")
    st.stop()


status_counts = {
    "new": sum(email.get("status") == "new" for email in emails),
    "needs_review": sum(
        email.get("status") == "needs_review"
        for email in emails
    ),
    "escalated": sum(
        email.get("status") == "escalated"
        for email in emails
    ),
    "processed": sum(
        email.get("status") == "processed"
        for email in emails
    ),
}

metric_columns = st.columns(5)
metric_columns[0].metric("All cases", len(emails))
metric_columns[1].metric("New", status_counts["new"])
metric_columns[2].metric("Needs review", status_counts["needs_review"])
metric_columns[3].metric("Escalated", status_counts["escalated"])
metric_columns[4].metric("Processed", status_counts["processed"])


st.write("")

filter_column, search_column = st.columns([1, 2])

with filter_column:
    selected_status = st.selectbox(
        "Filter by status",
        options=[
            "All statuses",
            "New",
            "Needs review",
            "Escalated",
            "Processed",
        ],
    )

status_values = {
    "All statuses": "all",
    "New": "new",
    "Needs review": "needs_review",
    "Escalated": "escalated",
    "Processed": "processed",
}

with search_column:
    search_text = st.text_input(
        "Search cases",
        placeholder="Search sender, subject, or message...",
    ).strip().lower()


filtered_emails = []

for email in emails:
    email_status = email.get("status", "unknown")

    if (
        status_values[selected_status] != "all"
        and email_status != status_values[selected_status]
    ):
        continue

    searchable_text = " ".join(
        [
            email.get("sender", ""),
            email.get("recipient", ""),
            email.get("subject", ""),
            email.get("body", ""),
        ]
    ).lower()

    if search_text and search_text not in searchable_text:
        continue

    filtered_emails.append(email)


st.write("")

if not filtered_emails:
    st.info("No support cases match the selected filters.")
    st.page_link(
        "pages/1_Test_Agent.py",
        label="Create a sample case",
        icon="✍️",
    )
    st.stop()


st.caption(f"Showing {len(filtered_emails)} of {len(emails)} cases")


for email in filtered_emails:
    email_id = email.get("id")
    subject = email.get("subject") or "(no subject)"
    sender = email.get("sender") or "Unknown sender"
    recipient = email.get("recipient") or "Unknown recipient"
    body = email.get("body") or ""
    status = email.get("status", "unknown")
    status_label = status.replace("_", " ").title()

    with st.container(border=True):
        title_column, status_column, action_column = st.columns(
            [5, 1.5, 1.5]
        )

        with title_column:
            st.markdown(f"### {subject}")
            st.caption(f"From: {sender}  ·  To: {recipient}")

            preview = body[:260]
            if len(body) > 260:
                preview += "..."
            st.write(preview or "No message body.")

            if email.get("source") == "demo_seed":
                st.caption("Synthetic sample case")
            else:
                st.caption("Created in the demo workspace")

        with status_column:
            st.caption("CASE STATUS")
            st.markdown(f"**{status_label}**")

        with action_column:
            if st.button(
                "Open case",
                key=f"inbox-open-{email_id}",
                type="primary",
                use_container_width=True,
            ):
                st.session_state["selected_email_id"] = email_id
                st.switch_page("pages/3_Email_Details.py")

            if status == "new" and st.button(
                "Run agent",
                key=f"inbox-run-{email_id}",
                use_container_width=True,
            ):
                try:
                    with st.spinner("Running the agent workflow..."):
                        run_response = api_request(
                            "POST",
                            f"agent/run/{email_id}",
                            timeout=180,
                        )
                        run_response.raise_for_status()

                    st.success("Agent run completed.")
                    st.rerun()

                except requests.RequestException as exc:
                    st.error(
                        f"Could not run the agent: {get_error_detail(exc)}"
                    )