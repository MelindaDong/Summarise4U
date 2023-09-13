import streamlit as st

from dotenv import load_dotenv
import os

load_dotenv()


def sidebar():
    with st.sidebar:
        st.markdown(
            "## How to use\n"
            "1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) below🔑\n"  # noqa: E501
            "2. Upload a pdf document\n"
            "3. Get a summary of the document\n"
            "4. Ask questions about the summary\n"
            "5. Update the summary based on your interest\n"
        )
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="Paste your OpenAI API key here (sk-...)",
            help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
            value=os.environ.get("OPENAI_API_KEY", None)
            or st.session_state.get("OPENAI_API_KEY", ""),
        )

        st.session_state["OPENAI_API_KEY"] = api_key_input

        st.markdown("---")
        st.markdown("# About")
        st.markdown(
            "Summarize4U is a web application to summarize your pdf documents. "
            "and be able to update the summary based on your interest. "
            "at the moment, the setting is optimized for summarizing AI research papers. "
            "more features will be added in the future. "
        )
       