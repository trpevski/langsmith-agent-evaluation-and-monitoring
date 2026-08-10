"""Example of monitoring agent in production."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.monitoring import AgentMonitor
from src.config import LANGSMITH_PROJECT


def main():
    """Run monitoring example."""
    print("Initializing agent monitor...")
    monitor = AgentMonitor(project_name=LANGSMITH_PROJECT, check_interval=300)

    print(f"Checking health for project: {LANGSMITH_PROJECT}")
    print("(This checks runs from the last 5 minutes)\n")

    # Single health check
    metrics = monitor.check_health()

    if "error" not in metrics:
        print("\n" + "="*60)
        print("METRICS SUMMARY")
        print("="*60)
        print(f"Success Rate: {metrics.get('success_rate', 0):.1%}")
        print(f"Avg Latency: {metrics.get('avg_latency', 0):.2f}s")
        print(f"Total Cost: ${metrics.get('total_cost', 0):.2f}")

    # Analyze failing runs
    print("\n" + "="*60)
    print("FAILING RUNS ANALYSIS")
    print("="*60)
    failing_runs = monitor.analyze_failing_runs(limit=5)
    if failing_runs:
        for run in failing_runs:
            print(f"Run: {run['run_id']}")
            print(f"  Error: {run['error']}")
            print(f"  Tags: {', '.join(run['tags'])}")
    else:
        print("No failing runs found!")

    # Compare versions
    print("\n" + "="*60)
    print("VERSION COMPARISON")
    print("="*60)
    comparison = monitor.get_version_comparison("version:v1", "version:v2")
    if "error" not in comparison:
        print(f"V1 Success Rate: {comparison.get('metrics_v1', {}).get('success_rate', 'N/A'):.1%}")
        print(f"V2 Success Rate: {comparison.get('metrics_v2', {}).get('success_rate', 'N/A'):.1%}")

        improvements = comparison.get("improvement", {})
        if improvements:
            print("\nImprovements:")
            for metric, improvement in improvements.items():
                direction = "⬆️ " if improvement > 0 else "⬇️ "
                print(f"  {direction} {metric}: {improvement:.1f}%")


if __name__ == "__main__":
    main()
