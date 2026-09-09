<<<<<<< HEAD
# AI Code Review Bot

An automated bot that reviews GitHub pull requests using an LLM (Google Gemini),
delivered through a multi-service architecture (API + background worker) and a
full CI/CD pipeline: automated tests, security scanning, containerized builds,
staged deployments, a manual approval gate, and automatic rollback.

## How it works

1. A developer opens a pull request on GitHub.
2. GitHub sends a webhook to the FastAPI backend (`api/`), which responds
   immediately and pushes a job onto a Redis queue.
3. A background worker (`worker/`) picks up the job, fetches the PR's real
   code diff from GitHub, and asks Google Gemini to review it.
4. The worker posts the AI's comments back onto the PR and saves the result
   in PostgreSQL.
5. Anyone can check a review's status any time via `GET /reviews/{id}`.

## Local setup

1. Copy `.env.example` to `.env` and fill in:
   - `GOOGLE_API_KEY` -- from Google AI Studio (required)
   - `GITHUB_TOKEN` -- a fine-grained personal access token with
     "Pull requests: Read and write" and "Contents: Read-only" on your
     test repo (required for real GitHub reviews; leave blank to test
     locally against sample code instead)
   - `GITHUB_WEBHOOK_SECRET` -- any random string, used to verify webhooks
     really came from GitHub (leave blank to skip verification locally)
   - `SLACK_WEBHOOK_URL` -- optional, only used by the CI/CD pipeline

2. Start everything:
   ```
   docker-compose up --build
   ```

3. Check it's alive: open `http://localhost:8000/health` -- should show
   `{"status":"ok"}`.

## Connecting a real GitHub repo

1. Run `ngrok http 8000` to expose your local API.
2. In your test repo: Settings > Webhooks > Add webhook.
   - Payload URL: your ngrok URL + `/webhook`
   - Content type: `application/json`
   - Secret: same value as `GITHUB_WEBHOOK_SECRET` in your `.env`
   - Events: just "Pull requests"
3. Open a real PR on that repo and watch the logs.

## Running the tests

```
cd api && pip install -r requirements.txt && pytest tests/ -v
cd worker && pip install -r requirements.txt && pytest tests/ -v
```

Both test suites mock the GitHub and Gemini API calls, so they run fast and
don't need real credentials or network access.

## CI/CD pipeline

See `.github/workflows/ci-cd.yml`. On every push to `main` it runs:

`test` -> `build` (Docker images pushed to GHCR, tagged with commit SHA) ->
`security-scan` (Trivy) -> `deploy-staging` -> `smoke-test` ->
`deploy-production` (behind a manual approval gate) -> `rollback` (only if
production's health check fails) -> `notify` (Slack).

**Before this pipeline can actually deploy anywhere**, you need to:

1. Replace the `TODO` deploy commands in `deploy-staging` and
   `deploy-production` with real commands for your infrastructure (SSH to a
   VM, a cloud provider's CLI, Kubernetes, etc). Free options for staging
   include a free-tier VM (e.g. Oracle Cloud's free tier) or a platform like
   Render or Fly.io's free tier.
2. Replace the placeholder health-check URLs in `smoke-test` and
   `deploy-production` with your real staging/production URLs.
3. In your GitHub repo: Settings > Environments, create `staging` and
   `production` environments. On `production`, add a **required reviewer**
   -- this is what creates the manual approval gate.
4. (Optional) Add a `SLACK_WEBHOOK_URL` repo secret if you want pipeline
   notifications.

## Project structure

```
api/         FastAPI app: webhook receiver, status endpoint
worker/      Celery worker: fetches diffs, calls Gemini, posts comments
.github/workflows/ci-cd.yml   The CI/CD pipeline
docker-compose.yml            Local dev environment (Postgres, Redis, api, worker)
```
=======
# AI-Code-Review-Bot-
An automated AI-powered code review bot that analyzes pull requests via CI/CD
>>>>>>> 93cb40bae025c50a56005ab07c4106b36007ee00
