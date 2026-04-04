#!/usr/bin/env python3
"""Universal installer for Aceternity MCP Server."""

from __future__ import annotations

import json
import platform
import re
import shutil
import subprocess  # nosec B404
import sys
from pathlib import Path


def get_platform() -> str:
    """Detect the current operating system."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    if system == "windows":
        return "windows"
    if system == "linux":
        return "linux"
    return "unknown"


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    RED = "\033[31m"
    DIM = "\033[2m"


SUPPORTED_CLIENTS = {
    "claude-desktop": {
        "name": "Claude Desktop",
        "config_paths": [
            "~/Library/Application Support/Claude/claude_desktop_config.json",
            "~/.config/Claude/claude_desktop_config.json",
            "%APPDATA%/Claude/claude_desktop_config.json",
        ],
        "config_key": "mcpServers",
        "description": "Claude Desktop App",
    },
    "cursor": {
        "name": "Cursor",
        "config_paths": ["~/.cursor/mcp.json"],
        "config_key": "mcpServers",
        "description": "Cursor IDE",
    },
    "claude-code": {
        "name": "Claude Code CLI",
        "config_paths": ["~/.claude/mcp.json"],
        "config_key": "mcpServers",
        "description": "Claude Code CLI",
    },
    "cline": {
        "name": "Cline",
        "config_paths": [
            "~/.vscode/extensions/saoudrizwan.claude-dev-*/settings/cline_mcp_settings.json"
        ],
        "config_key": "mcpServers",
        "description": "Cline VS Code Extension",
    },
    "windsurf": {
        "name": "Windsurf",
        "config_paths": ["~/.codeium/windsurf/mcp_config.json"],
        "config_key": "mcp_servers",
        "description": "Windsurf IDE",
    },
    "opencode": {
        "name": "OpenCode",
        "config_paths": ["~/.opencode/mcp.json", "~/.config/opencode/opencode.jsonc"],
        "config_key": "mcpServers",
        "description": "OpenCode AI Assistant",
    },
}


def print_header(title: str, subtitle: str = "") -> None:
    width = 70
    print(f"\n{Colors.CYAN}{'=' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title.center(width)}{Colors.RESET}")
    if subtitle:
        print(f"{Colors.CYAN}{subtitle.center(width)}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * width}{Colors.RESET}\n")


def print_section(title: str) -> None:
    print(f"\n{Colors.BOLD}{Colors.BLUE}► {title}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 50}{Colors.RESET}")


def print_success(message: str) -> None:
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str) -> None:
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_info(message: str) -> None:
    print(f"{Colors.CYAN}→ {message}{Colors.RESET}")


def expand_path(path: str) -> Path:
    return Path(path).expanduser().resolve()


def configure_opencode_main_config() -> bool:
    """Configure OpenCode's main opencode.jsonc file."""
    config_path = expand_path("~/.config/opencode/opencode.jsonc")

    if not config_path.exists():
        print_info(f"OpenCode main config not found: {config_path}")
        return False

    try:
        # Read the file
        with config_path.open(encoding="utf-8") as f:
            content = f.read()

        # Check if aceternity-ui already exists
        if '"aceternity-ui"' in content or '"aceternity_ui"' in content:
            print_info("OpenCode: Already configured in opencode.jsonc")
            return True

        # Find the mcp section and add our server
        # Look for "mcp": { pattern
        mcp_pattern = r'("mcp"\s*:\s*\{)'
        match = re.search(mcp_pattern, content)

        if match:
            # Insert after "mcp": {
            insert_pos = match.end()
            new_entry = (
                '\n    "aceternity-ui": {\n'
                '      "type": "local",\n'
                '      "command": ["aceternity-mcp-server"],\n'
                '      "enabled": true\n'
                "    },"
            )
            new_content = content[:insert_pos] + new_entry + content[insert_pos:]

            # Write back
            with config_path.open("w", encoding="utf-8") as f:
                f.write(new_content)

            print_success("OpenCode: Configured in opencode.jsonc")
            return True
        print_error("OpenCode: Could not find 'mcp' section in opencode.jsonc")
        return False

    except Exception as e:
        print_error(f"OpenCode: Failed to update opencode.jsonc: {e}")
        return False


def configure_mcp_json(
    client_name: str, mcp_command: str = "aceternity-mcp-server"
) -> bool:
    """Configure a standard mcp.json file for a client."""
    client = SUPPORTED_CLIENTS[client_name]
    config_path = expand_path(client["config_paths"][0])
    config_key = client["config_key"]

    print_info(f"Configuring {client['name']}...")
    print_info(f"Config path: {config_path}")

    # Load existing config
    config = {}
    if config_path.exists():
        try:
            with config_path.open(encoding="utf-8") as f:
                config = json.load(f)
        except (OSError, json.JSONDecodeError):
            config = {}

    # Ensure the config key exists
    if config_key not in config:
        config[config_key] = {}

    # Determine server name
    server_name = "aceternity_ui" if config_key == "mcp_servers" else "aceternity-ui"

    # Create server configuration
    server_config = {
        "command": mcp_command,
        "args": [],
    }

    # Add to config
    config[config_key][server_name] = server_config

    # Save config
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print_success(f"{client['name']} configured at {config_path}")
        return True
    except OSError as e:
        print_error(f"Failed to write config: {e}")
        return False


def configure_all_clients(
    mcp_command: str = "aceternity-mcp-server",
) -> dict[str, bool]:
    """Configure all supported MCP clients."""
    results = {}

    print_section("Configuring AI Tools")
    print_info(f"Configuring MCP server: {mcp_command}")

    for client_name in SUPPORTED_CLIENTS:
        # For OpenCode, configure BOTH locations
        if client_name == "opencode":
            # Configure main config (opencode.jsonc)
            main_configured = configure_opencode_main_config()
            # Configure mcp.json as fallback
            mcp_configured = configure_mcp_json(client_name, mcp_command)
            results[client_name] = main_configured or mcp_configured
        else:
            # For others, just configure mcp.json
            results[client_name] = configure_mcp_json(client_name, mcp_command)

    return results


def verify_installation() -> bool:
    """Verify the MCP server installation."""
    print_section("Verifying Installation")

    cli_ok, cli_output = run_command(["aceternity-mcp", "--help"], timeout=8)
    server_path = shutil.which("aceternity-mcp-server")
    server_ok = server_path is not None

    if cli_ok and server_ok:
        print_success("MCP CLI and server are accessible")
        print_info(f"Server command: {server_path}")
        return True
    if not cli_ok:
        details = cli_output.strip() if cli_output else "unknown error"
        print_error(f"MCP CLI not accessible: {details}")
    if not server_ok:
        print_error("MCP server command not found on PATH")
    return False


def main() -> int:
    """Main installation function."""
    print_header(
        "Aceternity MCP Server - Universal Installer",
        "Automated setup for all AI tools",
    )

    print_info(f"Platform: {sys.platform}")
    print_info(f"Python: {sys.version_info.major}.{sys.version_info.minor}")

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
    print("  • Claude Desktop - Quit and reopen the app")
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


# Exported for CLI
def print_warning(message: str) -> None:
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def run_command(
    command: list[str],
    cwd: Path | None = None,
    capture: bool = True,
    timeout: float | None = None,
) -> tuple[bool, str]:
    try:
        result = subprocess.run(  # nosec B603
            command,
            cwd=cwd,
            capture_output=capture,
            text=True,
            check=False,
            timeout=timeout,
        )
        return result.returncode == 0, (
            result.stdout + result.stderr
        ) if capture else ""
    except subprocess.TimeoutExpired:
        timeout_value = timeout if timeout is not None else "configured"
        return False, f"Command timed out after {timeout_value}s"
    except FileNotFoundError as e:
        return False, f"Command not found: {e}"
    except Exception as e:
        return False, str(e)


def check_prerequisites() -> dict[str, bool]:
    results = {}
    version = sys.version_info
    results["python"] = version.major == 3 and version.minor >= 10
    results["npx"], _ = run_command(["npx", "--version"])
    return results


def find_config_file(config_paths: list[str]) -> Path | None:
    for path in config_paths:
        expanded = expand_path(path)
        if expanded and expanded.exists():
            return expanded
    return expand_path(config_paths[0]) if config_paths else None


def select_clients() -> list[str]:
    if not sys.stdin.isatty():
        return list(SUPPORTED_CLIENTS.keys())
    return list(SUPPORTED_CLIENTS.keys())


def sync_registry(_api_key: str | None = None) -> bool:
    print_info("Registry is bundled. Sync skipped.")
    return True
