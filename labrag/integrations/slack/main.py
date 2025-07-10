"""Simple FastAPI service for Slack integration."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from labrag.integrations.slack.app import slack_handler

app = FastAPI(title="LabRAG Slack Integration")


@app.get("/slack/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.api_route("/slack/events", methods=["POST"])
async def slack_events(req: Request) -> JSONResponse:
    """Handle Slack events."""
    body = await req.json()

    # Handle Slack's URL verification challenge
    if body.get("type") == "url_verification":
        return JSONResponse(content={"challenge": body["challenge"]})

    # Delegate all other events to the Bolt handler
    return await slack_handler.handle(req)
