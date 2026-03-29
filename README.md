<div align="center">

# Aceternity MCP

**A Model Context Protocol server for Aceternity UI components**

Discover, explore, and install 100+ Aceternity UI components directly from your AI assistant. Get intelligent recommendations, detailed metadata, and one-command installations.

[![PyPI - Version](https://img.shields.io/pypi/v/aceternity-mcp.svg)](https://pypi.org/project/aceternity-mcp/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aceternity-mcp.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compliant-1f6feb)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/github/license/devinoldenburg/aceternity-mcp)](./LICENSE)

</div>

---

## What is Aceternity MCP?

Aceternity MCP is a **pipx application** that brings the entire Aceternity UI component library to your AI assistant. Instead of just knowing component names, your AI gets rich metadata including:

- **Detailed descriptions** (60+ words per component)
- **Visual characteristics** and behavior patterns
- **Use case recommendations** and compatibility info
- **Installation commands** and dependencies
- **Scoring metrics** for animation, customization, performance impact

This helps your AI make informed decisions about which components fit your design needs.

## ⚡ Quick Start (60 seconds)

```bash
# 1. Install pipx (one-time setup)
brew install pipx
pipx ensurepath

# 2. Install Aceternity MCP
pipx install aceternity-mcp

# 3. Run the interactive setup
aceternity-mcp install
```

**That's it!** You're ready to use Aceternity MCP with your AI assistant.

## 🎯 CLI Commands

Aceternity MCP provides a powerful command-line interface:

| Command | Description |
|---------|-------------|
| `aceternity-mcp install` | Run interactive setup wizard |
| `aceternity-mcp update` | Check for and install updates |
| `aceternity-mcp repair` | Fix common installation issues |
| `aceternity-mcp status` | Show installation health |
| `aceternity-mcp diagnose` | Run diagnostics (JSON output) |
| `aceternity-mcp --version` | Show version |
| `aceternity-mcp --help` | Show help |

### Examples

```bash
# Check installation status
aceternity-mcp status

# Update to latest version
aceternity-mcp update

# Fix issues with registry or configs
aceternity-mcp repair

# Get detailed diagnostics
aceternity-mcp diagnose

# Repair only the registry
aceternity-mcp repair --registry
```

## 🤖 Configure Your AI Tool

After running `aceternity-mcp install`, the tool automatically configures your AI assistants. Manual configuration is also supported:

**Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "aceternity-ui": {
      "command": "aceternity-mcp-server",
      "args": []
    }
  }
}
```

**Claude Code** (`~/.claude/mcp.json`):
```json
{
  "mcpServers": {
    "aceternity-ui": {
      "command": "aceternity-mcp-server",
      "args": []
    }
  }
}
```

**Cline** (VS Code extension settings):
```json
{
  "mcpServers": {
    "aceternity-ui": {
      "command": "aceternity-mcp-server",
      "args": []
    }
  }
}
```

**Windsurf** (`~/.codeium/windsurf/mcp_config.json`):
```json
{
  "mcp_servers": {
    "aceternity_ui": {
      "command": "aceternity-mcp-server",
      "args": []
    }
  }
}
```

**OpenCode** (`~/.opencode/mcp.json`):
```json
{
  "mcpServers": {
    "aceternity-ui": {
      "command": "aceternity-mcp-server",
      "args": []
    }
  }
}
```

> **Note**: After configuration, restart your AI tool to load the new MCP server.

## 🛠️ Available MCP Tools

Once configured, your AI assistant can use these tools:

| Tool | Description |
|------|-------------|
| `list_components` | List all available components |
| `list_categories` | Show component categories |
| `search_components` | Search by name, description, or tags |
| `get_component` | Get detailed component information |
| `get_category` | Get all components in a category |
| `recommend_components` | Get recommendations for your use case |
| `recommend_combination` | Suggest complementary components |
| `match_components_to_project` | Match components to your project type |
| `install_component` | Install a component with dependencies |
| `filter_by_scores` | Filter by visual/animation intensity |

## 💬 Example Prompts

Try these with your AI assistant:

```
"Show me subtle dark background effects with low performance impact"
"Recommend a navbar + hero + CTA combination for a SaaS landing page"
"Find highly customizable card components for testimonials"
"Give me low-motion components suitable for a dashboard"
"Install Spotlight and show me what dependencies are needed"
"What components work well for dark mode dashboards?"
"Show me animated text effects that aren't too distracting"
```

## 📦 Installation

### Prerequisites

- **Python 3.10+** (required)
- **Node.js** (optional, for registry sync from Aceternity UI)
- **pipx** (recommended installation method)

### Step 1: Install pipx

```bash
# macOS
brew install pipx
pipx ensurepath

# Linux
python3 -m pip install --user pipx
pipx ensurepath

# Windows
pip install pipx
pipx ensurepath
```

### Step 2: Install Aceternity MCP

```bash
pipx install aceternity-mcp
```

### Step 3: Run Setup

```bash
# Interactive setup (recommended)
aceternity-mcp install

# Or configure all tools automatically
aceternity-mcp install --non-interactive
```

### What the Installer Does

1. ✅ Syncs 100+ components from Aceternity UI
2. ✅ Configures your AI tools automatically
3. ✅ Verifies the installation
4. ✅ Shows you next steps

## 🔧 Management Commands

### Check Status

```bash
aceternity-mcp status
```

Shows:
- Current version and update availability
- System information (platform, Python version)
- Health checks (registry, MCP command, Python)
- Client configuration status

### Update

```bash
# Check and install updates
aceternity-mcp update

# Non-interactive update
aceternity-mcp update --non-interactive
```

### Repair

```bash
# Fix all common issues
aceternity-mcp repair

# Repair only registry
aceternity-mcp repair --registry

# Repair only client configs
aceternity-mcp repair --configs

# Fix file permissions
aceternity-mcp repair --permissions
```

### Diagnostics

```bash
# Get JSON diagnostics
aceternity-mcp diagnose

# Verbose output
aceternity-mcp status --verbose
```

## 📚 Architecture

```
~/.local/pipx/venvs/aceternity-mcp/
├── bin/
│   ├── aceternity-mcp        # CLI management commands
│   ├── aceternity-mcp-server # MCP server
│   └── aceternity-mcp-install # Legacy installer
├── lib/python3.X/site-packages/aceternity_mcp/
│   ├── cli.py                # CLI implementation
│   ├── server.py             # MCP server
│   ├── install.py            # Installer
│   ├── registry.py           # Registry loader
│   ├── search.py             # Search engine
│   └── recommender.py        # Recommendation engine
└── share/aceternity-mcp/registry/
    ├── index.json            # Master index
    ├── components/           # Component metadata (106 components)
    └── categories/           # Category definitions (17 categories)
```

## 🧑‍💻 Development

### Clone and Install Locally

```bash
git clone https://github.com/devinoldenburg/aceternity-mcp.git
cd aceternity-mcp

# Install your local version with pipx
pipx install .

# Or install with editable mode for development
pipx inject aceternity-mcp -e .
```

### Validate Registry

```bash
# Compile check
python -m compileall src scripts

# Validate registry schema
python scripts/validate_registry.py
```

### Update Component Registry

```bash
# Sync latest components from Aceternity UI
python scripts/sync_registry.py

# With API key (optional)
python scripts/sync_registry.py --api-key "$ACETERNITY_API_KEY"

# Reinstall to bundle updated registry
pipx reinstall aceternity-mcp
```

### Run Tests

```bash
# Test CLI commands
aceternity-mcp --help
aceternity-mcp status
aceternity-mcp diagnose

# Test server
aceternity-mcp-server

# Test installer
aceternity-mcp-install
```

## 🌐 Supported AI Tools

| Tool | Config File | Status |
|------|-------------|--------|
| Cursor | `~/.cursor/mcp.json` | ✅ Supported |
| Claude Desktop | Platform-specific | ✅ Supported |
| Claude Code | `~/.claude/mcp.json` | ✅ Supported |
| Cline | VS Code extension | ✅ Supported |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | ✅ Supported |
| OpenCode | `~/.opencode/mcp.json` | ✅ Supported |

## 🔒 Security

- No secrets are committed to the repository
- API keys are optional and used only during sync operations
- Keys are not stored on disk
- The repository stores metadata descriptions, not component source files
- pipx provides isolated environment for security

## ❓ Troubleshooting

### Command Not Found

```bash
# Ensure pipx is in your PATH
pipx ensurepath

# Restart your terminal
# Or reload shell configuration
source ~/.zshrc  # or ~/.bashrc
```

### Registry Not Found

```bash
# Repair the installation
aceternity-mcp repair

# Or reinstall
pipx reinstall aceternity-mcp
```

### MCP Server Not Working

```bash
# Check status
aceternity-mcp status

# Get diagnostics
aceternity-mcp diagnose

# Repair configs
aceternity-mcp repair --configs
```

### Update Issues

```bash
# Force upgrade
pipx upgrade aceternity-mcp

# Or reinstall
pipx reinstall aceternity-mcp
```

## 📝 Contributing

Contributions are welcome! Please see:
- [Contributing Guide](./CONTRIBUTING.md)
- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Security Policy](./SECURITY.md)

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

## 🔗 Links

- [PyPI Package](https://pypi.org/project/aceternity-mcp/)
- [GitHub Repository](https://github.com/devinoldenburg/aceternity-mcp)
- [Issue Tracker](https://github.com/devinoldenburg/aceternity-mcp/issues)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Aceternity UI](https://ui.aceternity.com/)
