# aceternity-mcp

**npm wrapper for the Aceternity MCP server.**

This is a thin Node.js wrapper around the Python `aceternity-mcp` package. It enables usage via `npx`:

```bash
npx aceternity-mcp
```

## Prerequisites

The Python backend must be installed separately:

```bash
# Recommended
pipx install aceternity-mcp

# Or with uv
uv tool install aceternity-mcp

# Or with pip
pip install aceternity-mcp
```

## Usage

After installing the Python backend:

```bash
# Run the MCP server
npx aceternity-mcp-server
```

## Full Documentation

See the [main repository](https://github.com/devinoldenburg/aceternity-mcp) for complete documentation.
