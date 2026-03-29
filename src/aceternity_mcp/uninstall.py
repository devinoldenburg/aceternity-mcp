#!/usr/bin/env python3
"""Uninstall Aceternity MCP from all AI tools.

Removes MCP configuration from all supported AI tools.

Usage:
    aceternity-mcp uninstall
    aceternity-mcp-uninstall
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .install import (
    Colors,
    SUPPORTED_CLIENTS,
    expand_path,
    find_config_file,
    print_error,
    print_header,
    print_info,
    print_section,
    print_success,
    print_warning,
)


def remove_from_client(client_name: str) -> bool:
    """Remove MCP configuration from a specific client."""
    client = SUPPORTED_CLIENTS[client_name]
    config_path = find_config_file(list(client["config_paths"]))
    config_key = client["config_key"]

    if not config_path or not config_path.exists():
        print_info(f"{client['name']}: No config file found")
        return True

    print_info(f"Removing from {client['name']}...")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Determine server name
        if config_key == "mcp_servers":
            server_name = "aceternity_ui"
        else:
            server_name = "aceternity-ui"

        # Remove if present
        if config_key in config and server_name in config[config_key]:
            del config[config_key][server_name]

            # Save updated config
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print_success(f"Removed from {client['name']}")
            return True
        else:
            print_info(f"{client['name']}: Aceternity MCP not configured")
            return True

    except (json.JSONDecodeError, IOError) as e:
        print_error(f"Failed to update {client['name']}: {e}")
        return False


def uninstall_all_clients() -> dict[str, bool]:
    """Remove MCP configuration from all clients."""
    results = {}

    print_section("Removing from AI Tools")

    for client_name in SUPPORTED_CLIENTS:
        results[client_name] = remove_from_client(client_name)

    return results


def verify_removal() -> bool:
    """Verify MCP server is removed from configs."""
    print_section("Verifying Removal")

    all_removed = True
    for client_name, client_info in SUPPORTED_CLIENTS.items():
        config_path = find_config_file(list(client_info["config_paths"]))
        if config_path and config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                config_key = client_info["config_key"]
                if config_key in config:
                    if (
                        "aceternity-ui" in config[config_key]
                        or "aceternity_ui" in config[config_key]
                    ):
                        print_error(f"{client_info['name']}: Still configured!")
                        all_removed = False
            except Exception:
                pass

    if all_removed:
        print_success("MCP server removed from all tools")

    return all_removed


def main() -> int:
    """Main uninstall function."""
    print_header("Aceternity MCP - Uninstall", "Remove from all AI tools")

    # Remove from all clients
    results = uninstall_all_clients()

    # Verify removal
    verify_removal()

    # Summary
    print("\n" + "=" * 60)
    print("Uninstall Summary")
    print("=" * 60)

    removed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"Removed from {removed}/{total} AI tools")

    if removed == total:
        print_success("Uninstall completed successfully!")
        print("\nNote: The aceternity-mcp package is still installed.")
        print("To completely remove: pipx uninstall aceternity-mcp")
        return 0
    else:
        print_warning("Some tools could not be updated")
        return 1


if __name__ == "__main__":
    sys.exit(main())
