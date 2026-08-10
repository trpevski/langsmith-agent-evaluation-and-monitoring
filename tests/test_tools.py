"""Test tools module."""

import pytest
from src.tools import (
    search_documentation,
    fetch_user_data,
    create_summary,
    get_usage_metrics,
    list_available_features,
)


def test_search_documentation():
    """Test search_documentation tool."""
    result = search_documentation("test query")
    assert isinstance(result, str)
    assert "test query" in result


def test_fetch_user_data():
    """Test fetch_user_data tool."""
    result = fetch_user_data("user_123")
    assert isinstance(result, dict)
    assert "user_id" in result
    assert result["user_id"] == "user_123"


def test_create_summary():
    """Test create_summary tool."""
    content = "This is a long piece of content that needs to be summarized"
    result = create_summary(content)
    assert isinstance(result, str)


def test_get_usage_metrics():
    """Test get_usage_metrics tool."""
    result = get_usage_metrics("user_123")
    assert isinstance(result, dict)
    assert "api_calls_today" in result
    assert "tokens_used" in result
    assert "cost_today" in result


def test_list_available_features():
    """Test list_available_features tool."""
    result = list_available_features()
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(f, str) for f in result)
