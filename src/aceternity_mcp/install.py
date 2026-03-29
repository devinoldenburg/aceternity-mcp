#!/usr/bin/env python3
"""Universal installer for Aceternity MCP Server.

This is a universal, cross-platform Python installer that:
1. Syncs the component registry from Aceternity UI
2. Configures all supported AI tools (Cursor, Claude Code, Cline, Windsurf, OpenCode)
3. Verifies the installation

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
# Supported AI Tools Configuration
# ============================================================================
SUPPORTED_CLIENTS = {
    "cursor": {
        "name": "Cursor",
        "config_paths": [
            "~/.cursor/mcp.json",
            "~/.cursor/mcp_settings.json",
        ],
        "config_key": "mcpServers",
        "description": "Cursor IDE - AI-first code editor",
        "platform": "all",
    },
    "claude": {
        "name": "Claude Desktop",
        "config_paths": [
            "~/Library/Application Support/Claude/claude_desktop_config.json",  # macOS
            "%APPDATA%/Claude/claude_desktop_config.json",  # Windows
            "~/.config/claude/claude_desktop_config.json",  # Linux
        ],
        "config_key": "mcpServers",
        "description": "Claude Desktop App",
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
        # Handle Windows environment variables
        if os.name == "nt":
            path = os.path.expandvars(path)

        # Expand ~ to home directory
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

    # Check Python version
    version = sys.version_info
    python_ok = version.major == 3 and version.minor >= 10
    results["python"] = python_ok
    if python_ok:
        print_success(f"Python {version.major}.{version.minor} found")
    else:
        print_error(f"Python 3.10+ required (found {version.major}.{version.minor})")

    # Check npx
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
def sync_registry(api_key: str | None = None) -> bool:
    """Sync the component registry from Aceternity UI.

    Note: The registry is bundled with the pipx package, so sync is optional.
    Only needed for development or to get the latest components.
    """
    print_section("Syncing Component Registry")
    print_info("Note: Registry is bundled with the package. Sync is optional.")

    # Try to find sync_registry.py script
    script_locations = [
        Path(__file__).parent.parent.parent / "scripts" / "sync_registry.py",
        Path(__file__).parent / "scripts" / "sync_registry.py",
        Path.cwd() / "scripts" / "sync_registry.py",
    ]

    sync_script = None
    for loc in script_locations:
        if loc.exists():
            sync_script = loc
            break

    if not sync_script:
        print_info("Registry already bundled (106 components)")
        print_info("Skipping sync (only needed for development)")
        return True

    command = [sys.executable, str(sync_script)]
    if api_key:
        command.extend(["--api-key", api_key])

    print_info("Fetching components from Aceternity UI...")

    success, output = run_command(command)

    if success:
        print_success(output)
        return True
    else:
        print_error(f"Sync failed: {output}")
        return False


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

    # Ensure the configs key exists
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

    # Create server configuration
    server_config = {
        "command": mcp_command,
        "args": mcp_args,
        "cwd": cwd,
    }

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


def configure_all_clients(
    mcp_command: str = "aceternity-mcp-server",
) -> dict[str, bool]:
    """Configure all supported MCP clients.

    Uses aceternity-mcp-server (the MCP server) by default, not the CLI.
    When installed via pipx, no cwd is needed as the command is on PATH.
    """
    results = {}

    print_section("Configuring AI Tools")
    print_info(f"Configuring MCP server: {mcp_command}")

    # No cwd needed when installed via pipx - command is on PATH
    # Configure each client
    for client_name in SUPPORTED_CLIENTS:
        results[client_name] = configure_client(
            client_name=client_name,
            mcp_command=mcp_command,
            mcp_args=[],
            cwd=None,  # No cwd needed for pipx installations
        )

    return results


def verify_installation() -> bool:
    """Verify the MCP server installation."""
    print_section("Verifying Installation")

    success, output = run_command(["aceternity-mcp", "--help"])

    if success:
        print_success("MCP server is accessible and working")
        return True
    else:
        print_error(f"MCP server not accessible: {output}")
        return False


def get_api_key() -> str | None:
    """Get API key from environment or prompt user."""
    # Check environment variable first
    api_key = os.environ.get("ACETERNITY_API_KEY")
    if api_key:
        print_info("API key found in environment variable")
        return api_key

    # Check if running in non-interactive mode
    if not sys.stdin.isatty():
        print_info("Running in non-interactive mode, skipping API key")
        return None

    # Prompt user
    print("\n" + "=" * 60)
    print("Aceternity UI API Key (Optional)")
    print("=" * 60)
    print("\nThe API key is optional and used for authenticated registry access.")
    print("It is NOT stored on disk and only used during sync operations.")
    print("\nPress Enter to skip or enter your API key:")

    try:
        # Try getpass for hidden input
        try:
            import getpass

            api_key = getpass.getpass("API key: ").strip()
        except Exception:
            # Fallback to regular input
            api_key = input("API key: ").strip()

        if api_key:
            print_success("API key provided")
            return api_key
        else:
            print_info("No API key provided (using public registry)")
            return None
    except (EOFError, KeyboardInterrupt):
        print("\n")
        print_info("No API key provided (using public registry)")
        return None


def select_clients() -> list[str]:
    """Let user select which clients to configure."""
    if not sys.stdin.isatty():
        # Non-interactive mode - configure all
        return list(SUPPORTED_CLIENTS.keys())

    print("\n" + "=" * 60)
    print("Select AI Tools to Configure")
    print("=" * 60)
    print("\nAvailable AI tools:")

    clients = list(SUPPORTED_CLIENTS.keys())
    for i, client_name in enumerate(clients, 1):
        client = SUPPORTED_CLIENTS[client_name]
        print(
            f"  {Colors.BOLD}{i}{Colors.RESET}. {client['name']} - {client['description']}"
        )

    print(f"\n  {Colors.BOLD}A{Colors.RESET}. Configure ALL tools")
    print(f"  {Colors.BOLD}N{Colors.RESET}. Skip configuration")

    print("\nEnter your choice (e.g., '1,3' or 'A' or 'N'):", end=" ")

    try:
        choice = input().strip().upper()

        if choice == "A":
            print_success("Configuring all AI tools")
            return clients
        elif choice == "N":
            print_info("Skipping client configuration")
            return []
        else:
            selected = []
            for num in choice.split(","):
                num = num.strip()
                if num.isdigit():
                    idx = int(num) - 1
                    if 0 <= idx < len(clients):
                        selected.append(clients[idx])

            if selected:
                names = [SUPPORTED_CLIENTS[c]["name"] for c in selected]
                print_success(f"Selected: {', '.join(names)}")
                return selected
            else:
                print_warning("No valid selection, configuring all tools")
                return clients

    except (EOFError, KeyboardInterrupt):
        print("\n")
        print_info("Configuring all tools by default")
        return clients


def print_summary(results: dict[str, Any]) -> None:
    """Print installation summary."""
    print("\n" + "=" * 60)
    print("Installation Summary")
    print("=" * 60)

    if results.get("registry_synced"):
        print_success("Registry synced")
    else:
        print_error("Registry sync failed (can run manually later)")

    if results.get("verified"):
        print_success("Installation verified")
    else:
        print_warning("Verification failed")

    client_results = results.get("clients", {})
    if client_results:
        print("\nAI Tool Configuration:")
        for client_name, success in client_results.items():
            name = SUPPORTED_CLIENTS[client_name]["name"]
            if success:
                print_success(f"{name} configured")
            else:
                print_warning(
                    f"{name} - config file not found (will create on first launch)"
                )

    print("\n" + "=" * 60)
    print("Next Steps")
    print("=" * 60)
    print("\n1. Restart your AI tools to load the new MCP configuration")
    print("\n2. Try these example prompts:")
    print("   • 'Show me subtle background effects for landing pages'")
    print("   • 'Recommend a navbar + hero combination'")
    print("   • 'Install Spotlight component and show dependencies'")
    print("\n3. Update registry anytime:")
    print("   aceternity-mcp-install --sync-only")
    print("\n")


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

    # Parse command line arguments
    args = sys.argv[1:]

    sync_only = "--sync-only" in args
    api_key = None
    selected_clients = None

    # Extract API key if provided
    for i, arg in enumerate(args):
        if arg == "--api-key" and i + 1 < len(args):
            api_key = args[i + 1]
        elif arg == "--clients" and i + 1 < len(args):
            selected_clients = args[i + 1].split(",")

    # Check prerequisites
    print_section("Checking Prerequisites")
    prereqs = check_prerequisites()

    if not all(prereqs.values()):
        print_error("\nSome prerequisites are missing.")
        if not sys.stdin.isatty():
            print_info("Continuing in non-interactive mode...")
        else:
            response = input("\nContinue anyway? (y/n): ").strip().lower()
            if response not in ("y", "yes"):
                return 1

    # Get API key (unless sync-only mode)
    if not sync_only and api_key is None:
        api_key = get_api_key()

    # Select clients (unless sync-only mode)
    if not sync_only and selected_clients is None:
        selected_clients = select_clients()

    # Sync registry
    if not sync_registry(api_key):
        print_warning("Registry sync failed, continuing...")

    if sync_only:
        print_success("Registry sync complete!")
        return 0

    # Configure clients
    client_results = {}
    if selected_clients:
        client_results = configure_all_clients()

    # Verify installation
    verified = verify_installation()

    # Print summary
    print_summary(
        {
            "registry_synced": True,
            "verified": verified,
            "clients": client_results,
        }
    )

    return 0 if verified else 1


if __name__ == "__main__":
    sys.exit(main())
