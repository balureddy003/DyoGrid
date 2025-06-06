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

### run the frontend
cd frontend
npm run dev

### install mongodb


### install litellm
 litellm --config litellm.config.yaml
