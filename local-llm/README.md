### Local Ollama via LiteLLM

1. Install [Ollama](https://ollama.ai) and make sure `ollama serve` is running.
2. Install LiteLLM with proxy extras:

```bash
pip install 'litellm[proxy]'
```

3. Start the LiteLLM proxy using the provided configuration:

```bash
litellm --config litellm.config.yaml
```

The configuration loads several Ollama models so they are ready for use by the backend.
