#!/usr/bin/env python3
"""
Test runner script for LLM service.
Provides convenient commands for running different types of tests.
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a shell command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description or cmd}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=False)
    return result.returncode == 0


def run_unit_tests():
    """Run unit tests only"""
    return run_command(
        "python -m pytest tests/unit/ -v",
        "Unit Tests"
    )


def run_integration_tests():
    """Run integration tests only"""
    return run_command(
        "python -m pytest tests/integration/ -v",
        "Integration Tests"
    )


def run_all_tests():
    """Run all tests"""
    return run_command(
        "python -m pytest tests/ -v",
        "All Tests"
    )


def run_tests_with_coverage():
    """Run tests with coverage report"""
    return run_command(
        "python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html",
        "Tests with Coverage"
    )


def run_specific_test(test_path):
    """Run a specific test file or function"""
    return run_command(
        f"python -m pytest {test_path} -v",
        f"Specific Test: {test_path}"
    )


def lint_code():
    """Run code linting (if available)"""
    try:
        return run_command(
            "python -m flake8 app/ tests/",
            "Code Linting"
        )
    except:
        print("Flake8 not available, skipping linting")
        return True


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="LLM Service Test Runner")
    parser.add_argument(
        "command",
        choices=["unit", "integration", "all", "coverage", "lint", "specific"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--test",
        help="Specific test file or function to run (for 'specific' command)"
    )
    
    args = parser.parse_args()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    import os
    os.chdir(project_dir)
    
    success = True
    
    if args.command == "unit":
        success = run_unit_tests()
    elif args.command == "integration":
        success = run_integration_tests()
    elif args.command == "all":
        success = run_all_tests()
    elif args.command == "coverage":
        success = run_tests_with_coverage()
    elif args.command == "lint":
        success = lint_code()
    elif args.command == "specific":
        if not args.test:
            print("Error: --test argument required for 'specific' command")
            sys.exit(1)
        success = run_specific_test(args.test)
    
    if success:
        print(f"\n✅ {args.command.title()} completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ {args.command.title()} failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()