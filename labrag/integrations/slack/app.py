"""Slack app integration for labrag."""

import os
from collections.abc import Callable

import httpx
from dotenv import load_dotenv
from loguru import logger
from slack_bolt import App
from slack_bolt.adapter.starlette import SlackRequestHandler

from labrag.integrations.slack.utils import format_for_slack, remove_slack_mention

load_dotenv()

app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
)


def send_message(event: dict, say: Callable) -> None:
    """Send message to labrag chat endpoint."""
    message = event["text"]
    message = remove_slack_mention(message)

    # Create session_id from channel + thread combination
    session_id = f"slack_{event['channel']}_{event.get('thread_ts', event['ts'])}"

    try:
        base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

        # Prepare chat request for labrag API
        chat_request = {"message": message, "session_id": session_id}

        response = httpx.post(f"{base_url}/api/chat/", json=chat_request, timeout=60.0)
        response.raise_for_status()
        chat_response = response.json()
        reply = chat_response.get("response", "Error getting chat response.")

    except Exception as e:
        reply = f"Error processing: {e}"
        logger.error(f"Error: {e}")

    # Format and send the response to Slack
    thread_ts = event.get("thread_ts", event["ts"])
    say(markdown_text=format_for_slack(reply), thread_ts=thread_ts)


@app.event("app_mention")
def handle_mention(event: dict, say: Callable) -> None:
    """Handle when the bot is mentioned."""
    if event.get("thread_ts"):
        return  # Skip thread messages

    send_message(event, say)


@app.event("message")
def handle_thread_message(event: dict, say: Callable) -> None:
    """Handle messages in threads."""
    if not event.get("thread_ts"):
        return  # Not a thread message

    if event.get("bot_id"):
        return  # Skip bot messages

    send_message(event, say)


# Create the request handler for FastAPI integration
slack_handler = SlackRequestHandler(app)
