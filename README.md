<div align="center">

# Aceternity MCP

**A structured MCP registry and integration server for Aceternity UI.**

It helps AI agents discover, understand, recommend, and install Aceternity UI components with rich metadata instead of only raw component names.

[![PyPI - Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compliant-1f6feb)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/github/license/devinoldenburg/aceternity-mcp)](./LICENSE)
[![Repo Stars](https://img.shields.io/github/stars/devinoldenburg/aceternity-mcp?style=social)](https://github.com/devinoldenburg/aceternity-mcp)

</div>

## Why this exists

Aceternity UI has a large and visually rich catalog. Component names alone are not enough for an agent to make correct UX decisions.

This server adds a structured local knowledge layer so agents can answer:

- Which component actually fits this use case?
- Is it decorative or layout-critical?
- Is it subtle or visually dominant?
- What is the exact install command?
- What should it be combined with?

## What this MCP server provides

- Full local normalized registry (`registry/components/*.json`) for CLI-discoverable Aceternity components.
- Minimum 60-word `detailedDescription` for every component.
- Metadata fields designed for agent reasoning:
  - `purpose`, `behavior`, `visualCharacteristics`
  - `difficulty`, `designTone`, `layoutRole`, `recommendations`
  - `compatibility`, `dependencies`, install/docs URLs
  - score dimensions: `visualIntensity`, `animationIntensity`, `layoutImportance`, `customizationEase`, `landingPageFit`, `dashboardFit`, `performanceImpact`
- MCP tools for listing, searching, filtering, recommendation, project matching, and install workflows.
- Sync script that refreshes the local registry from `@aceternity` via shadcn CLI.

## Architecture

### 1) Raw Source Layer

`registry/raw/components.json`

- Stores discovered factual metadata (slug, name, install command, docs URL, registry URL, dependencies).
- Discovery source is `npx shadcn@latest list @aceternity`.
- **No component source files are stored.**

### 2) Enriched Metadata Layer

`registry/components/*.json`

- Stores rich static AI-facing metadata.
- Includes long descriptions and recommendation-oriented scoring.

### 3) Runtime MCP Layer

`src/aceternity_mcp/server.py`

- Serves the enriched local registry through MCP tools.
- No runtime scraping required for normal query paths.

## Tools exposed

- `list_components`
- `list_categories`
- `search_components`
- `get_component`
- `get_category`
- `recommend_components`
- `recommend_combination`
- `match_components_to_project`
- `install_component`
- `filter_by_scores`

## Quick start

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2) Build/update the local registry

```bash
python scripts/sync_registry.py
```

Optional:

```bash
python scripts/sync_registry.py --api-key "$ACETERNITY_API_KEY"
```

The key is optional and is not persisted.

### 3) Run the MCP server

```bash
aceternity-mcp
```

## MCP client config example

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

## Example prompts for agents

- "Show me subtle dark background effects with low performance impact."
- "Recommend a navbar + hero + CTA combination for a premium AI SaaS landing page."
- "Find highly customizable card components for testimonials."
- "Give me low-motion components suitable for a dashboard."
- "Install Spotlight and show required dependencies."

## Project structure

```text
registry/
  index.json
  raw/
    components.json
  components/
    *.json
  categories/
    *.json
scripts/
  sync_registry.py
  validate_registry.py
src/aceternity_mcp/
  models.py
  registry.py
  search.py
  recommender.py
  server.py
```

## Development

Validate code and registry quality:

```bash
python -m compileall src scripts
python scripts/validate_registry.py
```

## Open-source friendliness

- Clear architecture split (raw / enriched / runtime).
- Reproducible sync script.
- Validation script for schema/quality checks.
- Community files included: contributing guide, code of conduct, security policy.

## Security note

- Do not commit secrets.
- API keys are optional for sync workflows.
- This repository intentionally stores metadata descriptions, not upstream component source files.

## License

MIT - see `LICENSE`.
