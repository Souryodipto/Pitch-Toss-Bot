# 24/7 Activation Checklist

To keep Pitch & Toss AI active when your laptop is off, deploy it to Render, Railway, or a VPS.

## Fastest Option: Render

1. Push this folder to a GitHub repository.
2. Go to Render and choose **New > Blueprint**.
3. Select the GitHub repository.
4. Render reads `render.yaml` and creates:
   - the web service,
   - a PostgreSQL database,
   - the health check.
5. Add these secret environment variables:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=your_group_or_channel_id
DRY_RUN=false
```

6. Deploy.
7. Open `/health`; it should return:

```json
{"ok": true}
```

## What Happens After Deploy

- On startup, the bot scans immediately.
- Every 15 minutes, it fetches upcoming cricket matches.
- For every new discovered match, it creates one prediction only when the match is inside the 6-hour pre-match window.
- It never repeats a prediction for the same stored match.
- Every 10 minutes, it checks toss results and posts the accuracy update.
- Daily schedule, engagement posts, VIP teasers, pinning, graphics, and outdated post deletion continue automatically.

## Manual Cloud Triggers

Replace `YOUR_URL` with your Render/Railway URL:

```bash
curl -X POST https://YOUR_URL/admin/run-scan
curl -X POST https://YOUR_URL/admin/check-results
curl -X POST https://YOUR_URL/admin/post-schedule
```

## Important

Free tiers may sleep. For true 24/7 posting, use a paid always-on instance or a VPS.
