import requests
import streamlit as st

from ui.api_client import api_request, get_error_detail, require_login


st.set_page_config(
    page_title="Create Case | SupportFlow AI",
    page_icon="🤖",
    layout="wide",
)

require_login()


SAMPLE_CASES = {
    "Billing: duplicate charge": {
        "subject": "I was charged twice",
        "body": (
            "I was charged twice for my subscription this month. "
            "Could you please check the charges and let me know what "
            "happens next?"
        ),
    },
    "Product: ask a question": {
        "subject": "How do I invite a teammate?",
        "body": (
            "I am setting up my workspace and would like to invite "
            "a teammate. Where can I find the invitation option?"
        ),
    },
    "Bug: report a problem": {
        "subject": "I cannot sign in",
        "body": (
            "I cannot sign in to my account. I have tried refreshing "
            "the page, but I still see an error. Can you help me?"
        ),
    },
    "Custom message": {
        "subject": "",
        "body": "",
    },
}


st.markdown(
    """
    <style>
        .stApp {
            background: #f4f7fb;
        }

        .block-container {
            max-width: 1200px;
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
            margin-bottom: 1rem;
        }

        .sf-note {
            background: #fff4dc;
            border: 1px solid #f3dda8;
            border-radius: 13px;
            color: #744b08;
            padding: 1rem 1.1rem;
            margin: 1rem 0;
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
            min-height: 2.6rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="sf-eyebrow">Agent workspace</div>'
    '<div class="sf-title">Create a support case</div>'
    '<div class="sf-caption">'
    "Submit a sample customer email and review the agent workflow."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sf-note">
        This page uses synthetic email only. The workflow can create a draft for
        human review or, when simulated auto-send is enabled and every safety check
        passes, mark an eligible reply as sent in the demo. No real email is sent.
    </div>
    """,
    unsafe_allow_html=True,
)


selected_sample = st.selectbox(
    "Start with a sample",
    options=list(SAMPLE_CASES.keys()),
)
sample = SAMPLE_CASES[selected_sample]


with st.container(border=True):
    st.subheader("Customer email")

    with st.form("create_support_case_form"):
        sender = st.text_input(
            "Customer email address",
            value="customer@example.com",
        )
        recipient = st.text_input(
            "Support email address",
            value="support@apex.example",
        )
        subject = st.text_input(
            "Subject",
            value=sample["subject"],
            placeholder="Enter the email subject",
        )
        body = st.text_area(
            "Message",
            value=sample["body"],
            height=190,
            placeholder="Enter the customer's message",
        )

        submitted = st.form_submit_button(
            "Create case and run agent",
            type="primary",
        )


if submitted:
    st.session_state.pop("last_agent_result", None)

    if not sender.strip():
        st.error("Enter the customer email address.")

    elif not recipient.strip():
        st.error("Enter the support email address.")

    elif not subject.strip():
        st.error("Enter a subject before submitting the case.")

    elif not body.strip():
        st.error("Enter a message before submitting the case.")

    else:
        try:
            with st.spinner(
                "Creating the case and running the AI workflow..."
            ):
                create_response = api_request(
                    "POST",
                    "emails/mock",
                    json={
                        "sender": sender.strip(),
                        "recipient": recipient.strip(),
                        "subject": subject.strip(),
                        "body": body.strip(),
                    },
                    timeout=30,
                )
                create_response.raise_for_status()
                email = create_response.json()

                run_response = api_request(
                    "POST",
                    f"agent/run/{email['id']}",
                    timeout=180,
                )
                run_response.raise_for_status()
                result = run_response.json()

            st.session_state["selected_email_id"] = email["id"]
            st.session_state["last_agent_result"] = result
            st.success("Case created and agent workflow completed.")

        except requests.RequestException as exc:
            st.error(f"Could not process the case: {get_error_detail(exc)}")


result = st.session_state.get("last_agent_result")

if result:
    st.divider()
    st.subheader("Agent run summary")

    metric_columns = st.columns(5)

    intent = result.get("intent") or "unknown"
    metric_columns[0].metric(
        "Detected intent",
        intent.replace("_", " ").title(),
    )

    confidence = result.get("confidence")
    metric_columns[1].metric(
        "Confidence",
        f"{float(confidence):.0%}" if confidence is not None else "N/A",
    )

    grounding_score = result.get("grounding_score")
    metric_columns[2].metric(
        "Knowledge overlap",
        (
            f"{float(grounding_score):.0%}"
            if grounding_score is not None
            else "N/A"
        ),
    )

    validation_passed = result.get("validation_passed")
    validation_label = (
        "Passed"
        if validation_passed is True
        else "Needs review"
        if validation_passed is False
        else "Not available"
    )
    metric_columns[3].metric("Validation", validation_label)

    workflow_status = (result.get("status") or "unknown")
    metric_columns[4].metric(
        "Run status",
        workflow_status.replace("_", " ").title(),
    )

    if result.get("status") == "auto_sent_demo":
        st.success(
            "The eligible reply was marked sent in the demo. "
            "No email was sent."
        )

    elif result.get("escalation_required"):
        st.warning("The agent recommends escalating this case.")

        for reason in result.get("escalation_reasons") or []:
            st.write(f"- {reason}")

    elif result.get("review_required", True):
        st.info("The draft is waiting for human review.")

    else:
        st.info("The agent run completed.")

    if result.get("error"):
        st.warning(f"Workflow issue: {result['error']}")

    if st.button("Open case review", type="primary"):
        st.session_state["selected_email_id"] = result["email_id"]
        st.switch_page("pages/3_Email_Details.py")