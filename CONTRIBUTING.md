# Contributing

Thanks for contributing to Aceternity MCP.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Local workflow

1. Sync registry data:

```bash
python scripts/sync_registry.py
```

2. Validate code and registry:

```bash
python -m compileall src scripts
python scripts/validate_registry.py
```

3. Run the server:

```bash
aceternity-mcp
```

## Contribution guidelines

- Keep component metadata factual and actionable.
- Preserve `detailedDescription` minimum quality (60+ words).
- Do not commit API keys, auth headers, or credentials.
- Keep tools MCP-compliant and schema-driven.

## Pull requests

- Include a concise description of what changed and why.
- Include validation output if registry data was updated.
- Keep commits focused and reviewable.
