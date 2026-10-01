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

Copy `.env.example` to `backend/.env`. `APP_ENV` picks the providers:

- **Development** (default): concepts come from Ollama (`TEXT_PROVIDER=ollama`). Ollama can't generate images, so thumbnails use the cheapest hosted tier when a key is set (`gpt-image-2` at `low` quality, or Stable Image Core on Bedrock with `IMAGE_PROVIDER=bedrock`) and the offline compositor otherwise.
- **Production**: set `TEXT_PROVIDER` and `IMAGE_PROVIDER` to `openai` or `bedrock`. The server refuses to start if either is missing or its credentials aren't configured. Images default to high quality (`gpt-image-2` at `high`, or Stable Image Ultra).

Bedrock uses the standard AWS credential chain (profile, environment variables, or IAM role). Set `BEDROCK_TEXT_MODEL` to a model or inference profile ID enabled in your account and `AWS_REGION`.

Each project's privacy mode still limits where its data goes:

- **Local**: never sent to a hosted model. Concepts use Ollama or the studio engine; thumbnails use the compositor.
- **Hybrid**: uses the configured providers and falls back to the local engine and compositor if one fails.
- **Cloud**: uses the configured providers and reports an error instead of falling back.

## Tests

```bash
cd backend && .venv/bin/pytest
```
