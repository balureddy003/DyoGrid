---
sidebar_position: 2
title: Quickstart
---

# Quickstart

## Prerequisites

- Python 3.10 or higher
- Docker (optional for local LLMs)
- Node.js (optional for the low-code canvas)

## Installation

```bash
git clone https://github.com/dyogrid/dyogrid.git
cd dyogrid
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Backend

```bash
uv venv
source .venv/bin/activate
uv sync
playwright install --with-deps chromium
uvicorn main:app --reload
```

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

This will start the development server at `http://localhost:3000`.
