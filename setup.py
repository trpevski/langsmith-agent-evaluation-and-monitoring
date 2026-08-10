"""Setup script for langsmith-agent-eval package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="langsmith-agent-eval",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Production-grade agent evaluation and monitoring with LangSmith",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/langsmith-agent-eval",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=[
        "langsmith>=0.1.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.1",
        "langgraph>=0.0.1",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
)
