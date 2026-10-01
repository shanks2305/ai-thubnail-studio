# Thumbnail Suite

Local studio that turns a video description into YouTube thumbnail concepts, then a 1280×720 frame you can edit and export.

## Run it

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

Without an API key, concepts come from the local studio engine and thumbnails are composed on this machine. To use a language model:

- Set `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`, `OPENAI_IMAGE_MODEL`), or
- Run Ollama and set `OLLAMA_MODEL`

Copy `.env.example` to `backend/.env`. `LLM_MODE=auto` uses OpenAI for Hybrid and Cloud projects, Ollama or the studio engine for Local projects.

Cloud privacy mode refuses to start unless an OpenAI key is set.

## Tests

```bash
cd backend && .venv/bin/pytest
```
