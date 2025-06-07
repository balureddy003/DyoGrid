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

### documentation
The documentation website uses [Docusaurus](https://docusaurus.io).

To start a local docs server:
```bash
cd website
npm install
npm run start
```

To build the static site:
```bash
npm run build
```
