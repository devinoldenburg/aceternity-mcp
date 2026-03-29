#!/usr/bin/env python3
"""Universal installer for Aceternity MCP Server.

This is a universal, cross-platform Python installer that:
1. Configures all supported AI tools (Cursor, Claude Code, Cline, Windsurf, OpenCode)
2. Verifies the installation

Run via: aceternity-mcp-install
Or: python -m aceternity_mcp.install
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


# ============================================================================
# ANSI Color Codes for Terminal Output
# ============================================================================
class Colors:
    """ANSI escape codes for colored terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    RED = "\033[31m"
    WHITE = "\033[37m"


# ============================================================================
# Supported AI Tools Configuration - CORRECT PATHS
# ============================================================================
SUPPORTED_CLIENTS = {
    "cursor": {
        "name": "Cursor",
        "config_paths": [
            "~/.cursor/mcp.json",
        ],
        "config_key": "mcpServers",
        "description": "Cursor IDE - AI-first code editor",
        "platform": "all",
    },
    "claude-code": {
        "name": "Claude Code CLI",
        "config_paths": [
            "~/.claude/mcp.json",
        ],
        "config_key": "mcpServers",
        "description": "Claude Code Command Line Interface",
        "platform": "all",
    },
    "cline": {
        "name": "Cline",
        "config_paths": [
            "~/.vscode/extensions/saoudrizwan.claude-dev-*/settings/cline_mcp_settings.json",
            "~/.vscode-server/extensions/saoudrizwan.claude-dev-*/settings/cline_mcp_settings.json",
        ],
        "config_key": "mcpServers",
        "description": "Cline VS Code Extension",
        "platform": "all",
    },
    "windsurf": {
        "name": "Windsurf",
        "config_paths": [
            "~/.codeium/windsurf/mcp_config.json",
        ],
        "config_key": "mcp_servers",
        "description": "Windsurf IDE by Codeium",
        "platform": "all",
    },
    "opencode": {
        "name": "OpenCode",
        "config_paths": [
            "~/.opencode/mcp.json",
            "~/.config/opencode/mcp.json",
        ],
        "config_key": "mcpServers",
        "description": "OpenCode AI Assistant",
        "platform": "all",
    },
}


# ============================================================================
# Helper Functions
# ============================================================================
def print_header(title: str, subtitle: str = "") -> None:
    """Print a formatted header with colors."""
    width = 70
    print(f"\n{Colors.CYAN}{'=' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title.center(width)}{Colors.RESET}")
    if subtitle:
        print(f"{Colors.DIM}{subtitle.center(width)}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * width}{Colors.RESET}\n")


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}► {title}{Colors.RESET}")
    print(f"{Colors.DIM}{'─' * 50}{Colors.RESET}")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"{Colors.CYAN}→ {message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def get_platform() -> str:
    """Get the current platform."""
    if sys.platform.startswith("win"):
        return "windows"
    elif sys.platform.startswith("darwin"):
        return "macos"
    else:
        return "linux"


def expand_path(path: str) -> Path | None:
    """Expand ~ and environment variables in a path."""
    try:
        if os.name == "nt":
            path = os.path.expandvars(path)
        expanded = os.path.expanduser(path)
        return Path(expanded).resolve()
    except Exception:
        return None


def find_config_file(config_paths: list[str]) -> Path | None:
    """Find the first existing config file from a list of paths."""
    for path in config_paths:
        expanded = expand_path(path)
        if expanded and expanded.exists():
            return expanded
    
    # If none exist, return the first path for creation
    if config_paths:
        return expand_path(config_paths[0])
    return None


def run_command(
    command: list[str], cwd: Path | None = None, capture: bool = True
) -> tuple[bool, str]:
    """Run a shell command and return success status and output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=capture,
            text=True,
            check=False,
        )
        output = result.stdout + result.stderr if capture else ""
        return result.returncode == 0, output.strip()
    except FileNotFoundError as e:
        return False, f"Command not found: {e}"
    except Exception as e:
        return False, str(e)


def check_prerequisites() -> dict[str, bool]:
    """Check system prerequisites."""
    results = {}

    version = sys.version_info
    python_ok = version.major == 3 and version.minor >= 10
    results["python"] = python_ok
    if python_ok:
        print_success(f"Python {version.major}.{version.minor} found")
    else:
        print_error(f"Python 3.10+ required (found {version.major}.{version.minor})")

    success, _ = run_command(["npx", "--version"])
    results["npx"] = success
    if success:
        print_success("npx (Node.js) found")
    else:
        print_error("npx not found - Node.js required for registry sync")

    return results


# ============================================================================
# Installation Functions
# ============================================================================
def configure_client(
    client_name: str, mcp_command: str, mcp_args: list[str], cwd: str | None = None
) -> bool:
    """Configure a specific MCP client."""
    client = SUPPORTED_CLIENTS[client_name]
    config_path = find_config_file(client["config_paths"])
    config_key = client["config_key"]

    if not config_path:
        print_error(f"Cannot determine config path for {client['name']}")
        return False

    print_info(f"Configuring {client['name']}...")
    print_info(f"Config path: {config_path}")

    # Load existing config
    config = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print_warning(f"Could not parse existing config: {e}")
            config = {}

    # Ensure the config key exists
    if config_key not in config:
        config[config_key] = {}

    # Determine server name based on config key format
    if config_key == "mcp_servers":
        server_name = "aceternity_ui"
    else:
        server_name = "aceternity-ui"

    # Create server configuration (only include cwd if provided)
    server_config = {
        "command": mcp_command,
        "args": mcp_args,
    }
    if cwd:
        server_config["cwd"] = cwd

    # Add to config
    config[config_key][server_name] = server_config

    # Save config
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print_success(f"{client['name']} configured at {config_path}")
        return True
    except IOError as e:
        print_error(f"Failed to write config: {e}")
        return False


def configure_all_clients(mcp_command: str = "aceternity-mcp-server") -> dict[str, bool]:
    """Configure all supported MCP clients.
    
    Uses aceternity-mcp-server (the MCP server) by default, not the CLI.
    When installed via pipx, no cwd is needed as the command is on PATH.
    """
    results = {}

    print_section("Configuring AI Tools")
    print_info(f"Configuring MCP server: {mcp_command}")

    # No cwd needed when installed via pipx - command is on PATH
    for client_name in SUPPORTED_CLIENTS:
        results[client_name] = configure_client(
            client_name=client_name,
            mcp_command=mcp_command,
            mcp_args=[],
            cwd=None,
        )

    return results


def verify_installation() -> bool:
    """Verify the MCP server installation."""
    print_section("Verifying Installation")

    success, output = run_command(["aceternity-mcp", "--help"])
    cli_ok = success

    success, output = run_command(["aceternity-mcp-server", "--help"])
    server_ok = success

    if cli_ok and server_ok:
        print_success("MCP CLI and server are accessible")
        print_info("Server command: aceternity-mcp-server")
        return True
    else:
        if not cli_ok:
            print_error("MCP CLI not accessible")
        if not server_ok:
            print_error("MCP server not accessible")
        return False


# ============================================================================
# Main Entry Point
# ============================================================================
def main() -> int:
    """Main installation function."""
    print_header(
        "Aceternity MCP Server - Universal Installer",
        "Automated setup for all AI tools",
    )

    platform = get_platform()
    print_info(f"Platform: {platform}")
    print_info(
        f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )

    args = sys.argv[1:]
    non_interactive = "--non-interactive" in args or "-y" in args

    if not sys.stdin.isatty():
        non_interactive = True

    # Configure clients
    configure_all_clients()

    # Verify installation
    verified = verify_installation()

    # Print summary
    print("\n" + "=" * 60)
    print("Installation Summary")
    print("=" * 60)

    if verified:
        print_success("Installation verified successfully!")
    else:
        print_warning("Verification failed")

    print("\n⚠️  IMPORTANT: Restart your AI tools to load the MCP server!")
    print("\nRestart these tools now:")
    print("  • OpenCode - Quit and reopen")
    print("  • Cursor - Restart the application")
    print("  • Claude Code - Restart or run: claude")
    print("  • Cline - Reload VS Code window")
    print("  • Windsurf - Restart the application")

    print("\nAfter restarting, the MCP server will be available!")
    print()

    return 0 if verified else 1


if __name__ == "__main__":
    sys.exit(main())
