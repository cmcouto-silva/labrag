import os
import uuid

import requests
import streamlit as st

# Configuration
API_URL = os.getenv("LABRAG_API_URL", "http://localhost:8000/chat/")
REQUEST_TIMEOUT = 45

# Page config
st.set_page_config(
    page_title="LabRAG Chatbot",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def initialize_session_state() -> None:
    """Initialize session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []


def clear_conversation() -> None:
    """Clear the conversation history."""
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.rerun()


def display_chat_history() -> None:
    """Display the chat history."""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def send_message_to_api(message: str, session_id: str) -> dict[str, str]:
    """Send message to the API and return response."""
    try:
        with st.spinner("🧬 Analyzing your research question..."):
            response = requests.post(
                API_URL,
                json={"message": message, "session_id": session_id},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again with a shorter question."}
    except requests.exceptions.ConnectionError:
        return {
            "error": (
                "Cannot connect to LabRAG API. Please ensure the server is running."
            )
        }
    except requests.exceptions.HTTPError as e:
        return {"error": f"API error ({e.response.status_code}): {e.response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e!s}"}


def main() -> None:
    """Main application."""
    initialize_session_state()

    # Header
    st.title("🧬 LabRAG Chatbot")
    st.markdown("*Your AI Research Assistant for Lab Papers & Media*")

    # Sidebar for session management
    with st.sidebar:
        st.header("Session Controls")
        if st.button("🗑️ Clear Conversation", type="secondary"):
            clear_conversation()

        st.markdown("---")
        st.markdown(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
        st.markdown(f"**Messages:** {len(st.session_state.messages)}")

    # Display chat history
    display_chat_history()

    # User input
    if prompt := st.chat_input("Ask about your research papers and media coverage..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get API response
        api_response = send_message_to_api(prompt, st.session_state.session_id)

        # Handle response
        if "error" in api_response:
            assistant_msg = f"❌ **Error:** {api_response['error']}."
        else:
            assistant_msg = api_response.get(
                "response", "❌ No response received from the assistant."
            )

        # Add assistant message to history
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_msg}
        )
        with st.chat_message("assistant"):
            st.markdown(assistant_msg)


if __name__ == "__main__":
    main()
