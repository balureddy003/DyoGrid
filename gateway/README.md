# MCP Gateway Service

This standalone service exposes enterprise connectors as MCP tools using
[mcp-contextforge-gateway](https://github.com/IBM/mcp-context-forge).

## Running locally

Install [`uv`](https://github.com/astral-sh/uv), create a quick virtual
environment and run the gateway wrapper:

```bash
# 1 · Install uv (provides the `uvenv` helper)
curl -Ls https://astral.sh/uv/install.sh | sh   # or: pipx install uv

# 2 · Create a venv and install the gateway package
uv venv ~/.venv/mcpgateway
source ~/.venv/mcpgateway/bin/activate
uv pip install mcp-contextforge-gateway

export SAP_BASE_URL="https://sap.example.com/api"
export SALESFORCE_BASE_URL="https://salesforce.example.com/api"
export BASIC_AUTH_USER=admin  # optional
export BASIC_AUTH_PASSWORD=changeme
MCP_AUTH_TOKEN=${MCPGATEWAY_BEARER_TOKEN} \
MCP_SERVER_CATALOG_URLS=http://localhost:4444/servers/1 \
uv run --directory . -m mcpgateway.wrapper
```

The admin UI will be available at `http://localhost:4444/admin`.
