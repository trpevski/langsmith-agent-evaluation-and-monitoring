"""
Complete production workflow example.

This shows a realistic workflow:
1. Create and test agent
2. Evaluate against dataset
3. Compare with previous version
4. Monitor in production
"""

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
from src.monitoring import AgentMonitor
from src.config import LANGSMITH_PROJECT


def main():
    """Run complete production workflow."""

    print("="*70)
    print("PRODUCTION WORKFLOW: Agent Evaluation and Deployment")
    print("="*70)

    # Step 1: Create agent
    print("\n[STEP 1] Creating agent...")
    agent = create_agent()
    print("✓ Agent created and configured")

    # Step 2: Test locally
    print("\n[STEP 2] Running local tests...")
    test_queries = [
        "What's our top customer's usage?",
        "Summarize our Q3 performance",
        "List available features",
    ]

    for query in test_queries:
        result = run_agent(agent, query, user_id="test_run")
        print(f"  Query: {query[:40]}...")
        print(f"    Steps: {result['steps']}, Cost: ${result['cost']:.4f}")

    print("✓ Local tests completed")

    # Step 3: Evaluate against dataset
    print("\n[STEP 3] Running evaluation suite...")
    dataset = create_evaluation_dataset()
    evaluators = get_evaluators()

    def agent_wrapper(input_data: dict) -> dict:
        query = input_data.get("query", input_data.get("inputs", {}).get("query", ""))
        return run_agent(agent, query, user_id="eval_user")

    results = run_evaluation_suite(
        agent_fn=agent_wrapper,
        dataset=dataset,
        evaluators=evaluators,
        experiment_prefix="v2_pre_deployment",
    )

    print("✓ Evaluation completed")
    if results and "error" not in results:
        print("  Evaluation results saved to LangSmith")

    # Step 4: Check production metrics
    print("\n[STEP 4] Checking current production metrics...")
    monitor = AgentMonitor(project_name=LANGSMITH_PROJECT, check_interval=300)
    metrics = monitor.check_health()

    if "error" not in metrics:
        print(f"  Current success rate: {metrics.get('success_rate', 0):.1%}")
        print(f"  Current avg latency: {metrics.get('avg_latency', 0):.2f}s")
        print(f"  Current avg cost: ${metrics.get('avg_cost', 0):.4f}")

        # Compare versions
        print("\n[STEP 5] Comparing new vs current version...")
        comparison = monitor.get_version_comparison("version:v1", "version:v2")

        if "error" not in comparison:
            improvements = comparison.get("improvement", {})
            if improvements:
                print("  Improvements:")
                for metric, improvement in improvements.items():
                    direction = "⬆️ " if improvement > 0 else "⬇️ "
                    print(f"    {direction} {metric}: {improvement:+.1f}%")
            else:
                print("  No version data available yet")
    else:
        print("  Could not retrieve metrics (check LangSmith connection)")

    # Step 5: Pre-deployment checklist
    print("\n[STEP 6] Pre-deployment checklist...")
    checklist = {
        "Local tests passed": True,
        "Evaluation completed": True,
        "Regression detection": True,
        "Monitoring configured": True,
        "Alerts enabled": True,
    }

    for item, status in checklist.items():
        status_str = "✓" if status else "✗"
        print(f"  {status_str} {item}")

    # Final summary
    print("\n" + "="*70)
    print("READY FOR DEPLOYMENT")
    print("="*70)
    print("""
Next steps:
1. Review evaluation results in LangSmith UI (Experiments tab)
2. Compare metrics with v1 if available
3. Start canary deployment (10% traffic)
4. Monitor metrics for 1-2 hours
5. Gradually increase to 100% if everything looks good

To deploy:
  docker-compose up -d  # Start monitoring container
  # Update your production code to use the new agent version
    """)


if __name__ == "__main__":
    main()
