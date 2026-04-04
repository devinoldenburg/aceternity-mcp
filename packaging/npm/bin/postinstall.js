#!/usr/bin/env node
/**
 * Post-install script for npm package.
 * Checks if the Python aceternity-mcp package is available.
 */

const { execSync } = require("child_process");

function check() {
  try {
    execSync("aceternity-mcp-server --help", { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

if (!check()) {
  console.log(
    "\n" +
      "╔══════════════════════════════════════════════════════════╗\n" +
      "║  aceternity-mcp npm wrapper installed                   ║\n" +
      "║                                                         ║\n" +
      "║  The Python backend is required. Install it with:       ║\n" +
      "║                                                         ║\n" +
      "║    pipx install aceternity-mcp                          ║\n" +
      "║                                                         ║\n" +
      "║  Or with uv:                                            ║\n" +
      "║                                                         ║\n" +
      "║    uv tool install aceternity-mcp                       ║\n" +
      "╚══════════════════════════════════════════════════════════╝\n"
  );
}
