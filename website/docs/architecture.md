---
sidebar_position: 3
title: Architecture
---

# Architecture Overview

DyoGrid is organized into several components. The repository contains a Python backend, a React-based frontend and optional agent controller services.

## Backend

The backend provides FastAPI endpoints and utilities for orchestrating agents.

- `main.py` – FastAPI application with endpoints for chat and file uploads.
- `magentic_one_custom_agent.py` – example of a custom agent implementation.
- `orchestration_utils.py` – helper class for stopping agent loops when tasks are done.
- `llm_config.py` – reads environment variables to configure the local Ollama LLM provider.

## Frontend

The frontend is built with React, Vite and Tailwind CSS. It offers a chat interface and agent management UI.

- To develop locally, run `npm install` and `npm run dev` inside `frontend/`.
- The build output can be deployed to any static hosting solution.

## MCP Server

The `mcp/` directory contains an example remote MCP server using FastAPI and SSE transport. It can be run with `uv run fastapi dev main.py`.

## MCP Gateway

DyoGrid also ships a lightweight integration with
[mcp-context-forge](https://github.com/IBM/mcp-context-forge). The helper
script at `backend/connectors/mcp_gateway.py` registers REST connectors for
SAP and Salesforce based on environment variables. The backend mounts the
resulting MCP Gateway under `/mcp`, so its admin UI is reachable at
`http://localhost:8000/mcp/admin` and also via `/mcp-admin` when running the
frontend locally. All `/admin` or `/mcp-admin` paths are redirected to
`/mcp/admin` so the UI works even when users enter the wrong URL.
