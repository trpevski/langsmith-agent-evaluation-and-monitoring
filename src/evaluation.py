"""Evaluation metrics and dataset management for agent."""

from langsmith import evaluate
from langsmith.schemas import Example, Run
from typing import List, Dict, Any, Callable
from .config import COST_PER_1K_INPUT, COST_PER_1K_OUTPUT


def evaluate_cost_efficiency(run: Run, example: Example) -> Dict[str, Any]:
    """
    Check if the agent solved the task without excessive steps.

    Args:
        run: LangSmith run object
        example: Example from evaluation dataset

    Returns:
        Evaluation result dictionary
    """
    cost = run.outputs.get("cost", 0) if run.outputs else 0
    steps = run.outputs.get("steps", 0) if run.outputs else 0

    # Cost efficiency: should solve in 2-4 steps, cost < $0.01
    is_efficient = steps <= 4 and cost < 0.01

    return {
        "key": "cost_efficiency",
        "score": 1.0 if is_efficient else 0.0,
        "comment": f"Used {steps} steps, cost ${cost:.4f}",
    }


def evaluate_accuracy(run: Run, example: Example) -> Dict[str, Any]:
    """
    Check if output matches expected result.

    Args:
        run: LangSmith run object
        example: Example from evaluation dataset

    Returns:
        Evaluation result dictionary
    """
    if not run.outputs:
        return {
            "key": "accuracy",
            "score": 0.0,
            "comment": "No output from run",
        }

    output = str(run.outputs.get("response", ""))
    expected = example.outputs.get("expected_output", "") if example.outputs else ""

    # Simple substring match (in production, use semantic similarity)
    accuracy = 1.0 if expected.lower() in output.lower() else 0.0

    return {
        "key": "accuracy",
        "score": accuracy,
        "comment": f"Output relevance: {'matched' if accuracy else 'missed'}",
    }


def evaluate_latency(run: Run, example: Example) -> Dict[str, Any]:
    """
    Evaluate response latency.

    Args:
        run: LangSmith run object
        example: Example from evaluation dataset

    Returns:
        Evaluation result dictionary
    """
    if not run.end_time or not run.start_time:
        return {"key": "latency", "score": 0.5, "comment": "Unable to calculate latency"}

    latency = (run.end_time - run.start_time).total_seconds()
    # Prefer responses under 5 seconds
    score = 1.0 if latency < 5 else 0.5 if latency < 10 else 0.0

    return {
        "key": "latency",
        "score": score,
        "comment": f"Response time: {latency:.2f}s",
    }


def create_evaluation_dataset() -> List[Dict[str, Any]]:
    """
    Create evaluation dataset for testing.

    Returns:
        List of example inputs and expected outputs
    """
    return [
        {
            "input": "What's our top customer's usage?",
            "expected_output": "Pro customer with 450 units used",
            "category": "data_retrieval",
        },
        {
            "input": "Summarize our Q3 performance",
            "expected_output": "Summary should mention revenue and key metrics",
            "category": "summary",
        },
        {
            "input": "Create a plan for scaling to 10x users",
            "expected_output": "Should consider infrastructure, costs, and strategy",
            "category": "planning",
        },
        {
            "input": "What features are available in our platform?",
            "expected_output": "Should list analytics, monitoring, alerts",
            "category": "feature_list",
        },
        {
            "input": "Get current usage metrics",
            "expected_output": "Should return API calls, tokens, cost",
            "category": "metrics",
        },
    ]


def run_evaluation_suite(
    agent_fn: Callable,
    dataset: List[Dict[str, Any]],
    evaluators: List[Callable],
    experiment_prefix: str = "agent_eval",
) -> Dict[str, Any]:
    """
    Run evaluation suite against agent.

    Args:
        agent_fn: Function that runs the agent
        dataset: List of evaluation examples
        evaluators: List of evaluator functions
        experiment_prefix: Prefix for experiment name in LangSmith

    Returns:
        Evaluation results
    """
    results = {}

    try:
        # Convert dataset format for LangSmith
        langsmith_examples = [
            Example(
                inputs={"query": item["input"]},
                outputs={"expected_output": item["expected_output"]},
                metadata={"category": item.get("category", "general")},
            )
            for item in dataset
        ]

        # Run evaluation
        eval_results = evaluate(
            agent_fn,
            data=langsmith_examples,
            evaluators=evaluators,
            experiment_prefix=experiment_prefix,
        )

        results = eval_results

    except Exception as e:
        print(f"Error running evaluation: {e}")
        results = {"error": str(e)}

    return results


def calculate_total_cost(runs: List[Run]) -> float:
    """
    Sum up costs from all runs.

    Args:
        runs: List of LangSmith run objects

    Returns:
        Total cost estimate
    """
    return sum(
        run.outputs.get("cost", 0)
        for run in runs
        if run.outputs and "cost" in run.outputs
    )


def get_evaluators() -> List[Callable]:
    """
    Get list of all evaluator functions.

    Returns:
        List of evaluator functions
    """
    return [evaluate_cost_efficiency, evaluate_accuracy, evaluate_latency]
