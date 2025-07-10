import os
import uuid

import requests
import streamlit as st

# Configuration
API_URL = os.getenv("LABRAG_API_URL", "http://localhost:8000/api/chat/")
REQUEST_TIMEOUT = 45

# Page config
st.set_page_config(
    page_title="LabRAG - AI Research Assistant",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state() -> None:
    """Initialize session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    # Ensure the conversation list exists
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Track how many questions have been asked
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0


def clear_conversation() -> None:
    """Clear the conversation history."""
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.total_questions = 0
    st.rerun()


def display_welcome_message() -> None:
    """Display welcome message when no conversations exist."""
    if not st.session_state.messages:
        st.markdown(
            """
        <div class="welcome-card">
            <h3>🧬 Welcome to LabRAG!</h3>
            <p>Your AI Research Assistant for Lab Papers & Media Coverage</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


def display_chat_history() -> None:
    """Display the chat history with improved styling."""
    for _i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and msg["content"].startswith("❌"):
                st.error(msg["content"])
            else:
                st.markdown(msg["content"])


def send_message_to_api(message: str, session_id: str) -> dict[str, str]:
    """Send message to the API and return response."""
    try:
        with st.spinner("🧬 Analyzing your research question..."):
            # # Add a progress bar for better UX
            # progress_bar = st.progress(0)
            # for i in range(100):
            #     progress_bar.progress(i + 1)

            response = requests.post(
                API_URL,
                json={"message": message, "session_id": session_id},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            # progress_bar.empty()
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


def display_sidebar() -> None:
    """Display improved sidebar with about info and example queries."""
    with st.sidebar:
        st.title("🧬 LabRAG")
        st.markdown("""
LabRAG helps you explore and understand scientific papers and media coverage.

- Ask about research findings, methods, or media articles.
- All answers include direct citations and references to the original sources.
- Supports both research and general chat queries.
""")

        with st.expander("💡 Example Queries"):
            st.markdown("""
- Hi, how are you?
- What genes are important for human adaptation in the Amazon?
- How is this research covered in the media?
- Explain the methodology of the DSL paper.
- What abbreviations should I know to better understand this paper?
""")

        st.markdown(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
        if st.button("🔄 Clear Chat History"):
            clear_conversation()


def main() -> None:
    """Main application with enhanced aesthetics."""
    # Initialize session state
    initialize_session_state()

    # Sidebar
    display_sidebar()

    # Main content area
    main_container = st.container()

    with main_container:
        # Welcome message or chat history
        if not st.session_state.messages:
            display_welcome_message()
        else:
            display_chat_history()

    # User input with enhanced styling
    if prompt := st.chat_input(
        "💬 Ask about your research papers and media coverage...", key="main_input"
    ):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get API response with enhanced feedback
        api_response = send_message_to_api(prompt, st.session_state.session_id)

        # Handle response with better error styling
        if "error" in api_response:
            assistant_msg = f"🚨 **Error:** {api_response['error']}"
        else:
            assistant_msg = api_response.get(
                "response", "⚠️ No response received from the assistant."
            )

        # Add assistant message to history
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_msg}
        )
        with st.chat_message("assistant"):
            if assistant_msg.startswith("🚨"):
                st.error(assistant_msg)
            else:
                st.markdown(assistant_msg)


if __name__ == "__main__":
    main()
