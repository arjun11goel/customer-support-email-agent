# ruff: noqa: E402
import sys
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import requests
import streamlit as st

from ui.api_client import api_request, get_error_detail, require_login


st.set_page_config(
    page_title="Knowledge Base | SupportFlow AI",
    page_icon="📚",
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
            margin-bottom: 1rem;
        }

        .sf-note {
            background: #edf4ff;
            border: 1px solid #d6e5ff;
            border-radius: 13px;
            color: #29456f;
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
            min-height: 2.55rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="sf-eyebrow">Grounded support answers</div>'
    '<div class="sf-title">Knowledge base</div>'
    '<div class="sf-caption">'
    "Browse the Markdown support documents used by the retrieval workflow."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sf-note">
        SupportFlow reads Markdown documents, splits them into chunks, and
        rebuilds the FAISS index. Retrieval currently compares wording
        similarity; it may not recognize every synonym or paraphrase.
    </div>
    """,
    unsafe_allow_html=True,
)


try:
    list_response = api_request(
        "GET",
        "knowledge-base",
        timeout=30,
    )
    list_response.raise_for_status()
    documents = list_response.json().get("documents", [])

except requests.RequestException as exc:
    st.error(
        f"Could not load the knowledge documents: {get_error_detail(exc)}"
    )
    st.info("Check that the SupportFlow backend is running.")
    st.stop()


metric_column, action_column = st.columns([2, 1])

with metric_column:
    st.metric("Knowledge documents", len(documents))

with action_column:
    st.write("")
    st.write("")

    if st.button("Rebuild FAISS index", type="primary"):
        try:
            with st.spinner("Rebuilding the local knowledge index..."):
                rebuild_response = api_request(
                    "POST",
                    "knowledge-base/rebuild",
                    timeout=180,
                )
                rebuild_response.raise_for_status()
                result = rebuild_response.json()

            st.success(
                f"Indexed {result.get('chunks_indexed', 0)} chunks "
                f"from {result.get('documents_indexed', 0)} documents."
            )

        except requests.RequestException as exc:
            st.error(
                f"Could not rebuild the index: {get_error_detail(exc)}"
            )


st.divider()
st.subheader("Available documents")


if not documents:
    st.warning("No Markdown knowledge documents were found.")
    st.stop()


selected_document = st.selectbox(
    "Choose a document to preview",
    options=documents,
)


try:
    document_response = api_request(
        "GET",
        f"knowledge-base/{selected_document}",
        timeout=30,
    )
    document_response.raise_for_status()
    document = document_response.json()

except requests.RequestException as exc:
    st.error(
        f"Could not load the selected document: {get_error_detail(exc)}"
    )
    st.stop()


with st.container(border=True):
    st.markdown(f"### 📄 {document.get('filename', selected_document)}")
    st.markdown(document.get("content") or "_This document is empty._")


st.divider()
st.caption(
    "Knowledge files are maintained in `data/knowledge_base/`. "
    "Rebuild the index after changing those files."
)