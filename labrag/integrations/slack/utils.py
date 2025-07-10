"""Slack utility functions."""

import re


def remove_slack_mention(message: str) -> str:
    """Remove Slack mention from message."""
    # Remove <@U...> mentions
    cleaned = re.sub(r"<@U\w+>", "", message)
    # Remove extra whitespace
    return cleaned.strip()


def format_for_slack(text: str) -> str:
    """Format response text for better Slack display."""
    text = re.sub(r"(Step 1)\.", r"\1\\.", text)
    text = re.sub(r"(Step 2)\.", r"\1\\.", text)
    text = re.sub(r"(Step 3)\.", r"\1\\.", text)

    return text
