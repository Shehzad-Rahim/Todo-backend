"""Application configuration loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env using absolute path BEFORE Settings instantiation
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_FILE, override=True)

# Fail fast if required variables are missing
_missing = []
if not os.getenv("BETTER_AUTH_SECRET"):
    _missing.append("BETTER_AUTH_SECRET")
if not os.getenv("BETTER_AUTH_BASE_URL"):
    _missing.append("BETTER_AUTH_BASE_URL")

if _missing:
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(_missing)}. "
        f"Ensure they are set in {_ENV_FILE} or as environment variables."
    )


class Settings(BaseSettings):
    """Application settings.

    Loads configuration from environment variables.
    BETTER_AUTH_SECRET and BETTER_AUTH_BASE_URL must match the frontend configuration.
    """

    better_auth_secret: str
    better_auth_base_url: str
    database_url: str = ""

    class Config:
        extra = "ignore"


settings = Settings()
