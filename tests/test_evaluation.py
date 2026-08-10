"""Test evaluation module."""

import pytest
from src.evaluation import (
    create_evaluation_dataset,
    evaluate_cost_efficiency,
    evaluate_accuracy,
    evaluate_latency,
    get_evaluators,
)


def test_create_evaluation_dataset():
    """Test evaluation dataset creation."""
    dataset = create_evaluation_dataset()
    assert len(dataset) > 0
    assert all("input" in item for item in dataset)
    assert all("expected_output" in item for item in dataset)


def test_get_evaluators():
    """Test that evaluators are available."""
    evaluators = get_evaluators()
    assert len(evaluators) > 0
    assert all(callable(e) for e in evaluators)


def test_evaluator_signatures():
    """Test that evaluators have correct signature."""
    from src.evaluation import evaluate_cost_efficiency, evaluate_accuracy

    # These should be callable
    assert callable(evaluate_cost_efficiency)
    assert callable(evaluate_accuracy)
