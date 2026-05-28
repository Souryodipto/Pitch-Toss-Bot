# Pitch & Toss AI

Fully automated AI-powered Telegram cricket analytics bot for toss prediction posts, result tracking, graphics, and 24/7 scheduled publishing.

The system runs without Telegram user commands. It scans cricket fixtures, creates probability-calibrated predictions, generates black/gold sports graphics, publishes to a Telegram channel, checks toss results, updates accuracy, and posts engagement/VIP teaser content automatically.

## Features

- Auto-fetch upcoming cricket matches every 15 minutes.
- Cricbuzz and ESPN Cricinfo scraping with resilient parsing.
- Extracts teams, venue, league/format, weather placeholders, day/night profile, and raw source text.
- Logistic Regression, Random Forest, Gradient Boosting, and weighted statistical scoring ensemble.
- Confidence is intentionally calibrated to realistic ranges, usually 50% to 65%.
- Telegram channel publishing with Markdown, photos, optional pinning, edits/deletes, and scheduled posts.
- Prediction cards and streak cards generated with Pillow.
- SQLite by default, PostgreSQL-ready through `DATABASE_URL`.
- FastAPI health/admin API.
- Docker, Railway, Render, VPS, and cron deployment notes.

## Folder Structure

```text
bot/          Telegram publishing and message templates
scraper/      Cricbuzz, ESPN Cricinfo, and aggregator modules
ml_engine/    Toss prediction ensemble
graphics/     Pillow poster/card generation
database/     SQLAlchemy models, repository, schema
scheduler/    APScheduler automation jobs
api/          FastAPI app and admin endpoints
utils/        Text helpers
data/         SQLite database volume
assets/       Generated graphics
```

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel
DRY_RUN=false
```

Add the bot as an admin in your Telegram channel with permission to post, edit, delete, and pin messages.

## Run

```bash
python main.py
```

Open:

```text
http://localhost:8000/health
http://localhost:8000/stats
```

Manual admin triggers:

```bash
curl -X POST http://localhost:8000/admin/run-scan
curl -X POST http://localhost:8000/admin/check-results
```

## Docker

```bash
cp .env.example .env
docker compose up --build -d
```

## Railway

1. Create a new Railway project from this repository.
2. Railway can use `railway.json` automatically.
3. Add environment variables from `.env.example`.
4. Set `DRY_RUN=false`.
5. Use the default start command:

```bash
python main.py
```

6. Add a persistent volume mounted at `/app/data` if using SQLite, or set `DATABASE_URL` to Railway PostgreSQL.

## Render

1. Push this repository to GitHub.
2. In Render, create a new Blueprint from the repo.
3. Render will read `render.yaml`, create the web service, and attach PostgreSQL.
4. Add secret values for `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL_ID`.
5. Confirm `DRY_RUN=false`.

Manual Render setup also works:

1. Create a Web Service.
2. Runtime: Docker, or Python 3.11 with start command `python main.py`.
3. Add all environment variables.
4. For SQLite, add a persistent disk mounted at `/app/data`.
5. For production, prefer Render PostgreSQL and set:

```bash
DATABASE_URL=postgresql+psycopg://user:password@host:5432/db
```

If using PostgreSQL, add the matching driver to `requirements.txt`, for example `psycopg[binary]`.

## Keep Running Without Your Laptop

Your laptop cannot keep the bot active while powered off. Deploy this project to Render, Railway, or a VPS. Once deployed, the cloud server runs `python main.py` continuously, APScheduler keeps the bot posting, and Telegram receives posts even when your laptop is off.

See `CLOUD_ACTIVATION.md` for the exact 24/7 activation checklist.

## VPS Deployment

```bash
git clone <your-repo-url> pitch-toss-ai
cd pitch-toss-ai
cp .env.example .env
nano .env
docker compose up --build -d
```

Systemd alternative:

```ini
[Unit]
Description=Pitch Toss AI
After=network.target

[Service]
WorkingDirectory=/opt/pitch-toss-ai
EnvironmentFile=/opt/pitch-toss-ai/.env
ExecStart=/opt/pitch-toss-ai/.venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Cron Setup

The app already schedules itself with APScheduler. Use cron only as a watchdog:

```cron
*/5 * * * * curl -fsS http://localhost:8000/health >/dev/null || docker compose -f /opt/pitch-toss-ai/docker-compose.yml restart
```

## Automation Schedule

- Every `POSTING_INTERVAL_MINUTES`: scan and publish new predictions.
- Predictions are posted once per match inside the `PREDICTION_LEAD_HOURS` pre-match window, default `6`.
- Every 10 minutes: check actual toss results.
- Hourly: delete outdated prediction posts when configured.
- 08:00: daily schedule.
- 14:00: engagement/streak post.
- 20:00: VIP teaser.

## Important Notes

Scraping public sports websites is fragile because markup can change. The bot logs scraper warnings and keeps running. For a commercial deployment, replace or supplement scraping with a licensed cricket data API.

Toss prediction is probabilistic. The model intentionally avoids fake certainty and caps confidence at 65%.

For strict 6-hour posting, keep `POST_WITHOUT_START_TIME=false`. If a scraped fixture has no reliable start time, the bot stores it but waits instead of posting early.
