"""Basic agent example - getting started."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agent import create_agent, run_agent


def main():
    """Run basic agent example."""
    print("Creating agent...")
    agent = create_agent()

    print("\nRunning agent with sample query...")
    result = run_agent(
        agent,
        query="What's our top customer's usage?",
        user_id="demo_user_123"
    )

    print("\n" + "="*60)
    print("RESULT")
    print("="*60)
    print(f"Query: {result['query']}")
    print(f"Steps: {result['steps']}")
    print(f"Cost: ${result['cost']:.4f}")
    print(f"User: {result['user_id']}")
    print(f"Response: {result['response']}")


if __name__ == "__main__":
    main()
