#!/usr/bin/env python3
"""
Development utilities for TungShing project.

This script provides convenient commands for common development tasks.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def run_tests():
    """Run the test suite with verbose output."""
    print("🧪 Running tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "-v", "--tb=short", "tests/"
    ], cwd=PROJECT_ROOT)
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    return result.returncode


def lint():
    """Run linting tools (ruff check and format)."""
    print("🔍 Running linting...")
    
    # Check code style
    print("  📋 Checking code style...")
    check_result = subprocess.run([
        sys.executable, "-m", "ruff", "check", "src", "tests"
    ], cwd=PROJECT_ROOT)
    
    # Check formatting
    print("  🎨 Checking formatting...")
    format_result = subprocess.run([
        sys.executable, "-m", "ruff", "format", "--check", "src", "tests"
    ], cwd=PROJECT_ROOT)
    
    if check_result.returncode == 0 and format_result.returncode == 0:
        print("✅ Linting passed!")
        return 0
    else:
        print("❌ Linting issues found!")
        return 1


def type_check():
    """Run type checking with mypy."""
    print("🔍 Running type checking...")
    result = subprocess.run([
        sys.executable, "-m", "mypy", "src", "--ignore-missing-imports"
    ], cwd=PROJECT_ROOT)
    if result.returncode == 0:
        print("✅ Type checking passed!")
    else:
        print("❌ Type checking issues found!")
    return result.returncode


def format_code():
    """Format code using ruff."""
    print("🎨 Formatting code...")
    
    # Format code
    format_result = subprocess.run([
        sys.executable, "-m", "ruff", "format", "src", "tests"
    ], cwd=PROJECT_ROOT)
    
    # Fix linting issues
    fix_result = subprocess.run([
        sys.executable, "-m", "ruff", "check", "--fix", "src", "tests"
    ], cwd=PROJECT_ROOT)
    
    if format_result.returncode == 0 and fix_result.returncode == 0:
        print("✅ Code formatting completed!")
        return 0
    else:
        print("❌ Formatting issues encountered!")
        return 1


def build():
    """Build the package."""
    print("📦 Building package...")
    result = subprocess.run([
        sys.executable, "-m", "build"
    ], cwd=PROJECT_ROOT)
    if result.returncode == 0:
        print("✅ Package built successfully!")
        print("📁 Output in dist/ directory")
        
        # Validate the built package
        print("🔍 Validating package...")
        validate_result = subprocess.run([
            sys.executable, "-m", "twine", "check", "dist/*"
        ], cwd=PROJECT_ROOT)
        if validate_result.returncode == 0:
            print("✅ Package validation passed!")
        else:
            print("⚠️ Package validation issues found!")
    else:
        print("❌ Build failed!")
    return result.returncode


def check():
    """Run all checks (lint, type, test)."""
    print("🔍 Running all checks...")
    
    issues = 0
    
    if lint() != 0:
        issues += 1
        
    if type_check() != 0:
        issues += 1
        
    if run_tests() != 0:
        issues += 1
    
    if issues == 0:
        print("\n🎉 All checks passed! Ready for release.")
        return 0
    else:
        print(f"\n❌ {issues} check(s) failed. Please fix issues before release.")
        return 1


def install_dev():
    """Install development dependencies."""
    print("📥 Installing development dependencies...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "-e", ".[dev]"
    ], cwd=PROJECT_ROOT)
    if result.returncode == 0:
        print("✅ Development dependencies installed!")
    else:
        print("❌ Failed to install development dependencies!")
    return result.returncode


def clean():
    """Clean build artifacts and cache."""
    print("🧹 Cleaning build artifacts...")
    
    import shutil
    
    patterns_to_remove = [
        "build/",
        "dist/", 
        "*.egg-info/",
        "src/**/__pycache__/",
        "tests/**/__pycache__/",
        "__pycache__/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".ruff_cache/"
    ]
    
    removed_count = 0
    for pattern in patterns_to_remove:
        for path in PROJECT_ROOT.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                removed_count += 1
                print(f"  🗑️ Removed {path}")
            elif path.is_file():
                path.unlink()
                removed_count += 1
                print(f"  🗑️ Removed {path}")
    
    print(f"✅ Cleaned {removed_count} items!")
    return 0


def show_version():
    """Show current package version."""
    try:
        version_file = PROJECT_ROOT / "src" / "tungshing" / "_version.py"
        version_code = version_file.read_text()
        local_vars = {}
        exec(version_code, {}, local_vars)
        version = local_vars.get('__version__', 'unknown')
        print(f"📦 TungShing version: {version}")
        return 0
    except Exception as e:
        print(f"❌ Error reading version: {e}")
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Development utilities for TungShing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dev.py check          # Run all checks
  python dev.py format         # Format code
  python dev.py test           # Run tests
  python dev.py build          # Build package
  python dev.py clean          # Clean artifacts
        """
    )
    parser.add_argument(
        "command", 
        choices=["test", "lint", "type", "format", "build", "check", "install-dev", "clean", "version"],
        help="Command to run"
    )
    
    args = parser.parse_args()
    
    commands = {
        "test": run_tests,
        "lint": lint,
        "type": type_check,
        "format": format_code,
        "build": build,
        "check": check,
        "install-dev": install_dev,
        "clean": clean,
        "version": show_version,
    }
    
    try:
        exit_code = commands[args.command]()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)