"""Simple FastAPI service for Slack integration."""

from fastapi import FastAPI, Request

from labrag.integrations.slack.app import slack_handler

app = FastAPI(title="LabRAG Slack Integration")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.api_route("/slack/events", methods=["POST"])
async def slack_events(req: Request) -> dict:
    """Handle Slack events."""
    return await slack_handler.handle(req)
