"""Production monitoring and alerting for agent."""

from langsmith import Client
from langsmith.schemas import Run
from datetime import datetime, timedelta
from typing import Dict, List, Any
import time
from .config import (
    LANGSMITH_PROJECT,
    MONITORING_INTERVAL,
    FAILURE_RATE_THRESHOLD,
    LATENCY_THRESHOLD,
    COST_ALERT_THRESHOLD,
)


class AgentMonitor:
    """Monitor agent health in production."""

    def __init__(self, project_name: str = LANGSMITH_PROJECT, check_interval: int = MONITORING_INTERVAL):
        """
        Initialize agent monitor.

        Args:
            project_name: LangSmith project name
            check_interval: Check interval in seconds
        """
        self.client = Client()
        self.project_name = project_name
        self.check_interval = check_interval
        self.running = False

    def start(self):
        """Start continuous monitoring."""
        self.running = True
        while self.running:
            try:
                self.check_health()
            except Exception as e:
                print(f"Error in monitoring: {e}")

            time.sleep(self.check_interval)

    def stop(self):
        """Stop monitoring."""
        self.running = False

    def check_health(self) -> Dict[str, Any]:
        """
        Check agent health metrics.

        Returns:
            Health metrics dictionary
        """
        # Get runs from last check interval
        time_window = datetime.now() - timedelta(seconds=self.check_interval)

        try:
            runs = self.client.list_runs(
                project_name=self.project_name,
                filter=f"create_time > {time_window.isoformat()}",
            )

            runs_list = list(runs)
            if not runs_list:
                print(f"[{datetime.now()}] No runs to analyze")
                return {"status": "no_runs"}

            # Calculate metrics
            metrics = self._calculate_metrics(runs_list)

            # Print report
            self._print_health_report(metrics)

            # Check alert conditions
            self._check_alerts(metrics)

            return metrics

        except Exception as e:
            print(f"Error checking health: {e}")
            return {"error": str(e)}

    def _calculate_metrics(self, runs: List[Run]) -> Dict[str, Any]:
        """
        Calculate health metrics from runs.

        Args:
            runs: List of runs

        Returns:
            Metrics dictionary
        """
        total_runs = len(runs)
        failed_runs = sum(1 for r in runs if r.error)
        successful_runs = total_runs - failed_runs

        # Calculate latency
        valid_latencies = [
            (r.end_time - r.start_time).total_seconds()
            for r in runs
            if r.end_time and r.start_time
        ]
        avg_latency = sum(valid_latencies) / len(valid_latencies) if valid_latencies else 0
        max_latency = max(valid_latencies) if valid_latencies else 0
        p99_latency = sorted(valid_latencies)[int(len(valid_latencies) * 0.99)] if len(valid_latencies) > 1 else 0

        # Calculate cost
        total_cost = self._calculate_total_cost(runs)
        avg_cost = total_cost / total_runs if total_runs > 0 else 0

        # Calculate success rate
        success_rate = successful_runs / total_runs if total_runs > 0 else 0
        failed_rate = 1 - success_rate

        return {
            "timestamp": datetime.now().isoformat(),
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": success_rate,
            "failed_rate": failed_rate,
            "avg_latency": avg_latency,
            "max_latency": max_latency,
            "p99_latency": p99_latency,
            "total_cost": total_cost,
            "avg_cost": avg_cost,
        }

    def _print_health_report(self, metrics: Dict[str, Any]):
        """
        Print formatted health report.

        Args:
            metrics: Metrics dictionary
        """
        print(f"\n[{metrics['timestamp']}] Agent Health Report")
        print(f"  Total runs: {metrics['total_runs']}")
        print(f"  Successful: {metrics['successful_runs']}")
        print(f"  Failed: {metrics['failed_runs']} ({metrics['failed_rate']:.1%})")
        print(f"  Success rate: {metrics['success_rate']:.1%}")
        print(f"  Avg latency: {metrics['avg_latency']:.2f}s")
        print(f"  Max latency: {metrics['max_latency']:.2f}s")
        print(f"  P99 latency: {metrics['p99_latency']:.2f}s")
        print(f"  Total cost (period): ${metrics['total_cost']:.2f}")
        print(f"  Avg cost per run: ${metrics['avg_cost']:.4f}")

    def _check_alerts(self, metrics: Dict[str, Any]):
        """
        Check for alert conditions and trigger alerts.

        Args:
            metrics: Metrics dictionary
        """
        alerts = []

        # Failure rate alert
        if metrics["failed_rate"] > FAILURE_RATE_THRESHOLD:
            msg = f"High failure rate: {metrics['failed_rate']:.1%}"
            alerts.append(msg)
            print(f"  ⚠️  ALERT: {msg}")
            self._alert_slack(msg)

        # Latency alert
        if metrics["avg_latency"] > LATENCY_THRESHOLD:
            msg = f"High latency: {metrics['avg_latency']:.2f}s"
            alerts.append(msg)
            print(f"  ⚠️  ALERT: {msg}")
            self._alert_slack(msg)

        # Cost alert
        if metrics["total_cost"] > COST_ALERT_THRESHOLD:
            msg = f"High cost (period): ${metrics['total_cost']:.2f}"
            alerts.append(msg)
            print(f"  ⚠️  ALERT: {msg}")
            self._alert_slack(msg)

        return alerts

    def _calculate_total_cost(self, runs: List[Run]) -> float:
        """
        Sum up costs from all runs.

        Args:
            runs: List of runs

        Returns:
            Total cost
        """
        return sum(
            run.outputs.get("cost", 0)
            for run in runs
            if run.outputs and "cost" in run.outputs
        )

    def _alert_slack(self, message: str):
        """
        Send alert to Slack.

        Args:
            message: Alert message
        """
        # Implement your Slack integration here
        # This is a placeholder
        print(f"  📢 Slack: {message}")

    def analyze_failing_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Analyze recent failing runs.

        Args:
            limit: Maximum number of runs to analyze

        Returns:
            List of failing run details
        """
        try:
            failed_runs = list(
                self.client.list_runs(
                    project_name=self.project_name,
                    filter="error != null",
                    limit=limit,
                )
            )

            results = []
            for run in failed_runs:
                results.append(
                    {
                        "run_id": str(run.id),
                        "error": run.error,
                        "created_at": run.create_time.isoformat() if run.create_time else None,
                        "tags": run.tags or [],
                    }
                )

                # Tag for review
                current_tags = set(run.tags or [])
                current_tags.update(["needs_review", "engine_analysis"])
                self.client.update_run(run.id, tags=list(current_tags))

            return results

        except Exception as e:
            print(f"Error analyzing failing runs: {e}")
            return []

    def get_version_comparison(self, version1: str, version2: str) -> Dict[str, Any]:
        """
        Compare metrics between two agent versions.

        Args:
            version1: First version tag
            version2: Second version tag

        Returns:
            Comparison results
        """
        try:
            runs_v1 = list(
                self.client.list_runs(
                    project_name=self.project_name,
                    filter=f'tags CONTAINS "{version1}"',
                )
            )

            runs_v2 = list(
                self.client.list_runs(
                    project_name=self.project_name,
                    filter=f'tags CONTAINS "{version2}"',
                )
            )

            metrics_v1 = self._calculate_metrics(runs_v1) if runs_v1 else {}
            metrics_v2 = self._calculate_metrics(runs_v2) if runs_v2 else {}

            return {
                "version1": version1,
                "version2": version2,
                "metrics_v1": metrics_v1,
                "metrics_v2": metrics_v2,
                "improvement": self._calculate_improvement(metrics_v1, metrics_v2),
            }

        except Exception as e:
            print(f"Error comparing versions: {e}")
            return {"error": str(e)}

    def _calculate_improvement(self, old: Dict, new: Dict) -> Dict[str, float]:
        """
        Calculate improvement between versions.

        Args:
            old: Old metrics
            new: New metrics

        Returns:
            Improvement percentages
        """
        if not old or not new:
            return {}

        improvements = {}

        if old.get("success_rate") and new.get("success_rate"):
            improvements["success_rate"] = (
                (new["success_rate"] - old["success_rate"]) / old["success_rate"] * 100
            )

        if old.get("avg_latency") and new.get("avg_latency"):
            improvements["latency"] = (
                (old["avg_latency"] - new["avg_latency"]) / old["avg_latency"] * 100
            )

        if old.get("avg_cost") and new.get("avg_cost"):
            improvements["cost"] = (
                (old["avg_cost"] - new["avg_cost"]) / old["avg_cost"] * 100
            )

        return improvements


def monitor_agent_health(
    project_name: str = LANGSMITH_PROJECT,
    check_interval: int = MONITORING_INTERVAL,
):
    """
    Start monitoring agent health.

    Args:
        project_name: LangSmith project name
        check_interval: Check interval in seconds
    """
    monitor = AgentMonitor(project_name, check_interval)
    monitor.start()
