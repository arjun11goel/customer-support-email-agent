import requests
import streamlit as st

from ui.api_client import api_request, get_error_detail, require_login
from ui.components.status_badge import show_status


st.set_page_config(
    page_title="Case Review | SupportFlow AI",
    page_icon="✉️",
    layout="wide",
)

require_login()


def percent_value(value) -> str:
    """Format a numeric score as a percentage."""
    if value is None:
        return "N/A"

    try:
        return f"{float(value):.0%}"
    except (TypeError, ValueError):
        return "N/A"


email_id = st.session_state.get("selected_email_id")


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
            font-size: clamp(1.9rem, 4vw, 2.6rem);
            font-weight: 780;
            letter-spacing: -0.05em;
            line-height: 1.1;
            margin-bottom: 0.35rem;
        }

        .sf-caption {
            color: #66758b;
            margin-bottom: 1rem;
        }

        .sf-section-title {
            color: #152238;
            font-size: 1.2rem;
            font-weight: 720;
            letter-spacing: -0.025em;
            margin: 0.4rem 0 0.7rem 0;
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
            min-height: 2.55rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="sf-eyebrow">Human review</div>'
    '<div class="sf-title">Support case review</div>'
    '<div class="sf-caption">'
    "Inspect the customer message, agent analysis, and suggested reply."
    "</div>",
    unsafe_allow_html=True,
)


if not email_id:
    st.warning("No case is selected.")
    st.page_link(
        "pages/2_Inbox.py",
        label="Return to the inbox",
        icon="📥",
    )
    st.stop()


try:
    email_response = api_request(
        "GET",
        f"emails/{email_id}",
        timeout=30,
    )
    email_response.raise_for_status()
    email = email_response.json()

except requests.RequestException as exc:
    st.error(f"Could not load this case: {get_error_detail(exc)}")
    st.stop()


st.markdown(f"### {email.get('subject') or '(no subject)'}")
st.caption(
    f"From: {email.get('sender', 'Unknown sender')}  ·  "
    f"To: {email.get('recipient', 'Unknown recipient')}"
)

status_column, source_column, case_column = st.columns(3)

with status_column:
    st.caption("CASE STATUS")
    show_status(email.get("status", "unknown"))

with source_column:
    st.caption("EMAIL SOURCE")
    source = email.get("source") or "mock"
    st.write(source.replace("_", " ").title())

with case_column:
    st.caption("CASE ID")
    st.code(str(email_id), language=None)


with st.container(border=True):
    st.markdown(
        '<div class="sf-section-title">Customer message</div>',
        unsafe_allow_html=True,
    )
    st.write(email.get("body") or "No message body was provided.")


st.markdown(
    '<div class="sf-section-title">Agent analysis</div>',
    unsafe_allow_html=True,
)


try:
    run_response = api_request(
        "GET",
        f"agent/runs/{email_id}",
        timeout=30,
    )
    run_response.raise_for_status()
    agent_run = run_response.json()

except requests.RequestException as exc:
    st.error(f"Could not load the agent result: {get_error_detail(exc)}")
    st.stop()


if not agent_run:
    st.info("This case has not been processed by the agent yet.")

    if st.button("Run AI agent", type="primary", icon="🤖"):
        try:
            with st.spinner("Running the support workflow..."):
                result_response = api_request(
                    "POST",
                    f"agent/run/{email_id}",
                    timeout=180,
                )
                result_response.raise_for_status()

            st.success("Agent run completed and saved.")
            st.rerun()

        except requests.RequestException as exc:
            st.error(f"Agent run failed: {get_error_detail(exc)}")

    st.page_link(
        "pages/2_Inbox.py",
        label="Return to the inbox",
        icon="📥",
    )
    st.stop()


metric_columns = st.columns(3)

intent = agent_run.get("intent") or "unknown"
metric_columns[0].metric(
    "Detected intent",
    intent.replace("_", " ").title(),
)
metric_columns[1].metric(
    "Classification confidence",
    percent_value(agent_run.get("confidence")),
)
metric_columns[2].metric(
    "Knowledge overlap",
    percent_value(agent_run.get("grounding_score")),
)


if agent_run.get("error"):
    st.warning(f"Workflow issue: {agent_run['error']}")


validation_column, escalation_column = st.columns(2)

with validation_column:
    with st.container(border=True):
        st.markdown("#### Draft validation")

        if agent_run.get("validation_passed"):
            st.success("The draft passed the local validation checks.")
        else:
            st.warning("The draft needs human review.")

        validation_issues = agent_run.get("validation_issues") or []

        if validation_issues:
            st.write("Review notes:")
            for issue in validation_issues:
                st.write(f"- {issue}")
        elif agent_run.get("validation_passed"):
            st.caption("No validation issues were reported.")


with escalation_column:
    with st.container(border=True):
        st.markdown("#### Escalation")

        if agent_run.get("escalation_required"):
            st.error("Escalation is recommended.")

            for reason in agent_run.get("escalation_reasons") or []:
                st.write(f"- {reason}")
        else:
            st.info("The workflow did not detect an escalation reason.")


st.markdown(
    '<div class="sf-section-title">Retrieved knowledge</div>',
    unsafe_allow_html=True,
)

retrieved_context = agent_run.get("retrieved_context") or []

if retrieved_context:
    for number, excerpt in enumerate(retrieved_context, start=1):
        with st.expander(f"Knowledge result {number}"):
            st.write(excerpt)
else:
    st.info("No knowledge excerpts were retrieved for this case.")


response_id = agent_run.get("response_id")

if not response_id:
    st.warning("No saved response draft is linked to this agent run.")
    st.stop()


try:
    saved_response_result = api_request(
        "GET",
        f"responses/{response_id}",
        timeout=30,
    )
    saved_response_result.raise_for_status()
    saved_response = saved_response_result.json()

except requests.RequestException as exc:
    st.error(f"Could not load the saved draft: {get_error_detail(exc)}")
    st.stop()


st.markdown(
    '<div class="sf-section-title">Suggested reply</div>',
    unsafe_allow_html=True,
)

response_status = saved_response.get("status", "unknown")
draft_widget_key = f"draft-editor-{response_id}"

if draft_widget_key not in st.session_state:
    st.session_state[draft_widget_key] = saved_response.get("content", "")


with st.container(border=True):
    st.caption("RESPONSE STATUS")
    show_status(response_status)

    if response_status == "draft":
        with st.form(f"response-review-{response_id}"):
            st.text_area(
                "Edit the reply before approval",
                key=draft_widget_key,
                height=220,
                help="Changes are saved to the demo workspace.",
            )

            current_user = st.session_state.get("current_user") or {}
            reviewer = st.text_input(
                "Reviewer name",
                value=current_user.get("email", "support_agent"),
            )

            save_clicked = st.form_submit_button("Save draft")
            approve_clicked = st.form_submit_button(
                "Save and approve draft",
                type="primary",
            )

        if save_clicked:
            try:
                update_response = api_request(
                    "PUT",
                    f"responses/{response_id}",
                    json={
                        "content": st.session_state[draft_widget_key],
                    },
                    timeout=30,
                )
                update_response.raise_for_status()
                st.success("Draft changes saved.")

            except requests.RequestException as exc:
                st.error(f"Could not save the draft: {get_error_detail(exc)}")

        if approve_clicked:
            try:
                update_response = api_request(
                    "PUT",
                    f"responses/{response_id}",
                    json={
                        "content": st.session_state[draft_widget_key],
                    },
                    timeout=30,
                )
                update_response.raise_for_status()

                approval_response = api_request(
                    "POST",
                    f"responses/{response_id}/approve",
                    json={"approved_by": reviewer.strip() or "support_agent"},
                    timeout=30,
                )
                approval_response.raise_for_status()

                st.success("Draft approved.")
                st.rerun()

            except requests.RequestException as exc:
                st.error(
                    f"Could not approve the draft: {get_error_detail(exc)}"
                )

    else:
        st.write(saved_response.get("content", ""))

    if response_status == "approved":
        approved_by = saved_response.get("approved_by") or "a reviewer"
        st.success(f"Approved by {approved_by}.")

        st.warning(
            "Demo action only: this records a sent status in the app. "
            "It does not send an email."
        )

        if st.button("Mark as sent (demo only)", icon="📨"):
            try:
                send_result = api_request(
                    "POST",
                    f"responses/{response_id}/send",
                    timeout=30,
                )
                send_result.raise_for_status()

                st.success("Demo send recorded. No email was sent.")
                st.rerun()

            except requests.RequestException as exc:
                st.error(
                    f"Could not record the demo send: "
                    f"{get_error_detail(exc)}"
                )

    elif response_status == "sent_demo":
        st.success("Demo send recorded. No email was sent.")


st.divider()

st.page_link(
    "pages/2_Inbox.py",
    label="Back to inbox",
    icon="📥",
)