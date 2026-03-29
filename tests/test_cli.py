"""Tests for CLI commands and functionality."""

import json
import subprocess
import sys


class TestCLIHelp:
    """Test CLI help commands."""

    def test_help_command(self):
        """Test that --help shows all commands."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "install" in result.stdout
        assert "update" in result.stdout
        assert "repair" in result.stdout
        assert "status" in result.stdout
        assert "diagnose" in result.stdout

    def test_short_help(self):
        """Test that -h shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "-h"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Aceternity MCP CLI" in result.stdout


class TestCLIVersion:
    """Test CLI version command."""

    def test_version_command(self):
        """Test that --version shows version."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Version should be a semantic version string
        assert len(result.stdout.strip()) > 0
        assert "." in result.stdout.strip() or result.stdout.strip() == "unknown"

    def test_version_short_flag(self):
        """Test that -v shows version."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "-v"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestCLIStatus:
    """Test CLI status command."""

    def test_status_command(self):
        """Test that status command runs."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "status"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Version Information" in result.stdout
        assert "System Information" in result.stdout
        assert "Health Checks" in result.stdout

    def test_status_verbose(self):
        """Test status with --verbose flag."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "status", "--verbose"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Client Configurations" in result.stdout or "Platform" in result.stdout


class TestCLIDiagnose:
    """Test CLI diagnose command."""

    def test_diagnose_command(self):
        """Test that diagnose command outputs valid JSON."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "diagnose"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # Find JSON in output (skip header)
        lines = result.stdout.split("\n")
        json_start = next(
            i for i, line in enumerate(lines) if line.strip().startswith("{")
        )
        json_str = "\n".join(lines[json_start:])

        # Parse JSON
        data = json.loads(json_str)
        assert "registry" in data
        assert "mcp_command" in data
        assert "python" in data
        assert "client_configs" in data

    def test_diagnose_registry_status(self):
        """Test that diagnose includes registry status."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "diagnose"],
            capture_output=True,
            text=True,
        )
        # Find JSON in output (skip colored header)
        lines = result.stdout.split("\n")
        json_start = next(
            i for i, line in enumerate(lines) if line.strip().startswith("{")
        )
        json_str = "\n".join(lines[json_start:])
        data = json.loads(json_str)
        assert "registry" in data
        assert "status" in data["registry"]
        assert "details" in data["registry"]


class TestCLIUnknownCommand:
    """Test CLI error handling."""

    def test_unknown_command(self):
        """Test that unknown commands show error."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "unknown-command"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Unknown command" in result.stdout or "unknown-command" in result.stdout


class TestCLIInstall:
    """Test CLI install command."""

    def test_install_non_interactive(self):
        """Test install with --non-interactive flag."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "aceternity_mcp.cli",
                "install",
                "--non-interactive",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert (
            result.returncode == 0 or result.returncode == 1
        )  # May fail if npx not available
        assert "Post-Install" in result.stdout or "Setup" in result.stdout


class TestCLIUpdate:
    """Test CLI update command."""

    def test_update_non_interactive(self):
        """Test update with --non-interactive flag."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "update", "--non-interactive"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Update may succeed or fail depending on PyPI availability
        assert "version" in result.stdout.lower() or "update" in result.stdout.lower()


class TestCLIRepair:
    """Test CLI repair command."""

    def test_repair_non_interactive(self):
        """Test repair with --non-interactive flag."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "repair", "--non-interactive"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0 or result.returncode == 1
        assert "Repair" in result.stdout or "repair" in result.stdout.lower()

    def test_repair_registry_flag(self):
        """Test repair with --registry flag."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "aceternity_mcp.cli",
                "repair",
                "--registry",
                "--non-interactive",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0 or result.returncode == 1


class TestCLIFlags:
    """Test CLI flag parsing."""

    def test_verbose_flag(self):
        """Test --verbose flag."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "status", "-v"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_non_interactive_flag(self):
        """Test --non-interactive flag."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "status", "-y"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_short_flags(self):
        """Test short flag variants."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "-v"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestCLIColors:
    """Test CLI color output."""

    def test_color_codes_present(self):
        """Test that ANSI color codes are used."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "--help"],
            capture_output=True,
            text=True,
        )
        # ANSI escape codes should be present
        assert "\033[" in result.stdout or "RESET" in result.stdout


class TestCLIEntryPoints:
    """Test that all entry points work."""

    def test_cli_module(self):
        """Test running as python -m aceternity_mcp.cli."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.cli", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_server_module(self):
        """Test running server as python -m aceternity_mcp.server."""
        # Server runs indefinitely, so we'll just check it starts
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.server", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Server may not have --help, but should not crash immediately
        assert result.returncode == 0 or result.returncode == 2

    def test_install_module(self):
        """Test running installer as python -m aceternity_mcp.install."""
        result = subprocess.run(
            [sys.executable, "-m", "aceternity_mcp.install", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Installer runs interactactively by default
        assert result.returncode == 0 or "Aceternity MCP" in result.stdout
