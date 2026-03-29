"""Tests for installer functionality."""

from pathlib import Path

import pytest

from aceternity_mcp.install import (
    SUPPORTED_CLIENTS,
    Colors,
    check_prerequisites,
    expand_path,
    find_config_file,
)


class TestColors:
    """Test ANSI color codes."""

    def test_color_codes_exist(self):
        """Test that color codes are defined."""
        assert hasattr(Colors, "RESET")
        assert hasattr(Colors, "BOLD")
        assert hasattr(Colors, "GREEN")
        assert hasattr(Colors, "RED")
        assert hasattr(Colors, "YELLOW")
        assert hasattr(Colors, "BLUE")

    def test_color_codes_are_strings(self):
        """Test that color codes are strings."""
        assert isinstance(Colors.RESET, str)
        assert isinstance(Colors.BOLD, str)
        assert isinstance(Colors.GREEN, str)


class TestExpandPath:
    """Test path expansion."""

    def test_expand_home_directory(self):
        """Test expanding ~ to home directory."""
        result = expand_path("~/test")
        assert result is not None
        assert str(Path.home()) in str(result)

    def test_expand_absolute_path(self):
        """Test expanding absolute path."""
        result = expand_path("/tmp/test")
        assert result is not None
        # Path may be resolved to /private/tmp on macOS
        assert "tmp/test" in str(result)

    def test_expand_none_path(self):
        """Test expanding invalid path."""
        # This should handle gracefully
        result = expand_path("")
        assert result is not None


class TestFindConfigFile:
    """Test config file finding."""

    def test_find_config_file_with_valid_paths(self):
        """Test finding config file from list."""
        # Test with existing file - just verify it returns something
        result = find_config_file(["~/.bashrc", "~/.profile"])
        # May or may not find these files, that's OK
        assert result is None or isinstance(result, Path)

    def test_find_config_file_empty_list(self):
        """Test with empty list."""
        result = find_config_file([])
        assert result is None


class TestCheckPrerequisites:
    """Test prerequisite checking."""

    def test_check_prerequisites_returns_dict(self):
        """Test that check_prerequisites returns a dict."""
        result = check_prerequisites()
        assert isinstance(result, dict)

    def test_check_prerequisites_has_python(self):
        """Test that python check is present."""
        result = check_prerequisites()
        assert "python" in result

    def test_check_prerequisites_has_npx(self):
        """Test that npx check is present."""
        result = check_prerequisites()
        assert "npx" in result


class TestSupportedClients:
    """Test supported client configuration."""

    def test_supported_clients_is_dict(self):
        """Test that SUPPORTED_CLIENTS is a dict."""
        assert isinstance(SUPPORTED_CLIENTS, dict)

    def test_supported_clients_has_required_keys(self):
        """Test that clients have required keys."""
        required_clients = [
            "cursor",
            "claude-code",
            "cline",
            "windsurf",
            "opencode",
        ]
        for client in required_clients:
            assert client in SUPPORTED_CLIENTS

    def test_client_has_required_fields(self):
        """Test that each client has required fields."""
        for client_name, client_info in SUPPORTED_CLIENTS.items():
            assert "name" in client_info
            assert "mcp_json_path" in client_info or "config_paths" in client_info
            assert "config_key" in client_info
            assert "description" in client_info

    def test_client_config_paths_is_list(self):
        """Test that config paths are properly structured."""
        for client_info in SUPPORTED_CLIENTS.values():
            # Either mcp_json_path (string) or config_paths (list) should exist
            has_mcp_path = "mcp_json_path" in client_info
            has_config_paths = "config_paths" in client_info
            assert has_mcp_path or has_config_paths

            if has_config_paths:
                assert isinstance(client_info["config_paths"], list)
                assert len(client_info["config_paths"]) > 0

    def test_client_name_is_string(self):
        """Test that client name is a string."""
        for client_info in SUPPORTED_CLIENTS.values():
            assert isinstance(client_info["name"], str)
            assert len(client_info["name"]) > 0


class TestInstallerFunctions:
    """Test installer helper functions."""

    def test_import_install_functions(self):
        """Test that install functions can be imported."""
        from aceternity_mcp.install import print_header, print_section, print_success

        # Just testing imports work
        assert callable(print_header)
        assert callable(print_section)
        assert callable(print_success)


class TestRunCommand:
    """Test run_command function."""

    @pytest.fixture
    def run_command_func(self):
        """Import run_command for testing."""
        from aceternity_mcp.install import run_command

        return run_command

    def test_run_command_success(self, run_command_func):
        """Test running a successful command."""
        success, output = run_command_func(["echo", "test"])
        assert success is True
        assert "test" in output

    def test_run_command_failure(self, run_command_func):
        """Test running a failing command."""
        success, output = run_command_func(["nonexistent-command-12345"])
        assert success is False

    def test_run_command_with_cwd(self, run_command_func):
        """Test running command with cwd."""
        success, output = run_command_func(["pwd"], cwd=Path.home())
        assert success is True
        assert str(Path.home()) in output


class TestInstallerIntegration:
    """Integration tests for installer."""

    def test_all_clients_configurable(self):
        """Test that all clients can be configured."""
        # Just verify the structure is correct
        for client_name, client_info in SUPPORTED_CLIENTS.items():
            # Check for either mcp_json_path or config_paths
            has_mcp_path = "mcp_json_path" in client_info
            has_config_paths = "config_paths" in client_info
            assert has_mcp_path or has_config_paths

            if has_config_paths:
                assert isinstance(client_info["config_paths"], list)

            assert isinstance(client_info["config_key"], str)
            assert len(client_info["config_key"]) > 0

    def test_client_descriptions_unique(self):
        """Test that client descriptions are unique."""
        descriptions = [info["description"] for info in SUPPORTED_CLIENTS.values()]
        assert len(descriptions) == len(set(descriptions))
