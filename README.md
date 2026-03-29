<div align="center">

# Aceternity MCP

**A Model Context Protocol server for Aceternity UI components**

Discover, explore, and install 106 Aceternity UI components directly from your AI assistant. Get intelligent recommendations, detailed metadata, and installation instructions.

[![PyPI - Version](https://img.shields.io/pypi/v/aceternity-mcp.svg)](https://pypi.org/project/aceternity-mcp/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aceternity-mcp.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compliant-1f6feb)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/github/license/devinoldenburg/aceternity-mcp)](./LICENSE)

</div>

---

## What is Aceternity MCP?

Aceternity MCP is a **pipx application** that brings the Aceternity UI component library to your AI assistant through the Model Context Protocol. Your AI gets access to rich metadata including:

- **Detailed descriptions** for each component
- **Visual characteristics** and behavior patterns
- **Use case recommendations** and compatibility info
- **Installation commands** and dependencies
- **Scoring metrics** for animation intensity, customization level, and performance impact

This helps your AI make informed decisions about which components fit your design needs.

## ⚡ Quick Start

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

Aceternity MCP provides a command-line interface for management:

| Command | Description |
|---------|-------------|
| `aceternity-mcp install` | Run interactive setup wizard |
| `aceternity-mcp update` | Check for and install updates |
| `aceternity-mcp repair` | Fix common installation issues |
| `aceternity-mcp status` | Show installation health |
| `aceternity-mcp diagnose` | Run diagnostics (JSON output) |
| `aceternity-mcp uninstall` | Remove from all AI tools |
| `aceternity-mcp --version` | Show version |
| `aceternity-mcp --help` | Show help |

**Command aliases:**
- Update: `update`, `upgrade`, `up`
- Repair: `repair`, `fix`
- Install: `install`, `setup`, `init`, `post-install`
- Status: `status`, `info`, `health`
- Diagnose: `diagnose`, `check`
- Uninstall: `uninstall`, `remove`

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

# Remove from all AI tools
aceternity-mcp uninstall
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

1. ✅ Configures all supported AI tools automatically
2. ✅ Verifies the MCP server installation
3. ✅ Provides restart instructions for each tool
4. ✅ Shows next steps and usage examples

The component registry (106 components) is bundled with the package during installation via pipx.

## 🔧 Management Commands

### Check Status

```bash
aceternity-mcp status
```

Shows:
- Current version and update availability
- System information (platform, Python version)
- Health checks (registry, MCP command, Python)
- Client configuration status for supported AI tools

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

**Repair options:**
- `--registry` or `-r`: Repair only the component registry
- `--configs` or `-c`: Repair only AI tool configurations
- `--permissions` or `-p`: Fix file permissions

### Diagnostics

```bash
# Get JSON diagnostics
aceternity-mcp diagnose

# Verbose output
aceternity-mcp status --verbose
```

### Uninstall

```bash
# Remove from all AI tools
aceternity-mcp uninstall
```

Removes MCP server configuration from all supported AI tools. Note: This does not uninstall the pipx package itself. To completely remove:

```bash
pipx uninstall aceternity-mcp
```

## 📚 Architecture

**Package installation location** (pipx):
```
~/.local/pipx/venvs/aceternity-mcp/
├── bin/
│   ├── aceternity-mcp         # CLI management commands
│   ├── aceternity-mcp-server  # MCP server executable
│   └── aceternity-mcp-install # Legacy installer script
└── lib/python3.X/site-packages/aceternity_mcp/
    ├── __init__.py            # Package initialization
    ├── cli.py                 # CLI implementation (677 lines)
    ├── server.py              # MCP server with tools (469 lines)
    ├── install.py             # Installation wizard
    ├── uninstall.py           # Uninstallation utility
    ├── models.py              # Data models
    ├── registry.py            # Registry loader
    ├── search.py              # Search engine
    └── recommender.py         # Recommendation engine
```

**Bundled registry** (installed to):
```
~/.local/pipx/venvs/aceternity-mcp/share/aceternity-mcp/registry/
├── index.json                 # Master component index
├── components/                # 106 component metadata files
│   ├── 3d-globe.json
│   ├── 3d-pin.json
│   ├── animated-tooltip.json
│   └── ... (103 more)
└── categories/                # 17 category definitions
    ├── backgrounds.json
    ├── cards.json
    └── ... (15 more)
```

**Source repository structure**:
```
aceternity-mcp/
├── src/aceternity_mcp/        # Python package source
├── registry/                  # Component registry (source)
│   ├── components/            # 106 component JSON files
│   ├── categories/            # 17 category JSON files
│   └── index.json             # Generated index
├── scripts/                   # Maintenance scripts
│   ├── sync_registry.py       # Sync from Aceternity UI
│   └── validate_registry.py   # Validate registry schema
├── tests/                     # Test suite
└── pyproject.toml             # Package configuration
```

## 🧑‍💻 Development

### Clone and Install Locally

```bash
git clone https://github.com/devinoldenburg/aceternity-mcp.git
cd aceternity-mcp

# Install your local version with pipx
pipx install .

# Or install in editable mode for development
pipx inject aceternity-mcp --pip-args "-e ."
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

# Reinstall to bundle updated registry
pipx reinstall aceternity-mcp
```

The `sync_registry.py` script fetches component data from the Aceternity UI website and generates the registry JSON files. No API key is required.

### Run Tests

```bash
# Run test suite
python -m pytest tests/

# Or use the test runner script
python scripts/run_tests.py

# Test CLI commands manually
aceternity-mcp --help
aceternity-mcp status
aceternity-mcp diagnose

# Test MCP server
aceternity-mcp-server
```

### Package Structure

- **src/aceternity_mcp/**: Main Python package
  - `server.py`: MCP server exposing tools to AI assistants
  - `cli.py`: Command-line interface for management
  - `install.py`: Interactive installation wizard
  - `uninstall.py`: Removal utility
  - `registry.py`: Registry loading and management
  - `search.py`: Component search engine
  - `recommender.py`: Recommendation logic
  - `models.py`: Data models for components

- **registry/**: Component metadata (106 components, 17 categories)
- **scripts/**: Maintenance and sync utilities
- **tests/**: Test suite for all functionality

## 🌐 Supported AI Tools

| Tool | Config File | Configuration Key |
|------|-------------|-------------------|
| Cursor | `~/.cursor/mcp.json` | `mcpServers` |
| Claude Code CLI | `~/.claude/mcp.json` | `mcpServers` |
| Cline (VS Code) | `~/.vscode/extensions/saoudrizwan.claude-dev-*/settings/cline_mcp_settings.json` | `mcpServers` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | `mcp_servers` |
| OpenCode | `~/.opencode/mcp.json` or `~/.config/opencode/opencode.jsonc` | `mcpServers` |

**Notes:**
- All tools use the same MCP server command: `aceternity-mcp-server`
- Windsurf uses snake_case (`mcp_servers`) instead of camelCase (`mcpServers`)
- OpenCode supports both user-level and global configuration files
- Cline configuration is managed through VS Code extension settings

## 🔒 Security

- **No secrets in repository**: No API keys, credentials, or sensitive data committed
- **Optional API usage**: Registry sync operations don't require authentication
- **Isolated execution**: pipx provides sandboxed virtual environments
- **Metadata only**: Repository contains component descriptions and metadata, not source code
- **Local configuration**: AI tool configs stored in user's home directory (~/.config/)

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
