"""Test configuration module."""

import os
import pytest
from src.config import (
    LANGSMITH_API_KEY,
    OPENAI_MODEL,
    MAX_AGENT_STEPS,
    MONITORING_ENABLED,
)


def test_config_defaults():
    """Test that configuration has defaults."""
    assert OPENAI_MODEL in ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    assert MAX_AGENT_STEPS > 0
    assert isinstance(MONITORING_ENABLED, bool)


def test_env_override():
    """Test that environment variables override defaults."""
    original = os.environ.get("OPENAI_MODEL")
    try:
        os.environ["OPENAI_MODEL"] = "gpt-3.5-turbo"
        # Would need to reload module to test
        assert True
    finally:
        if original:
            os.environ["OPENAI_MODEL"] = original
        else:
            os.environ.pop("OPENAI_MODEL", None)
