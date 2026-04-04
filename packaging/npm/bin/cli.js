#!/usr/bin/env node
/**
 * aceternity-mcp-server npm wrapper
 *
 * Delegates to the Python aceternity-mcp-server command.
 * Install the Python package first: pipx install aceternity-mcp
 */

const { spawn } = require("child_process");
const { execSync } = require("child_process");

function findCommand() {
  // Try direct command first
  try {
    execSync("aceternity-mcp-server --help", { stdio: "ignore" });
    return "aceternity-mcp-server";
  } catch {}

  // Try via uvx
  try {
    execSync("uvx --from aceternity-mcp aceternity-mcp-server --help", {
      stdio: "ignore",
    });
    return null; // Will use uvx path
  } catch {}

  // Try via pipx
  try {
    execSync("pipx run aceternity-mcp-server --help", { stdio: "ignore" });
    return null; // Will use pipx path
  } catch {}

  return null;
}

const directCmd = findCommand();

if (directCmd) {
  const child = spawn(directCmd, process.argv.slice(2), {
    stdio: "inherit",
  });
  child.on("exit", (code) => process.exit(code || 0));
} else {
  // Try uvx first, then pipx
  let cmd, args;
  try {
    execSync("uvx --version", { stdio: "ignore" });
    cmd = "uvx";
    args = [
      "--from",
      "aceternity-mcp",
      "aceternity-mcp-server",
      ...process.argv.slice(2),
    ];
  } catch {
    cmd = "pipx";
    args = ["run", "aceternity-mcp-server", ...process.argv.slice(2)];
  }

  const child = spawn(cmd, args, { stdio: "inherit" });
  child.on("exit", (code) => process.exit(code || 0));
  child.on("error", () => {
    console.error(
      "Error: aceternity-mcp-server not found.\n" +
        "Install it with: pipx install aceternity-mcp\n" +
        "Or: pip install aceternity-mcp"
    );
    process.exit(1);
  });
}
