# AutoGen accelerator

## Running locally

1. **Start LiteLLM** using the provided configuration:

   ```bash
   cd ../local-llm
   litellm --config litellm.config.yaml
   ```

   This exposes an OpenAI-compatible endpoint at `http://localhost:4000/v1`.

2. **Launch the MCP server** in stdio mode:

   ```bash
   cd ../mcp
   uv venv
   uv sync
   python mcp_general_server.py
   ```

3. **Run the backend** with environment variables pointing to the local MCP server:

   ```bash
   export MCP_SERVER_MODE=stdio
   export MCP_SERVER_URI=http://localhost:8333
   uvicorn main:app --reload
   ```

   Leaving `MCP_SERVER_MODE` unset retains the default SSE-based connection.

