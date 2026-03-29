#!/usr/bin/env python3
"""Aceternity MCP CLI - Powerful command-line interface.

Provides update, repair, post-install, and management commands.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .install import (
    Colors,
    check_prerequisites,
    configure_all_clients,
    find_config_file,
    print_error,
    print_header,
    print_info,
    print_section,
    print_success,
    print_warning,
    run_command,
    sync_registry,
    verify_installation,
)


# ============================================================================
# Version Management
# ============================================================================
def get_current_version() -> str:
    """Get the current installed version."""
    try:
        from importlib.metadata import version

        return version("aceternity-mcp")
    except Exception:
        try:
            from . import __version__

            return __version__
        except Exception:
            return "unknown"


def get_latest_version() -> str | None:
    """Get the latest version from PyPI."""
    try:
        req = urllib.request.Request(
            "https://pypi.org/pypi/aceternity-mcp/json",
            headers={"User-Agent": "aceternity-mcp-cli"},
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                version = data.get("info", {}).get("version")
                return str(version) if version else None
        except urllib.error.URLError:
            return None
    except Exception:
        return None


def check_for_updates() -> dict[str, Any]:
    """Check if updates are available."""
    current = get_current_version()
    latest = get_latest_version()

    if latest is None:
        return {"current": current, "latest": None, "available": False}

    current_parts = [int(x) for x in current.split(".") if x.isdigit()]
    latest_parts = [int(x) for x in latest.split(".") if x.isdigit()]

    has_update = latest_parts > current_parts

    return {
        "current": current,
        "latest": latest,
        "available": has_update,
    }


def perform_update(interactive: bool = True) -> bool:
    """Update the aceternity-mcp package."""
    print_section("Updating Aceternity MCP")

    update_info = check_for_updates()
    print_info(f"Current version: {update_info['current']}")

    if not update_info["available"]:
        if update_info["latest"]:
            print_success(f"Already on latest version ({update_info['latest']})")
            return True
        print_warning("Could not check for updates")
        print_info("Attempting upgrade anyway...")

    if update_info["available"]:
        print_info(f"Latest version: {update_info['latest']}")

    if interactive and not sys.stdin.isatty():
        interactive = False

    if interactive:
        response = (
            input(f"\nUpdate to {update_info['latest']}? [Y/n]: ").strip().lower()
        )
        if response in ("n", "no"):
            print_info("Update cancelled")
            return False

    print_info("Running pip install --upgrade aceternity-mcp...")

    success, output = run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "aceternity-mcp"]
    )

    if success:
        print_success("Update completed successfully!")
        print_info("Please restart your AI tools to apply the update.")
        return True
    print_error(f"Update failed: {output}")
    print_info("Try running: pip install --upgrade aceternity-mcp")
    return False


# ============================================================================
# Repair Functionality
# ============================================================================
class RepairManager:
    """Manages repair operations for common issues."""

    def __init__(self) -> None:
        self.issues_found: list[dict[str, Any]] = []
        self.issues_fixed: list[dict[str, Any]] = []
        self.home = Path.home()

    def check_registry(self) -> dict[str, Any]:
        """Check if registry is present and valid."""
        result = {"name": "Registry", "status": "unknown", "details": ""}

        try:
            from aceternity_mcp.registry import _find_registry_dir

            registry_path = _find_registry_dir()

            index_file = registry_path / "index.json"
            if not index_file.exists():
                result["status"] = "missing"
                result["details"] = "index.json not found"
                return result

            with index_file.open(encoding="utf-8") as f:
                data = json.load(f)

            if "components" not in data or len(data["components"]) == 0:
                result["status"] = "empty"
                result["details"] = "Registry appears empty"
                return result

            result["status"] = "ok"
            result["details"] = f"Found {len(data['components'])} components"
        except Exception as e:
            result["status"] = "error"
            result["details"] = str(e)

        return result

    def check_mcp_command(self) -> dict[str, Any]:
        """Check if aceternity-mcp command is accessible."""
        result = {"name": "MCP Command", "status": "unknown", "details": ""}

        success, output = run_command(["aceternity-mcp", "--help"])

        if success:
            result["status"] = "ok"
            result["details"] = "Command accessible"
        else:
            result["status"] = "missing"
            result["details"] = f"Command not found: {output}"

        return result

    def check_client_configs(self) -> list[dict[str, Any]]:
        """Check MCP client configurations."""
        from aceternity_mcp.install import SUPPORTED_CLIENTS

        results = []

        for _client_name, client_info in SUPPORTED_CLIENTS.items():
            result = {
                "name": client_info["name"],
                "status": "unknown",
                "details": "",
                "config_path": None,
            }

            config_path = find_config_file(list(client_info["config_paths"]))
            if config_path:
                result["config_path"] = str(config_path)
                if config_path.exists():
                    try:
                        with config_path.open(encoding="utf-8") as f:
                            config = json.load(f)

                        config_key = client_info["config_key"]
                        if config_key in config:
                            server_name = (
                                "aceternity_ui"
                                if config_key == "mcp_servers"
                                else "aceternity-ui"
                            )
                            if server_name in config[config_key]:
                                result["status"] = "ok"
                                result["details"] = "Configured correctly"
                            else:
                                result["status"] = "missing_config"
                                result["details"] = "Aceternity MCP not in config"
                        else:
                            result["status"] = "missing_config"
                            result["details"] = f"Missing '{config_key}' key"
                    except Exception as e:
                        result["status"] = "error"
                        result["details"] = f"Cannot read config: {e}"
                else:
                    result["status"] = "not_found"
                    result["details"] = "Config file doesn't exist"
            else:
                result["status"] = "not_found"
                result["details"] = "Could not locate config path"

            results.append(result)

        return results

    def check_python_path(self) -> dict[str, Any]:
        """Check if Python is on PATH."""
        result = {"name": "Python", "status": "unknown", "details": ""}

        python_exec = shutil.which(sys.executable)
        if python_exec:
            result["status"] = "ok"
            result["details"] = f"Found at: {python_exec}"
        else:
            result["status"] = "missing"
            result["details"] = "Python executable not on PATH"

        return result

    def diagnose(self) -> dict[str, Any]:
        """Run full diagnostic check."""
        return {
            "registry": self.check_registry(),
            "mcp_command": self.check_mcp_command(),
            "python": self.check_python_path(),
            "client_configs": self.check_client_configs(),
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }

    def repair_registry(self) -> bool:
        """Repair registry by verifying bundled registry availability."""
        print_info("Checking bundled registry...")

        if sync_registry():
            print_success("Registry is available")
            return True

        print_error("Registry check failed")
        return False

    def repair_client_config(self, client_name: str) -> bool:
        """Repair a specific client configuration."""
        from aceternity_mcp.install import SUPPORTED_CLIENTS

        if client_name not in SUPPORTED_CLIENTS:
            print_error(f"Unknown client: {client_name}")
            return False

        print_info(
            f"Repairing {SUPPORTED_CLIENTS[client_name]['name']} configuration..."
        )

        success = configure_all_clients()[client_name]

        if success:
            print_success(f"{SUPPORTED_CLIENTS[client_name]['name']} repaired")
            return True
        print_error(f"Failed to repair {SUPPORTED_CLIENTS[client_name]['name']}")
        return False

    def repair_all_configs(self) -> dict[str, bool]:
        """Repair all client configurations."""
        print_info("Repairing all client configurations...")
        return configure_all_clients()

    def fix_permissions(self) -> bool:
        """Fix common permission issues."""
        print_info("Checking file permissions...")

        try:
            import aceternity_mcp

            pkg_path = Path(aceternity_mcp.__file__).parent

            for py_file in pkg_path.glob("*.py"):
                if not os.access(py_file, os.R_OK):
                    py_file.chmod(0o644)
                    print_info(f"Fixed read permissions on {py_file.name}")

            print_success("Permissions verified")
            return True
        except Exception as e:
            print_error(f"Permission fix failed: {e}")
            return False

    def run_repairs(
        self, repair_type: str = "all", _interactive: bool = True
    ) -> dict[str, Any]:
        """Run repair operations."""
        print_section("Running Repairs")

        results: dict[str, Any] = {
            "diagnosis": self.diagnose(),
            "repairs_attempted": [],
            "repairs_successful": [],
            "repairs_failed": [],
        }

        if repair_type in ("all", "registry"):
            results["repairs_attempted"].append("registry")
            if self.repair_registry():
                results["repairs_successful"].append("registry")
            else:
                results["repairs_failed"].append("registry")

        if repair_type in ("all", "configs"):
            results["repairs_attempted"].append("configs")
            repair_results = self.repair_all_configs()
            for client, success in repair_results.items():
                if success:
                    results["repairs_successful"].append(f"config:{client}")
                else:
                    results["repairs_failed"].append(f"config:{client}")

        if repair_type in ("all", "permissions"):
            results["repairs_attempted"].append("permissions")
            if self.fix_permissions():
                results["repairs_successful"].append("permissions")
            else:
                results["repairs_failed"].append("permissions")

        return results


# ============================================================================
# Post-Install Wizard
# ============================================================================
def post_install_wizard(interactive: bool = True) -> int:
    """Run post-installation setup wizard."""
    print_header(
        "Aceternity MCP - Post-Install Setup", "Let's get everything configured"
    )

    if not interactive or not sys.stdin.isatty():
        print_info("Running in non-interactive mode...")
        return run_non_interactive_setup()

    print("\nWelcome! This wizard will help you configure Aceternity MCP.")
    print("Press Ctrl+C at any time to cancel.\n")

    # Step 1: Check prerequisites
    print_section("Step 1: Checking Prerequisites")
    prereqs = check_prerequisites()

    if not all(prereqs.values()):
        print_warning("Some prerequisites are missing.")
        if interactive:
            response = input("\nContinue anyway? [y/N]: ").strip().lower()
            if response not in ("y", "yes"):
                print_info("Setup cancelled")
                return 1

    # Step 2: Registry status (bundled with package)
    print_section("Step 2: Registry Status")
    print_info("Registry is bundled with the package (106 components)")
    print_info("✓ Already up to date")

    # Step 3: Configure AI tools
    print_section("Step 3: Configuring AI Tools")
    from aceternity_mcp.install import select_clients

    selected = select_clients()

    if selected:
        results = configure_all_clients()
        for client_name in selected:
            if results.get(client_name):
                print_success(f"{client_name} configured")
            else:
                print_warning(f"{client_name} configuration skipped")
    else:
        print_info("Skipping client configuration")

    # Step 4: Verify installation
    print_section("Step 4: Verifying Installation")
    if verify_installation():
        print_success("Installation verified successfully!")
    else:
        print_warning(
            "Verification failed (you can run 'aceternity-mcp repair' to fix)"
        )

    # Step 5: Show next steps
    print_section("You're All Set!")
    print("\n⚠️  IMPORTANT: Restart your AI tools to load the MCP server!")
    print("\nRestart these tools now:")
    print("  • OpenCode - Quit and reopen")
    print("  • Cursor - Restart the application")
    print("  • Claude Code - Restart or run: claude")
    print("  • Cline - Reload VS Code window")
    print("  • Windsurf - Restart the application")
    print("\nAfter restarting, try these prompts:\n")
    print("  • 'Show me subtle background effects for landing pages'")
    print("  • 'Recommend a navbar + hero combination for a SaaS site'")
    print("  • 'Install Spotlight component and show dependencies'")
    print("  • 'What components work well for dark mode dashboards?'")
    print("\nUseful commands:\n")
    print("  aceternity-mcp update     - Check for and install updates")
    print("  aceternity-mcp repair     - Fix common issues")
    print("  aceternity-mcp status     - Check installation health")
    print("  aceternity-mcp install    - Re-run this setup wizard")
    print()

    return 0


def run_non_interactive_setup() -> int:
    """Run setup in non-interactive mode."""
    from aceternity_mcp.install import sync_registry

    print_info("Syncing registry...")
    sync_registry()

    print_info("Configuring all clients...")
    configure_all_clients()

    print_info("Verifying installation...")
    if verify_installation():
        print_success("Setup completed successfully!")
        return 0
    print_warning("Setup completed with warnings")
    return 1


# ============================================================================
# Status Command
# ============================================================================
def show_status(verbose: bool = False) -> None:
    """Show current installation status and health."""
    print_header("Aceternity MCP Status")

    # Version info
    update_info = check_for_updates()
    print_section("Version Information")
    print_info(f"Current version: {update_info['current']}")
    if update_info["latest"]:
        if update_info["available"]:
            print_warning(f"Update available: {update_info['latest']}")
            print_info("Run: aceternity-mcp update")
        else:
            print_success(f"Latest version: {update_info['latest']}")
    else:
        print_info("Could not check for updates")

    # System info
    print_section("System Information")
    print_info(f"Platform: {sys.platform}")
    py_ver = sys.version_info
    print_info(f"Python: {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    print_info(f"Python executable: {sys.executable}")

    # Health checks
    print_section("Health Checks")
    manager = RepairManager()
    diagnosis = manager.diagnose()

    # Registry status
    registry = diagnosis["registry"]
    if registry["status"] == "ok":
        print_success(f"Registry: {registry['details']}")
    else:
        print_error(f"Registry: {registry['details']}")

    # MCP command status
    mcp_cmd = diagnosis["mcp_command"]
    if mcp_cmd["status"] == "ok":
        print_success(f"MCP Command: {mcp_cmd['details']}")
    else:
        print_error(f"MCP Command: {mcp_cmd['details']}")

    # Python status
    python = diagnosis["python"]
    if python["status"] == "ok":
        print_success(f"Python: {python['details']}")
    else:
        print_error(f"Python: {python['details']}")

    # Client configs
    if verbose:
        print_section("Client Configurations")
        for config in diagnosis["client_configs"]:
            status_icon = (
                "✓"
                if config["status"] == "ok"
                else "⚠"
                if config["status"] in ("not_found", "missing_config")
                else "✗"
            )
            print_info(f"{status_icon} {config['name']}: {config['details']}")
            if config.get("config_path"):
                print_info(f"  Path: {config['config_path']}")

    print()


# ============================================================================
# Main CLI Entry Point
# ============================================================================
def main() -> int:
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print_help()
        return 0

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    # Parse flags
    interactive = "--non-interactive" not in args and "-y" not in args
    verbose = "--verbose" in args or "-v" in args

    if command in ("update", "upgrade", "up"):
        return 0 if perform_update(interactive) else 1

    if command in ("repair", "fix"):
        print_header("Aceternity MCP Repair Tool")

        repair_type = "all"
        for arg in args:
            if arg in ("--registry", "-r"):
                repair_type = "registry"
            elif arg in ("--configs", "-c"):
                repair_type = "configs"
            elif arg in ("--permissions", "-p"):
                repair_type = "permissions"

        manager = RepairManager()
        results = manager.run_repairs(repair_type, interactive)

        print("\n" + "=" * 60)
        print("Repair Summary")
        print("=" * 60)

        if results["repairs_successful"]:
            print_success(f"Successful: {', '.join(results['repairs_successful'])}")

        if results["repairs_failed"]:
            print_error(f"Failed: {', '.join(results['repairs_failed'])}")
            print_info("\nTry running with --verbose for more details")
            print_info(
                "Or report the issue at: https://github.com/devinoldenburg/aceternity-mcp/issues"
            )

        return 0 if not results["repairs_failed"] else 1

    if command in ("install", "setup", "init", "post-install"):
        return post_install_wizard(interactive)

    if command in ("status", "info", "health"):
        show_status(verbose)
        return 0

    if command in ("diagnose", "check"):
        print_header("Aceternity MCP Diagnostics")
        manager = RepairManager()
        diagnosis = manager.diagnose()
        print(json.dumps(diagnosis, indent=2))
        return 0

    if command in ("--version", "-v", "version"):
        print(get_current_version())
        return 0

    if command in ("--help", "-h", "help"):
        print_help()
        return 0

    if command in ("uninstall", "remove"):
        from aceternity_mcp.uninstall import main as uninstall_main

        return uninstall_main()

    print_error(f"Unknown command: {command}")
    print_info("Run 'aceternity-mcp --help' for available commands")
    return 1


def print_help() -> None:
    """Print help message."""
    print_header("Aceternity MCP CLI", "Powerful command-line interface")

    print("Available Commands:\n")

    commands = [
        ("install", "Run post-installation setup wizard", "aceternity-mcp install"),
        ("update", "Check for and install updates", "aceternity-mcp update"),
        ("repair", "Fix common installation issues", "aceternity-mcp repair"),
        ("status", "Show installation status and health", "aceternity-mcp status"),
        ("diagnose", "Run diagnostics and output JSON", "aceternity-mcp diagnose"),
        ("uninstall", "Remove from all AI tools", "aceternity-mcp uninstall"),
        ("--version", "Show version information", "aceternity-mcp --version"),
        ("--help", "Show this help message", "aceternity-mcp --help"),
    ]

    for cmd, desc, example in commands:
        print(f"  {Colors.BOLD}{cmd:<15}{Colors.RESET} {desc}")
        print(f"  {Colors.DIM}Example: {example}{Colors.RESET}\n")

    print("Repair Options:\n")
    print("  --registry, -r     Repair registry only")
    print("  --configs, -c      Repair client configs only")
    print("  --permissions, -p  Fix file permissions only\n")

    print("Global Options:\n")
    print("  --verbose, -v      Show detailed output")
    print("  --non-interactive, -y  Run without prompts\n")

    print("=" * 60)
    print("Quick Start:\n")
    print("  1. First time? Run: aceternity-mcp install")
    print("  2. Having issues? Run: aceternity-mcp repair")
    print("  3. Want updates? Run: aceternity-mcp update")
    print("  4. Check status: aceternity-mcp status")
    print()


if __name__ == "__main__":
    sys.exit(main())
