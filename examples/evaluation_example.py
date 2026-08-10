"""Example of running evaluation suite on agent."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agent import create_agent, run_agent
from src.evaluation import (
    create_evaluation_dataset,
    run_evaluation_suite,
    get_evaluators,
)


def main():
    """Run evaluation suite."""
    print("Creating agent...")
    agent = create_agent()

    print("Creating evaluation dataset...")
    dataset = create_evaluation_dataset()
    print(f"Loaded {len(dataset)} evaluation examples")

    print("\nRunning evaluation suite...")
    print("This will test the agent against all examples...")

    # Create a wrapper for the agent
    def agent_wrapper(input_data: dict) -> dict:
        query = input_data.get("query", input_data.get("inputs", {}).get("query", ""))
        result = run_agent(agent, query, user_id="eval_user")
        return result

    # Get evaluators
    evaluators = get_evaluators()

    # Run evaluation
    results = run_evaluation_suite(
        agent_fn=agent_wrapper,
        dataset=dataset,
        evaluators=evaluators,
        experiment_prefix="agent_v1_eval",
    )

    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)

    if "error" in results:
        print(f"Error: {results['error']}")
    else:
        for key, value in results.items():
            if hasattr(value, "get"):
                pass_rate = value.get("pass_rate", "N/A")
                print(f"{key}: {pass_rate}")
            else:
                print(f"{key}: {value}")


if __name__ == "__main__":
    main()
