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

DyoGrid solves these challenges by providing:

- **Agent Fabric** – Pluggable LLM agent modules compatible with Autogen-style interactions and LiteLLM backends (OpenAI, Azure, Ollama, Claude, etc.)
- **Team Orchestrator** – DAG-style agent coordination with retry logic, stop rules, and budget caps.
- **Integration Mesh** – Prebuilt connectors and SDKs for REST, DBs, Kafka, RPA, OPC-UA, and more.
- **Governance Layer** – RBAC, telemetry (OpenTelemetry), cost metering, and traceability.
- **Developer UX** – Use the low-code canvas for visual flows or the Python SDK / CLI for advanced scripting.

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

### run the frontend
cd frontend
npm run dev

### install mongodb


### install litellm
uv venv
pip install litellm
pip install 'litellm[proxy]'
 litellm --config litellm.config.yaml

 ### install mcpserver
