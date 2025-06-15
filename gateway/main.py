"""Example MCP Gateway setup with SAP and Salesforce connectors.

This file shows how to programmatically register connectors using the
``mcp-contextforge-gateway`` package. In most cases you should install the
package with ``uv`` and run ``mcpgateway.wrapper`` (see ``gateway/README.md``).
Running this module directly will also start the gateway with its admin UI at
``http://localhost:4444/admin``.
"""

import os
import asyncio
from mcpgateway.main import app
from mcpgateway.db import Base, SessionLocal, engine
from mcpgateway.services.tool_service import ToolService
from mcpgateway.schemas import ToolCreate

# Environment variable names
SAP_URL = "SAP_BASE_URL"
SALESFORCE_URL = "SALESFORCE_BASE_URL"

async def register_connectors():
    """Register example connectors using mcpgateway."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    tool_service = ToolService()
    await tool_service.initialize()

    sap_endpoint = os.getenv(SAP_URL)
    if sap_endpoint:
        tool = ToolCreate(
            name="sap_api",
            url=sap_endpoint,
            description="SAP REST connector",
            integration_type="REST",
            request_type="POST",
        )
        await tool_service.register_tool(db, tool)

    sf_endpoint = os.getenv(SALESFORCE_URL)
    if sf_endpoint:
        tool = ToolCreate(
            name="salesforce_api",
            url=sf_endpoint,
            description="Salesforce REST connector",
            integration_type="REST",
            request_type="POST",
        )
        await tool_service.register_tool(db, tool)

    await tool_service.shutdown()
    db.close()

if __name__ == "__main__":
    asyncio.run(register_connectors())
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=4444)

