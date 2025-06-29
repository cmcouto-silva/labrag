"""Settings for LabRAG."""

from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Essential environment variables only."""

    # Required
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Optional
    firecrawl_api_key: str | None = Field(default=None, description="Firecrawl API key")
    vision_agent_api_key: str | None = Field(
        default=None, description="Vision Agent API key"
    )

    # LangSmith (optional for debugging/tracing)
    langsmith_tracing: bool = Field(
        default=False, description="Enable LangSmith tracing"
    )
    langsmith_api_key: str | None = Field(default=None, description="LangSmith API key")
    langsmith_project: str = Field(
        default="labrag", description="LangSmith project name"
    )
    langsmith_endpoint: str = Field(
        default="https://api.smith.langchain.com", description="LangSmith endpoint"
    )

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


def load_config(config_path: str | Path = "configs/default.yml") -> dict[str, str]:
    """Load user configuration from YAML file."""
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file) as f:
        return yaml.safe_load(f) or {}


def load_prompt_templates(
    prompts_path: str | Path = "configs/prompts.yml",
) -> dict[str, str]:
    """Load prompt templates from YAML file."""
    prompts_file = Path(prompts_path)

    if not prompts_file.exists():
        raise FileNotFoundError(f"Prompts file not found: {prompts_file}")

    with open(prompts_file) as f:
        return yaml.safe_load(f) or {}
