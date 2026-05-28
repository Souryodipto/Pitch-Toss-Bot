from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select
from config import get_settings
from database.models import Match, Prediction
from database.repository import accuracy_snapshot, current_streak
from database.session import get_db, init_db
from scheduler.runner import build_scheduler


settings = get_settings()
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    init_db()
    scheduler = build_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Pitch & Toss AI", version="1.0.0", lifespan=lifespan)


@app.get("/")
def root() -> dict:
    return {"service": settings.brand_name, "status": "running", "dry_run": settings.dry_run}


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/stats")
def stats() -> dict:
    db = get_db()
    try:
        snap = accuracy_snapshot(db)
        snap["streak"] = current_streak(db)
        snap["matches"] = len(db.scalars(select(Match)).all())
        snap["predictions"] = len(db.scalars(select(Prediction)).all())
        return snap
    finally:
        db.close()


@app.post("/admin/run-scan")
async def run_scan() -> dict:
    from scheduler.jobs import AutomationJobs

    await AutomationJobs().scan_and_publish()
    return {"ok": True}


@app.post("/admin/check-results")
async def check_results() -> dict:
    from scheduler.jobs import AutomationJobs

    await AutomationJobs().check_toss_results()
    return {"ok": True}


@app.post("/admin/post-schedule")
async def post_schedule() -> dict:
    from scheduler.jobs import AutomationJobs

    await AutomationJobs().post_daily_schedule()
    return {"ok": True}
