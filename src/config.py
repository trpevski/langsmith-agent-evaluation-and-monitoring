"""Configuration management for the agent framework."""

import os
from dotenv import load_dotenv

load_dotenv()

# LangSmith Configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "default-project")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# Agent Configuration
MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", "10"))
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.7"))

# Monitoring Configuration
MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", "300"))  # 5 minutes
FAILURE_RATE_THRESHOLD = float(os.getenv("FAILURE_RATE_THRESHOLD", "0.05"))  # 5%
LATENCY_THRESHOLD = float(os.getenv("LATENCY_THRESHOLD", "10.0"))  # 10 seconds

# Cost Configuration
COST_PER_1K_INPUT = float(os.getenv("COST_PER_1K_INPUT", "0.03"))
COST_PER_1K_OUTPUT = float(os.getenv("COST_PER_1K_OUTPUT", "0.06"))
COST_ALERT_THRESHOLD = float(os.getenv("COST_ALERT_THRESHOLD", "1.0"))  # Alert if $1+

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
