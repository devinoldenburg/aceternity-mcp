<div align="center">
  
# Aceternity MCP

**Model Context Protocol server for Aceternity UI components**

Discover, search, and install 106 Aceternity UI components from your AI assistant. Generate full page layouts, get context-aware recommendations, and install everything with a single command.

[![PyPI](https://img.shields.io/pypi/v/aceternity-mcp.svg)](https://pypi.org/project/aceternity-mcp/)
[![npm](https://img.shields.io/npm/v/aceternity-mcp.svg)](https://www.npmjs.com/package/aceternity-mcp)
[![Python](https://img.shields.io/pypi/pyversions/aceternity-mcp.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compliant-1f6feb)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/github/license/devinoldenburg/aceternity-mcp)](./LICENSE)
[![Tests](https://img.shields.io/badge/tests-172%20passed-brightgreen)]()

</div>

---

## Install

```bash
pipx install aceternity-mcp
aceternity-mcp install
```

Restart your AI tool. Done.

## What It Does

Your AI assistant gets 11 tools for working with Aceternity UI:

| Tool | What it does |
|------|-------------|
| `generate_page_layout` | Generate a full page layout with sections, components, and install commands |
| `search_components` | Full-text search across names, descriptions, tags, categories |
| `recommend_components` | Get recommendations for a use case or design goal |
| `recommend_combination` | Get component suggestions for each page section |
| `match_components_to_project` | Match components to a whole project description |
| `list_components` | List all 106 components with optional filters |
| `list_categories` | Show all 17 categories with component counts |
| `get_component` | Get full metadata for a single component |
| `get_category` | Get all components in a category |
| `install_component` | Get install command, dependencies, and setup steps |
| `filter_by_scores` | Filter by visual intensity, animation, performance, etc. |

## Page Layout Generator

The standout feature. Ask your AI to generate a complete page layout and it returns:

- Ordered sections with recommended components for each role
- Design tone detection (dark, premium, modern, minimal, etc.)
- Section-specific scoring using 17 role profiles
- De-duplicated components across sections
- Implementation notes for every section
- Batch install command for all components at once
- Performance estimate and dependency summary

**7 page types:** landing, saas, dashboard, portfolio, ecommerce, blog, documentation

**Example prompts:**

```
"Generate a page layout for a dark premium AI SaaS landing page"
"Build me a fintech dashboard layout with analytics"
"Create a portfolio page with 3D effects and scroll animations"
"Design an e-commerce store layout for a clothing brand"
```

**Scoring signals per component:**

| Signal | Description |
|---|---|
| Section-role category match | 17 role profiles with preferred categories |
| Section-role tag match | Role-specific tag boosting |
| Section score weights | Tuned dimension weights per role |
| Archetype context | Page-level scoring (SaaS, dashboard, portfolio, etc.) |
| Text relevance | User description keyword matching |
| Design tone coherence | Boosts components matching detected tones |
| Dependency reuse | Bonus for shared npm dependencies |

## Example Prompts

```
"Show me subtle dark background effects with low performance impact"
"Recommend a navbar + hero + CTA combination for a SaaS landing page"
"Find highly customizable card components for testimonials"
"Give me low-motion components suitable for a dashboard"
"Install Spotlight and show me what dependencies are needed"
"What components work well for dark mode dashboards?"
"Search for animated text effects"
"Filter components with visual intensity above 7 and low performance impact"
```

## Supported AI Tools

| Tool | Auto-configured |
|------|----------------|
| Claude Desktop | Yes |
| Claude Code CLI | Yes |
| Cursor | Yes |
| Cline (VS Code) | Yes |
| Windsurf | Yes |
| OpenCode | Yes |

Run `aceternity-mcp install` and all detected tools are configured automatically.

### Manual Configuration

All tools use the same server command:

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

| Tool | Config file |
|------|------------|
| Cursor | `~/.cursor/mcp.json` |
| Claude Code | `~/.claude/mcp.json` |
| Cline | VS Code extension settings |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` (uses `mcp_servers` / `aceternity_ui`) |
| OpenCode | `~/.opencode/mcp.json` |

## CLI Commands

| Command | Description |
|---------|-------------|
| `aceternity-mcp install` | Interactive setup wizard |
| `aceternity-mcp status` | Show installation health |
| `aceternity-mcp update` | Check for and install updates |
| `aceternity-mcp repair` | Fix registry, configs, or permissions |
| `aceternity-mcp diagnose` | Output JSON diagnostics |
| `aceternity-mcp uninstall` | Remove from all AI tools |
| `aceternity-mcp --version` | Show version |

```bash
# Repair only the registry
aceternity-mcp repair --registry

# Repair only client configs
aceternity-mcp repair --configs

# Non-interactive update
aceternity-mcp update -y
```

## Alternative Install Methods

### Docker

```bash
docker pull ghcr.io/devinoldenburg/aceternity-mcp
docker run -i ghcr.io/devinoldenburg/aceternity-mcp
```

### npm (wrapper)

```bash
npx aceternity-mcp-server
```

Requires the Python package installed separately (`pipx install aceternity-mcp`).

### pip

```bash
pip install aceternity-mcp
```

### From source

```bash
git clone https://github.com/devinoldenburg/aceternity-mcp.git
cd aceternity-mcp
pipx install .
```

## Component Registry

106 components across 17 categories:

| Category | Count | Examples |
|----------|-------|---------|
| Backgrounds | 18 | Aurora, Beams, Grid, Spotlight, Vortex |
| Cards | 15 | 3D Card, Card Hover, Expandable Card |
| Text Effects | 13 | Typewriter, Text Generate, Gradient Text |
| Scroll Effects | 11 | Parallax, Scroll Reveal, Tracing Beam |
| Visualization | 9 | Globe, World Map, SVG Mask |
| Hero Sections | 8 | Hero Parallax, Spotlight, Lamp Effect |
| Navigation | 7 | Floating Dock, Navbar Menu |
| Layout | 81 | Bento Grid, Container Scroll, Timeline |
| Forms | 6 | Input, Placeholders, Multi-Step |
| 3D Effects | 5 | 3D Card, 3D Pin, Globe |

Each component includes: detailed description, purpose, behavior, visual characteristics, design tone, difficulty level, dependencies, install command, compatibility flags, and 7 scoring dimensions.

## Scoring Dimensions

Every component is rated 1-10 on:

| Dimension | What it measures |
|-----------|-----------------|
| Visual Intensity | How visually dominant (1 = subtle, 10 = dramatic) |
| Animation Intensity | Amount of motion (1 = static, 10 = heavy animation) |
| Layout Importance | Structural criticality (1 = decorative, 10 = essential) |
| Customization Ease | Flexibility (1 = rigid, 10 = very configurable) |
| Landing Page Fit | Suitability for landing pages |
| Dashboard Fit | Suitability for dashboards |
| Performance Impact | Runtime cost (1 = lightweight, 10 = heavy) |

## Development

```bash
git clone https://github.com/devinoldenburg/aceternity-mcp.git
cd aceternity-mcp
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint + type check
ruff check src/ tests/
mypy src/aceternity_mcp/ tests/

# Validate registry
python scripts/validate_registry.py
```

### Quality

- 172 tests, 9 archetypes, 17 section role profiles, 7 page templates
- ruff lint + format, mypy strict, bandit security scan
- CI: quality gates on every push, auto-publish on release

## Security

- **Metadata only**: No Aceternity source code, documentation, or images in this repository
- **No secrets**: No API keys or credentials
- **Isolated**: pipx provides sandboxed virtual environments
- **Install commands**: Point to Aceternity's official `@aceternity` shadcn registry

## Troubleshooting

**Command not found** -- Run `pipx ensurepath` and restart your terminal.

**Registry not found** -- Run `aceternity-mcp repair` or `pipx reinstall aceternity-mcp`.

**MCP server not connecting** -- Run `aceternity-mcp diagnose` and check the output. Repair configs with `aceternity-mcp repair --configs`.

**Update issues** -- Run `pipx upgrade aceternity-mcp` or `pipx reinstall aceternity-mcp`.

## License

MIT -- see [LICENSE](./LICENSE).

## Links

- [PyPI](https://pypi.org/project/aceternity-mcp/)
- [npm](https://www.npmjs.com/package/aceternity-mcp)
- [Docker (ghcr.io)](https://github.com/devinoldenburg/aceternity-mcp/pkgs/container/aceternity-mcp)
- [GitHub](https://github.com/devinoldenburg/aceternity-mcp)
- [Issues](https://github.com/devinoldenburg/aceternity-mcp/issues)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Aceternity UI](https://ui.aceternity.com/)
