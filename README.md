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

Copy `.env.example` to `backend/.env`. The studio runs three kinds of agent, each with its own provider:

| Role | Agents | Setting |
|---|---|---|
| Chat | video analyst, reference analyst, hook strategist, creative director, visual director | `CHAT_PROVIDER` |
| Judge | critic: runs pixel checks, then a vision model scores the rendered thumbnail | `JUDGE_PROVIDER` |
| Image | renders the background | `IMAGE_PROVIDER` |

`APP_ENV` decides where they run. Users don't choose.

- **Development** (default): everything stays local. Chat uses `OLLAMA_CHAT_MODEL`, the judge uses the vision model `OLLAMA_JUDGE_MODEL` (run `ollama pull qwen2.5vl`), and images come from the offline compositor. If a provider fails, chat falls back to the studio engine and the judge to the pixel checks. You can point any role at `openai` or `bedrock` to try a hosted model.
- **Production**: set `CHAT_PROVIDER`, `JUDGE_PROVIDER`, and `IMAGE_PROVIDER` to `openai` or `bedrock`. The server refuses to start if any is missing or its credentials aren't configured, and failures are reported instead of falling back. Images default to high quality (`gpt-image-2` at `high`, or Stable Image Ultra).

Bedrock uses the standard AWS credential chain (profile, environment variables, or IAM role). Set `AWS_REGION` and `BEDROCK_CHAT_MODEL` to a model or inference profile ID enabled in your account. The judge uses `BEDROCK_JUDGE_MODEL`, or the chat model if that's blank; it must accept images.

## Tests

```bash
cd backend && .venv/bin/pytest
```
