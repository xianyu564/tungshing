#!/usr/bin/env python3
"""Development utilities for TungShing project."""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    subprocess.run([sys.executable, "-m", "pytest", "-v"], cwd=PROJECT_ROOT, check=True)


def lint():
    """Run linting tools."""
    print("Running ruff...")
    subprocess.run([sys.executable, "-m", "ruff", "check", "src", "tests"], cwd=PROJECT_ROOT, check=True)
    subprocess.run([sys.executable, "-m", "ruff", "format", "--check", "src", "tests"], cwd=PROJECT_ROOT, check=True)


def type_check():
    """Run type checking."""
    print("Running mypy...")
    subprocess.run([sys.executable, "-m", "mypy", "src"], cwd=PROJECT_ROOT, check=True)


def build():
    """Build the package."""
    print("Building package...")
    subprocess.run([sys.executable, "-m", "build"], cwd=PROJECT_ROOT, check=True)


def check():
    """Run all checks."""
    lint()
    type_check()
    run_tests()


def install_dev():
    """Install development dependencies."""
    print("Installing development dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], cwd=PROJECT_ROOT)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Development utilities")
    parser.add_argument("command", choices=["test", "lint", "type", "build", "check", "install-dev"])
    
    args = parser.parse_args()
    
    commands = {
        "test": run_tests,
        "lint": lint,
        "type": type_check,
        "build": build,
        "check": check,
        "install-dev": install_dev,
    }
    
    commands[args.command]()