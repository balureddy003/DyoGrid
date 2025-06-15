# MCP Gateway Service

This standalone service exposes enterprise connectors as MCP tools using [mcp-context-forge](https://github.com/IBM/mcp-context-forge).

## Running locally

Provide your SAP and Salesforce endpoints via environment variables and launch the gateway:

```bash
export SAP_BASE_URL="https://sap.example.com/api"
export SALESFORCE_BASE_URL="https://salesforce.example.com/api"
# optional: customise UI login credentials
export BASIC_AUTH_USER=admin
export BASIC_AUTH_PASSWORD=changeme
python main.py
```

The admin UI will be available at `http://localhost:4444/admin`.
