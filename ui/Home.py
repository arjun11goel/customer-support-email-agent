import os

import requests
import streamlit as st
from dotenv import load_dotenv

from api_client import (
    api_request,
    get_error_detail,
    get_backend_url,
    sign_in,
    sign_out,
)


load_dotenv()

st.set_page_config(
    page_title="SupportFlow AI",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_public_setting(name: str, default: str = "") -> str:
    """Read a setting from Streamlit secrets or environment variables."""
    try:
        secret_value = st.secrets.get(name)
    except Exception:
        secret_value = None

    return str(secret_value or os.getenv(name, default))


DEMO_EMAIL = get_public_setting(
    "DEMO_ADMIN_EMAIL",
    "demo@supportflow.ai",
)
DEMO_PASSWORD = get_public_setting("DEMO_ADMIN_PASSWORD")
DEMO_COMPANY = get_public_setting(
    "DEMO_COMPANY_NAME",
    "Apex Demo Support",
)


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

        [data-testid="stSidebar"] {
            background: #101827;
        }

        [data-testid="stSidebar"] * {
            color: #edf2f7;
        }

        .sf-brand {
            font-size: 1.2rem;
            font-weight: 750;
            letter-spacing: -0.03em;
            margin-bottom: 0.15rem;
        }

        .sf-brand-caption {
            color: #9ca9bb;
            font-size: 0.82rem;
            margin-bottom: 1.5rem;
        }

        .sf-hero {
            background: linear-gradient(120deg, #111c33, #263d68);
            padding: 2.1rem 2.3rem;
            border-radius: 22px;
            color: white;
            margin-bottom: 1.4rem;
            box-shadow: 0 14px 34px rgba(21, 38, 70, 0.16);
        }

        .sf-eyebrow {
            color: #a9c5ff;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.13em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }

        .sf-hero h1 {
            color: white;
            font-size: clamp(2rem, 4vw, 3rem);
            letter-spacing: -0.055em;
            line-height: 1.05;
            margin: 0 0 0.8rem 0;
        }

        .sf-hero p {
            color: #d4deef;
            font-size: 1rem;
            max-width: 760px;
            margin: 0;
            line-height: 1.6;
        }

        .sf-section-title {
            color: #152238;
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            margin: 1.2rem 0 0.2rem 0;
        }

        .sf-section-caption {
            color: #66758b;
            margin-bottom: 0.9rem;
        }

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #e5eaf2;
            padding: 1rem 1.1rem;
            border-radius: 15px;
            box-shadow: 0 3px 12px rgba(20, 38, 65, 0.04);
        }

        div[data-testid="stMetricLabel"] {
            color: #617087;
        }

        div[data-testid="stMetricValue"] {
            color: #152238;
            font-weight: 750;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #e5eaf2 !important;
            border-radius: 15px !important;
            background: white;
        }

        .sf-pill {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: #fff4dc;
            color: #8d5a00;
            font-weight: 700;
            font-size: 0.77rem;
        }

        div.stButton > button {
            border-radius: 10px;
            font-weight: 650;
            min-height: 2.65rem;
        }

        div[data-testid="stPageLink"] a {
            border-radius: 10px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown(
        """
        <div class="sf-brand">✉️ SupportFlow AI</div>
        <div class="sf-brand-caption">Customer support workspace</div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("access_token"):
        current_user = st.session_state.get("current_user") or {}

        st.markdown("#### Workspace")
        st.page_link(
            "pages/1_Test_Agent.py",
            label="Create support case",
            icon="✍️",
        )
        st.page_link(
            "pages/2_Inbox.py",
            label="Inbox",
            icon="📥",
        )
        st.page_link(
            "pages/4_Knowledge_Base.py",
            label="Knowledge base",
            icon="📚",
        )

        st.divider()
        st.caption("Signed in")
        st.write(current_user.get("email", DEMO_EMAIL))

        if st.button("Sign out", use_container_width=True):
            sign_out()
            st.rerun()
    else:
        st.caption("Public portfolio demo")
        st.markdown(
            '<span class="sf-pill">Synthetic demo workspace</span>',
            unsafe_allow_html=True,
        )


if st.session_state.get("auth_message"):
    st.info(st.session_state.pop("auth_message"))


if not st.session_state.get("access_token"):
    st.markdown(
        f"""
        <section class="sf-hero">
            <div class="sf-eyebrow">AI-assisted customer support</div>
            <h1>Welcome to SupportFlow AI</h1>
            <p>
                Sign in to the {DEMO_COMPANY} demo workspace to review support
                cases, inspect AI-assisted drafts, and try the agent workflow.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    left_column, center_column, right_column = st.columns([1, 1.35, 1])

    with center_column:
        with st.container(border=True):
            st.subheader("Sign in to the demo workspace")
            st.caption(
                "This portfolio demo uses synthetic emails. It does not "
                "connect to a real company mailbox or send real email."
            )

            if DEMO_PASSWORD:
                st.markdown("**Company Demo Access**")
                st.code(
                    f"Email: {DEMO_EMAIL}\nPassword: {DEMO_PASSWORD}",
                    language="text",
                )
            else:
                st.info(
                    "Set DEMO_ADMIN_PASSWORD in the Streamlit environment "
                    "to display the public demo password here."
                )

            with st.form("sign_in_form"):
                email_input = st.text_input(
                    "Work email",
                    value=DEMO_EMAIL,
                )
                password_input = st.text_input(
                    "Password",
                    value=DEMO_PASSWORD,
                    type="password",
                )
                submitted = st.form_submit_button(
                    "Sign in",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                try:
                    sign_in(email_input.strip(), password_input)
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"Could not sign in: {get_error_detail(exc)}")

    st.stop()


st.markdown(
    f"""
    <section class="sf-hero">
        <div class="sf-eyebrow">Customer support operations</div>
        <h1>{DEMO_COMPANY}</h1>
        <p>
            Review incoming support cases, retrieve relevant knowledge, and follow
            AI-generated replies through simulated sending or human review.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


health_response = None
emails = []
documents = []
backend_error = None

try:
    health_response = api_request(
        "GET",
        "health",
        include_auth=False,
        timeout=8,
    )
    health_response.raise_for_status()

    emails_response = api_request(
        "GET",
        "emails",
        timeout=15,
    )
    emails_response.raise_for_status()
    emails = emails_response.json()

    documents_response = api_request(
        "GET",
        "knowledge-base",
        timeout=15,
    )
    documents_response.raise_for_status()
    documents = documents_response.json().get("documents", [])

except requests.RequestException as exc:
    backend_error = get_error_detail(exc)


backend_online = backend_error is None

if backend_online:
    st.success("Backend connected")
else:
    st.error("Backend is not responding")
    st.caption(
        "Check the backend service and BACKEND_URL setting. "
        f"Details: {backend_error}"
    )


total_count = len(emails)
new_count = sum(email.get("status") == "new" for email in emails)
review_count = sum(
    email.get("status") == "needs_review"
    for email in emails
)
escalated_count = sum(
    email.get("status") == "escalated"
    for email in emails
)
processed_count = sum(
    email.get("status") == "processed"
    for email in emails
)

st.markdown(
    '<div class="sf-section-title">Inbox overview</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sf-section-caption">'
    "A live summary from your SupportFlow workspace."
    "</div>",
    unsafe_allow_html=True,
)

metric_columns = st.columns(5)
metric_columns[0].metric("Total cases", total_count)
metric_columns[1].metric("New", new_count)
metric_columns[2].metric("Needs review", review_count)
metric_columns[3].metric("Escalated", escalated_count)
metric_columns[4].metric("Processed", processed_count)


left_column, right_column = st.columns([1.45, 1], gap="large")

with left_column:
    st.markdown(
        '<div class="sf-section-title">Recent support cases</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sf-section-caption">'
        "Open a case to inspect its email and saved agent result."
        "</div>",
        unsafe_allow_html=True,
    )

    if not emails and backend_online:
        st.info("Your inbox is empty. Create a sample support case.")
        st.page_link(
            "pages/1_Test_Agent.py",
            label="Create a support case",
            icon="✍️",
        )
    else:
        for email in emails[:5]:
            email_id = email.get("id")

            with st.container(border=True):
                title_column, status_column, action_column = st.columns(
                    [5, 2, 1]
                )

                with title_column:
                    st.markdown(
                        f"**{email.get('subject') or '(no subject)'}**"
                    )
                    st.caption(
                        f"{email.get('sender', 'Unknown sender')} · "
                        f"{(email.get('body') or '')[:100]}"
                    )

                    if email.get("source") == "demo_seed":
                        st.caption("Synthetic example case")

                with status_column:
                    status = (
                        email.get("status", "unknown")
                        .replace("_", " ")
                        .title()
                    )
                    st.caption("STATUS")
                    st.write(status)

                with action_column:
                    if st.button(
                        "Open",
                        key=f"home-open-{email_id}",
                    ):
                        st.session_state["selected_email_id"] = email_id
                        st.switch_page("pages/3_Email_Details.py")


with right_column:
    st.markdown(
        '<div class="sf-section-title">Agent workflow</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sf-section-caption">'
        "How SupportFlow prepares a response for review."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown(
            """
            **1. Classify**  
            Identify the customer’s support intent.

            **2. Retrieve**  
            Search the Markdown knowledge base with FAISS.

            **3. Draft**  
            Generate a suggested response using the configured LLM.

            **4. Validate and route**  
            Eligible product questions may be marked sent in the demo when simulated auto-send is enabled. Other cases wait for human review.
            """
        )

    st.write("")
    st.page_link(
        "pages/1_Test_Agent.py",
        label="Create and process a case",
        icon="🤖",
    )
    st.page_link(
        "pages/4_Knowledge_Base.py",
        label="View knowledge documents",
        icon="📚",
    )


st.divider()
st.caption(
    "SupportFlow AI · Synthetic demo inbox · Eligible replies may be marked "
    "sent in the demo when enabled; other cases require human review · "
    "No real emails are sent."
)