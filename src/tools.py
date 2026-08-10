"""Tool definitions for the agent."""

from langchain.tools import tool
from typing import List, Dict, Any


@tool
def search_documentation(query: str) -> str:
    """
    Search internal documentation for relevant information.

    Args:
        query: Search query string

    Returns:
        Search results as a formatted string
    """
    # Simulate search with proper instrumentation
    results = f"Found 3 docs matching '{query}'"
    return results


@tool
def fetch_user_data(user_id: str) -> Dict[str, Any]:
    """
    Fetch user context for personalization.

    Args:
        user_id: Unique user identifier

    Returns:
        Dictionary containing user information
    """
    # In production, this hits your database
    return {
        "user_id": user_id,
        "subscription": "pro",
        "usage_this_month": 450,
        "created_at": "2024-01-15",
        "tier": "enterprise",
    }


@tool
def create_summary(content: str, max_length: int = 200) -> str:
    """
    Summarize content to specified length.

    Args:
        content: Content to summarize
        max_length: Maximum length of summary

    Returns:
        Summarized content
    """
    return f"Summary of {len(content)} chars to {max_length} max"


@tool
def get_usage_metrics(user_id: str) -> Dict[str, Any]:
    """
    Get usage metrics for a specific user.

    Args:
        user_id: User identifier

    Returns:
        Usage metrics and analytics
    """
    return {
        "user_id": user_id,
        "api_calls_today": 234,
        "tokens_used": 45678,
        "cost_today": 2.45,
        "remaining_quota": 1500000,
    }


@tool
def list_available_features() -> List[str]:
    """
    List all available features for the user.

    Returns:
        List of feature names
    """
    return [
        "analytics",
        "real-time-monitoring",
        "custom-alerts",
        "api-access",
        "webhooks",
        "sso",
    ]
