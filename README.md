# LangSmith Agent Evaluation and Monitoring

Production-grade implementation of LLM agent evaluation and continuous monitoring using LangSmith Studio.

Based on the blog post: [Using LangSmith Studio for Agent Evaluation and Monitoring: A Production Guide](https://test.trpevski.com)

## Overview

This project demonstrates:

- **Complete agent tracing** with LangSmith for full visibility into agent behavior
- **Custom evaluation metrics** to measure agent performance consistently
- **Production monitoring** with real-time alerts for cost, latency, and failure rates
- **Version comparison** to compare agent versions before deployment
- **Cost tracking** to understand exactly where your money goes

## Quick Start

### 1. Setup

```bash
# Clone/extract the project
cd langsmith-agent-eval

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your actual API keys
# LANGSMITH_API_KEY=your_key
# OPENAI_API_KEY=your_key
```

### 2. Run Basic Example

```bash
python examples/basic_agent.py
```

This creates a simple agent and runs it with tracing enabled. You'll see the run appear in LangSmith Studio immediately.

### 3. Run Evaluation

```bash
python examples/evaluation_example.py
```

This tests the agent against a pre-defined dataset and generates evaluation metrics.

### 4. Monitor Production

```bash
python examples/monitoring_example.py
```

This checks your production agent's health and triggers alerts if thresholds are exceeded.

## Project Structure

```
langsmith-agent-eval/
├── src/
│   ├── agent.py          # Main agent implementation
│   ├── evaluation.py      # Custom evaluators and dataset
│   ├── monitoring.py      # Production monitoring and alerts
│   ├── tools.py          # Tool definitions
│   └── config.py         # Configuration management
├── examples/
│   ├── basic_agent.py              # Getting started
│   ├── evaluation_example.py        # Running evaluations
│   └── monitoring_example.py        # Production monitoring
├── tests/
│   └── test_*.py         # Unit tests
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Features

### Agent Tracing

Every agent step is automatically traced with full context:
- Tool calls and responses
- LLM invocations and tokens used
- Cost tracking per step
- Execution time and latency

View in LangSmith Studio → Traces tab.

### Custom Evaluation

Built-in evaluators for:
- **Cost Efficiency** - Measure cost per successful completion
- **Accuracy** - Check if outputs match expected results
- **Latency** - Track response times

Add new evaluators by implementing the evaluator interface:

```python
def my_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    return {
        "key": "my_metric",
        "score": 0.95,
        "comment": "Your feedback"
    }
```

### Production Monitoring

Real-time monitoring checks:
- Success rates
- Average and P99 latency
- Total cost and cost per request
- Error tracking with details

Automatic alerts for:
- High failure rate (> 5%)
- High latency (> 10s avg)
- High costs (> $1/period)

Extend `AgentMonitor` class to add custom alerts.

### Version Management

Compare agent versions with tagging:

```python
# Tag runs with version
run.tags = ["version:v2", "canary"]

# Later, compare versions
monitor.get_version_comparison("version:v1", "version:v2")
```

## Configuration

All configuration in `src/config.py` can be overridden via environment variables:

```bash
# Agent settings
OPENAI_MODEL=gpt-4
AGENT_TEMPERATURE=0.7
MAX_AGENT_STEPS=15

# Monitoring thresholds
FAILURE_RATE_THRESHOLD=0.1  # 10%
LATENCY_THRESHOLD=15.0       # 15 seconds
COST_ALERT_THRESHOLD=2.0     # $2 per period

# Project configuration
LANGSMITH_PROJECT=production-agent
ENVIRONMENT=production
```

## Usage Examples

### Example 1: Run Agent Once

```python
from src.agent import create_agent, run_agent

agent = create_agent()
result = run_agent(agent, "What's our top customer's usage?", user_id="user_123")

print(f"Response: {result['response']}")
print(f"Cost: ${result['cost']:.4f}")
print(f"Steps: {result['steps']}")
```

### Example 2: Evaluate Multiple Versions

```python
from src.evaluation import create_evaluation_dataset, run_evaluation_suite

dataset = create_evaluation_dataset()

# Test v1
evaluators = get_evaluators()
results_v1 = run_evaluation_suite(agent_v1, dataset, evaluators, "v1")

# Test v2
results_v2 = run_evaluation_suite(agent_v2, dataset, evaluators, "v2")

# Compare in LangSmith UI under Experiments
```

### Example 3: Continuous Monitoring

```python
from src.monitoring import AgentMonitor

monitor = AgentMonitor(project_name="production", check_interval=300)

# One-time check
metrics = monitor.check_health()

# Continuous monitoring (runs in background)
monitor.start()

# Or in a separate process/container
if __name__ == "__main__":
    monitor_agent_health()
```

### Example 4: Cost Attribution

```python
from src.monitoring import AgentMonitor

monitor = AgentMonitor()
metrics = monitor.check_health()

print(f"Average cost per run: ${metrics['avg_cost']:.4f}")
print(f"Total cost (5min window): ${metrics['total_cost']:.2f}")

# Identify expensive failures
failing_runs = monitor.analyze_failing_runs()
for run in failing_runs:
    if run.outputs and "cost" in run.outputs:
        cost = run.outputs["cost"]
        if cost > 0.05:  # Over $0.05
            print(f"Expensive failure: {cost}")
```

## Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t langsmith-agent .

# Run monitoring container
docker-compose up -d monitoring

# View logs
docker-compose logs -f monitoring
```

## Testing

Run tests:

```bash
pytest tests/
```

## Production Checklist

Before deploying to production:

- [ ] Set `ENVIRONMENT=production` in .env
- [ ] Configure LANGSMITH_PROJECT to production project name
- [ ] Set appropriate monitoring thresholds
- [ ] Configure alert integration (Slack, PagerDuty, etc.)
- [ ] Test evaluation dataset with multiple agent versions
- [ ] Run monitoring for 1-2 hours to establish baseline
- [ ] Implement gradual rollout (10% → 50% → 100%)

## Monitoring Strategy

1. **Baseline (Day 1)**
   - Run agent in shadow mode (don't use results)
   - Collect 1000+ traces to establish baseline metrics
   - Identify evaluation dataset edge cases

2. **Canary (Day 2-3)**
   - Deploy new version to 10% of traffic
   - Compare metrics against v1 in real-time
   - Watch for regressions

3. **Gradual Rollout (Day 4-7)**
   - Increase to 50% if metrics look good
   - Continue monitoring
   - Be ready to rollback if issues arise

4. **Full Production (Day 8+)**
   - Move to 100% when confident
   - Continue daily monitoring
   - Weekly review of metrics trends

## Troubleshooting

### No runs appearing in LangSmith

- Check `LANGSMITH_API_KEY` is valid
- Check `LANGSMITH_PROJECT` matches your project name
- Ensure LangSmith is imported: `from langsmith import get_tracer`

### High failure rates in production

- Check recent code changes
- Review failing run details in LangSmith
- Check error messages in monitoring output
- Consider rolling back to previous version

### Unexpected cost increases

- Run cost attribution analysis
- Check which tools are most expensive
- Review tool usage in failing runs
- Consider caching frequent queries

## Performance Tips

1. **Batch requests** - Process multiple queries together when possible
2. **Cache tool results** - Many queries may need same data
3. **Use cheaper models** - Use GPT-3.5-turbo for simple tasks
4. **Limit agent steps** - Set MAX_AGENT_STEPS conservatively
5. **Monitor tokens** - Track token usage, not just cost

## Integration

### Slack Alerts

Modify `_alert_slack()` in `src/monitoring.py`:

```python
def _alert_slack(self, message: str):
    import requests
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    requests.post(webhook_url, json={"text": message})
```

### Datadog/New Relic

Add custom metrics to your monitoring provider using the metrics returned by `check_health()`.

## Contributing

This is a reference implementation. Feel free to extend:
- Add new evaluators
- Implement custom alert systems
- Add database logging
- Integrate with your infrastructure

## License

MIT

## Support

For questions or issues:
1. Check the blog post for detailed explanations
2. Review LangSmith documentation: https://docs.langchain.com/langsmith
3. Check LangChain docs: https://docs.langchain.com

## See Also

- Blog Post: [Using LangSmith Studio for Agent Evaluation and Monitoring](https://trpevski.com/blog/langsmith-studio-agent-evaluation-and-monitoring)
- LangSmith Docs: https://docs.langchain.com/langsmith
- LangChain Docs: https://docs.langchain.com
# LangSmith-Agent-Evaluation-and-Monitoring
