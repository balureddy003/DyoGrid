# 🧠 DyoGrid

**DyoGrid** is an open-source, modular platform for orchestrating teams of intelligent agents powered by LLMs. Build agent-based workflows that integrate with your existing systems like ERPs, CRMs, databases, and IoT platforms—with full governance, observability, and extensibility.

---

## 🚨 The Problem

Modern organizations face:

- 🌀 **Shadow AI**: Isolated LangChain/RAG experiments across teams create duplication and security gaps.
- 🔌 **Integration Pain**: Connecting LLMs to enterprise systems (e.g., SAP, Salesforce, Kafka) takes weeks of brittle code.
- 🔒 **Vendor Lock-In**: Proprietary AI platforms limit flexibility and control.
- ❌ **No Observability**: Poor insight into agent behavior, cost, and outcome quality.

---

## ✅ The DyoGrid Solution

DyoGrid is your platform to build AI-powered "dream teams" of agents—just like remote workers—with distinct roles, responsibilities, and skills. Each agent can reason, act, and collaborate with others to accomplish your business goals, automate workflows, and integrate with your real systems.

**How It Works:**

- **🤖 Agent Fabric** – Assemble agents like you build a team—strategist, researcher, analyst, operator. Each agent has defined tools, memory, and decision autonomy.
- **🔁 Team Orchestrator** – Coordinate how agents talk, collaborate, and share work. Define workflows as conversations, chains, or parallel task DAGs—with fail-safes and cost rules.
- **🔌 Integration Mesh** – Plug agents into your business stack: REST APIs, databases, Kafka pipelines, ERPs (SAP, Salesforce), RPA bots, OPC-UA sensors, and more.
- **🛡️ Governance Layer** – Track what agents do, how much they cost, and who can run what. Includes RBAC, audit trails, and OpenTelemetry-based tracing.
- **🛠️ UX Surfaces for Every User** – Visual canvas (React) for citizen developers to compose teams, and Python SDK / CLI for developers to script advanced workflows.

**Example:**

Want a team that reads orders from SAP, checks inventory in MongoDB, and emails suppliers when stock is low? Just spin up `PlannerAgent`, `InventoryAgent`, and `VendorCommsAgent`—connect them to your systems, define the goal, and let them get to work.

This makes DyoGrid more than just an agent framework—it's a business-aware operating layer where intelligent, modular agents work together like digital coworkers, helping you scale human effort with precision and control.

---

## 🔍 Use Cases

| Use Case                     | Description                                               |
|-----------------------------|-----------------------------------------------------------|
| Autonomous Support Agents   | Integrate with Zendesk, Salesforce, or Freshdesk          |
| Finance Ops Automation      | Query ERP, reconcile reports, generate insights           |
| Smart Factory Agents        | Analyze IoT logs via OPC-UA + LLM for diagnostics         |
| R&D Workflows               | Agents collaborating on patent research or document review|
| Compliance Audits           | Validate controls by querying internal logs and systems   |

---

## 🌍 Industries Supported

- 🏢 **Enterprise SaaS / IT**
- 🏭 **Manufacturing / IIoT**
- 🧾 **Finance & Accounting**
- 🚚 **Logistics & Supply Chain**
- 📞 **Customer Support / BPO**
- 🧠 **Research & Knowledge Work**

---

## ⚙️ Quickstart

### 🔧 Prerequisites

- Python 3.10+
- Docker (for optional local LLMs)
- Node.js (for low-code canvas, optional)

### 🚀 Installation

```bash
git clone https://github.com/dyogrid/dyogrid.git
cd dyogrid
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt



### setup ollama

###
litellm --config litellm.config.json

### setup mongodb

### run the backend
Set up a virtual environment (Preferred)
uv venv
source .venv/bin/activate

uv sync
playwright install --with-deps chromium

uvicorn main:app --reload

To see detailed agent logs during development, set `DEBUG_AGENT_LOGS=true` in
your `.env` file before starting the backend.
Set `RAG_BACKEND=faiss` to build and query a local FAISS index.

### run the frontend
cd frontend
npm run dev

### install mongodb


### install litellm
uv venv
pip install litellm
pip install 'litellm[proxy]'
 litellm --config litellm.config.yaml

Set the `AGENT_MODEL_MAP` environment variable to map agent names to specific models.  
Agent names are matched case-insensitively.
You can always enable function-calling support for custom models by setting `LITELLM_ALWAYS_ENABLE_TOOLS=true`.
Example:

```bash
export AGENT_MODEL_MAP="Coder:ollama/deepseek-coder:6.7b,WebSurfer:ollama/llama3.1"
export LITELLM_ALWAYS_ENABLE_TOOLS=true
```

## MCP Gateway Integration

The repository includes a helper script using
[mcp-context-forge](https://github.com/IBM/mcp-context-forge) to expose
enterprise systems as MCP tools. Provide your SAP and Salesforce endpoints
via environment variables. The backend automatically mounts the gateway under
`/mcp` when it starts, so no extra process is required:

```bash
export SAP_BASE_URL="https://sap.example.com/api"
export SALESFORCE_BASE_URL="https://salesforce.example.com/api"
export BASIC_AUTH_USER=admin
export BASIC_AUTH_PASSWORD=changeme
uvicorn backend.main:app --reload
```

Agents can now invoke `sap_api` or `salesforce_api` through this gateway. Open
`http://localhost:8000/mcp/admin` to manage connectors using the MCP Gateway UI
404 page. If you accidentally browse to `/mcp/mcp-admin` or `/mcp/-admin`,
you'll be redirected back to the correct location as well. If you prefer a
separate process, run
`npm run dev`, Vite proxies any `/mcp` requests to this URL while leaving the
`/mcp-admin` path untouched, so keep the `/mcp` prefix in place.
The frontend expects a `VITE_MCP_GATEWAY_URL` environment variable (see
`frontend/.env.example`) pointing at your gateway instance, typically
`http://localhost:8000/mcp` when running the backend locally.


## 🤝 Contributing

We welcome contributions from the community! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our process and guidelines.

