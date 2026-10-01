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

For a fully local model run, pull the Ollama models and leave the provider settings blank:

```bash
ollama pull llama3.2
ollama pull qwen2.5vl
ollama pull x/flux2-klein:4b
```

`docker compose up` uses those local defaults and stores data in a volume. For Postgres and S3-compatible storage, start the hosted profile and point the backend at it:

```bash
DATABASE_URL=postgresql+psycopg://thumbnail:thumbnail@postgres:5432/thumbnail \
STORAGE_BACKEND=s3 S3_BUCKET=thumbnails S3_ENDPOINT_URL=http://minio:9000 \
AWS_ACCESS_KEY_ID=thumbnail AWS_SECRET_ACCESS_KEY=thumbnail-secret \
docker compose --profile hosted up
```

Create the `thumbnails` bucket in MinIO before the first render. Set `AUTH_TOKEN` when the API is reachable by anyone other than you. Send it as `Authorization: Bearer <token>`. Teammates are added with `POST /api/team/members`.

Copy `.env.example` to `backend/.env`. The studio runs three kinds of agent, each with its own provider:

| Role | Agents | Setting |
|---|---|---|
| Chat | video analyst, audience analyst, researcher, reference analyst, hook strategist, creative director, visual director | `CHAT_PROVIDER` |
| Judge | critic: runs pixel checks, then a vision model scores the rendered thumbnail | `JUDGE_PROVIDER` |
| Image | renders the background | `IMAGE_PROVIDER` |

Set `YOUTUBE_API_KEY` to let the researcher save popular thumbnails for the same game or live stream. Player photos come from frames of the linked video. The game page comes from Wikipedia.

`APP_ENV` decides where they run. Users don't choose.

- **Development** (default): everything stays local. Chat uses `OLLAMA_CHAT_MODEL`, the judge uses the vision model `OLLAMA_JUDGE_MODEL` (run `ollama pull qwen2.5vl`), and images come from the offline compositor. If a provider fails, chat falls back to the studio engine and the judge to the pixel checks. You can point any role at `openai` or `bedrock` to try a hosted model.
- **Production**: set `CHAT_PROVIDER`, `JUDGE_PROVIDER`, and `IMAGE_PROVIDER` to `openai` or `bedrock`. The server refuses to start if any is missing or its credentials aren't configured, and failures are reported instead of falling back. Images default to high quality (`gpt-image-2` at `high`, or Stable Image Ultra).

Bedrock uses the standard AWS credential chain (profile, environment variables, or IAM role). Set `AWS_REGION` and `BEDROCK_CHAT_MODEL` to a model or inference profile ID enabled in your account. The judge uses `BEDROCK_JUDGE_MODEL`, or the chat model if that's blank; it must accept images.

## Tests

```bash
cd backend && .venv/bin/pytest
```
