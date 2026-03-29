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

Aceternity MCP is a Model Context Protocol server that brings the entire Aceternity UI component library to your AI assistant. Instead of just knowing component names, your AI gets rich metadata including:

- **Detailed descriptions** (60+ words per component)
- **Visual characteristics** and behavior patterns
- **Use case recommendations** and compatibility info
- **Installation commands** and dependencies
- **Scoring metrics** for animation, customization, performance impact

This helps your AI make informed decisions about which components fit your design needs.

## Features

- **Complete Registry**: Access to 100+ Aceternity UI components with full metadata
- **Intelligent Search**: Filter by category, visual intensity, animation level, use case
- **Smart Recommendations**: Get component suggestions based on your project type
- **Combination Planning**: Recommend complementary components (navbar + hero + CTA)
- **One-Command Install**: Install components directly through your AI assistant
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **Universal Support**: Configures Cursor, Claude Desktop, Claude Code, Cline, Windsurf, OpenCode

## Quick Start

### Install from PyPI (Recommended)

```bash
# Install the package
pip install aceternity-mcp

# Run the universal installer (interactive)
aceternity-mcp-install

# Or configure all tools automatically
aceternity-mcp-install --non-interactive
```

**What the installer does:**
1. Syncs 100+ components from Aceternity UI
2. Configures your AI tools automatically
3. Verifies the installation
4. Shows you next steps

### Development Installation

```bash
# Clone the repository
git clone https://github.com/devinoldenburg/aceternity-mcp.git
cd aceternity-mcp

# Install in development mode
pip install -e .

# Sync the component registry
python scripts/sync_registry.py

# Configure your AI tools
python -m aceternity_mcp.install
```

### Manual Configuration

Add to your AI tool's MCP configuration:

**Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "aceternity-ui": {
      "command": "aceternity-mcp",
      "args": [],
      "cwd": "/absolute/path/to/aceternity-mcp"
    }
  }
}
```

**Claude Code** (`~/.claude/mcp.json`):
```json
{
  "mcpServers": {
    "aceternity-ui": {
      "command": "aceternity-mcp",
      "args": [],
      "cwd": "/absolute/path/to/aceternity-mcp"
    }
  }
}
```

**Cline** (VS Code extension settings):
```json
{
  "mcpServers": {
    "aceternity-ui": {
      "command": "aceternity-mcp",
      "args": [],
      "cwd": "/absolute/path/to/aceternity-mcp"
    }
  }
}
```

**Windsurf** (`~/.codeium/windsurf/mcp_config.json`):
```json
{
  "mcp_servers": {
    "aceternity_ui": {
      "command": "aceternity-mcp",
      "args": [],
      "cwd": "/absolute/path/to/aceternity-mcp"
    }
  }
}
```

**OpenCode** (`~/.opencode/mcp.json`):
```json
{
  "mcpServers": {
    "aceternity-ui": {
      "command": "aceternity-mcp",
      "args": [],
      "cwd": "/absolute/path/to/aceternity-mcp"
    }
  }
}
```

## Available Tools

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

## Example Prompts

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

## Architecture

```
aceternity-mcp/
├── registry/              # Component metadata registry
│   ├── index.json        # Master index
│   ├── raw/              # Raw data from Aceternity UI
│   ├── components/       # Enriched component metadata
│   └── categories/       # Category definitions
├── scripts/              # Utility scripts
│   ├── sync_registry.py  # Sync from Aceternity UI
│   └── validate_registry.py
├── src/aceternity_mcp/   # MCP server source
│   ├── server.py         # MCP server implementation
│   ├── install.py        # Universal installer
│   ├── models.py         # Data models
│   ├── registry.py       # Registry loader
│   ├── search.py         # Search functionality
│   └── recommender.py    # Recommendation engine
└── pyproject.toml        # Package configuration
```

## Development

### Validate Registry Quality

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
```

## Supported AI Tools

| Tool | Config File | Status |
|------|-------------|--------|
| Cursor | `~/.cursor/mcp.json` | ✅ Supported |
| Claude Desktop | Platform-specific | ✅ Supported |
| Claude Code | `~/.claude/mcp.json` | ✅ Supported |
| Cline | VS Code extension | ✅ Supported |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | ✅ Supported |
| OpenCode | `~/.opencode/mcp.json` | ✅ Supported |

## Requirements

- **Python**: 3.10 or higher
- **Node.js**: Required for registry sync (npx command)
- **MCP Client**: One of the supported AI tools listed above

## Security

- No secrets are committed to the repository
- API keys are optional and used only during sync operations
- Keys are not stored on disk
- The repository stores metadata descriptions, not component source files

## Contributing

Contributions are welcome! Please see:
- [Contributing Guide](./CONTRIBUTING.md)
- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Security Policy](./SECURITY.md)

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Links

- [PyPI Package](https://pypi.org/project/aceternity-mcp/)
- [GitHub Repository](https://github.com/devinoldenburg/aceternity-mcp)
- [Issue Tracker](https://github.com/devinoldenburg/aceternity-mcp/issues)
- [Model Context Protocol](https://modelcontextprotocol.io/)
