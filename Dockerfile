FROM python:3.12-slim AS builder

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir build && python -m build --wheel

FROM python:3.12-slim

LABEL org.opencontainers.image.title="aceternity-mcp"
LABEL org.opencontainers.image.description="MCP server for Aceternity UI components"
LABEL org.opencontainers.image.source="https://github.com/devinoldenburg/aceternity-mcp"
LABEL org.opencontainers.image.url="https://github.com/devinoldenburg/aceternity-mcp"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Devin Oldenburg"

COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# MCP server runs on stdio
ENTRYPOINT ["aceternity-mcp-server"]
