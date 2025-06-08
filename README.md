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

Run the LiteLLM proxy pointing to your local Ollama service:

```bash
litellm --config local-llm/litellm.config.yaml
```

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
Use `RAG_BACKEND=azure` to leverage Azure Cognitive Search or `RAG_BACKEND=faiss`
for a local FAISS index.

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


## 🤝 Contributing

We welcome contributions from the community! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our process and guidelines.


### Use local Ollama with LiteLLM

1. Start the Ollama service (models should be pulled first):

```bash
ollama serve &
```

2. Launch the LiteLLM proxy so the backend can access the models via an OpenAI-compatible API:

```bash
litellm --config local-llm/litellm.config.yaml
```

3. Set environment variables to enable Ollama in the backend:

```bash
export LLM_PROVIDER=ollama
export LITELLM_BASE_URL=http://localhost:4000/v1
```

Optionally adjust `AGENT_MODEL_MAP` to choose which model each agent uses.
