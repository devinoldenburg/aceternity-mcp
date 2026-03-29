#!/usr/bin/env python3
"""Comprehensive test runner for Aceternity MCP.

Run all tests with various options and generate reports.

Usage:
    python scripts/run_tests.py              # Run all tests
    python scripts/run_tests.py --quick      # Run fast tests only
    python scripts/run_tests.py --coverage   # Run with coverage report
    python scripts/run_tests.py --verbose    # Run with verbose output
"""

import argparse
import subprocess
import sys
from pathlib import Path


def print_header(text: str) -> None:
    """Print a formatted header."""
    width = 70
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width + "\n")


def run_command(command: list[str], cwd: Path | None = None) -> int:
    """Run a command and return exit code."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            shell=False,
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"\nError running command: {e}")
        return 1


def check_prerequisites() -> bool:
    """Check if pytest is installed."""
    try:
        __import__("pytest")
        return True
    except ImportError:
        print("pytest not found. Installing...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"],
            check=False,
        )
        return result.returncode == 0


def run_all_tests(verbose: bool = False) -> int:
    """Run all tests."""
    print_header("Running All Tests")

    command = [sys.executable, "-m", "pytest"]
    if verbose:
        command.append("-vv")

    return run_command(command)


def run_quick_tests() -> int:
    """Run quick tests only (exclude slow tests)."""
    print_header("Running Quick Tests")

    command = [sys.executable, "-m", "pytest", "-m", "not slow", "-v"]

    return run_command(command)


def run_with_coverage() -> int:
    """Run tests with coverage report."""
    print_header("Running Tests with Coverage")

    command = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=src/aceternity_mcp",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v",
    ]

    return run_command(command)


def run_specific_test(test_path: str, verbose: bool = False) -> int:
    """Run a specific test or test file."""
    print_header(f"Running Test: {test_path}")

    command = [sys.executable, "-m", "pytest", test_path]
    if verbose:
        command.append("-vv")

    return run_command(command)


def run_cli_tests() -> int:
    """Run CLI-specific tests."""
    print_header("Running CLI Tests")

    command = [sys.executable, "-m", "pytest", "tests/test_cli.py", "-v"]

    return run_command(command)


def run_registry_tests() -> int:
    """Run registry-specific tests."""
    print_header("Running Registry Tests")

    command = [sys.executable, "-m", "pytest", "tests/test_registry.py", "-v"]

    return run_command(command)


def run_server_tests() -> int:
    """Run server-specific tests."""
    print_header("Running Server Tests")

    command = [sys.executable, "-m", "pytest", "tests/test_server.py", "-v"]

    return run_command(command)


def print_summary(results: dict[str, int]) -> None:
    """Print test run summary."""
    print_header("Test Run Summary")

    total = len(results)
    passed = sum(1 for code in results.values() if code == 0)
    failed = total - passed

    print(f"Total test suites: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()

    if results:
        print("Results by suite:")
        for name, code in results.items():
            status = "✓ PASS" if code == 0 else "✗ FAIL"
            print(f"  {status}: {name}")

    print()
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} test suite(s) failed")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Aceternity MCP tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py              # Run all tests
  python scripts/run_tests.py --quick      # Run fast tests only
  python scripts/run_tests.py --coverage   # Run with coverage
  python scripts/run_tests.py --cli        # Run CLI tests only
  python scripts/run_tests.py --verbose    # Verbose output
        """,
    )

    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Run quick tests only (exclude slow tests)",
    )

    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Run with coverage report"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    parser.add_argument("--cli", action="store_true", help="Run CLI tests only")

    parser.add_argument(
        "--registry", action="store_true", help="Run registry tests only"
    )

    parser.add_argument("--server", action="store_true", help="Run server tests only")

    parser.add_argument(
        "test_path", nargs="?", help="Specific test file or function to run"
    )

    args = parser.parse_args()

    # Check prerequisites
    if not check_prerequisites():
        print("Failed to install pytest. Please install manually:")
        print("  pip install pytest pytest-cov")
        return 1

    # Run tests based on options
    if args.test_path:
        return run_specific_test(args.test_path, args.verbose)
    if args.cli:
        return run_cli_tests()
    if args.registry:
        return run_registry_tests()
    if args.server:
        return run_server_tests()
    if args.quick:
        return run_quick_tests()
    if args.coverage:
        return run_with_coverage()
    return run_all_tests(args.verbose)


if __name__ == "__main__":
    sys.exit(main())
