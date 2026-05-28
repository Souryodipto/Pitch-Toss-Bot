from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from database.models import Match, Prediction, TossActual
from scraper.models import MatchInfo


def upsert_match(db: Session, item: MatchInfo) -> Match:
    match = db.scalar(select(Match).where(Match.source_id == item.source_id))
    now = datetime.utcnow()
    if match is None:
        match = Match(source_id=item.source_id, created_at=now)
        db.add(match)
    match.title = item.title
    match.team_a = item.team_a
    match.team_b = item.team_b
    match.short_a = item.short_a
    match.short_b = item.short_b
    match.venue = item.venue
    match.league = item.league
    match.match_format = item.match_format
    match.starts_at = item.starts_at
    match.captain_a = item.captain_a
    match.captain_b = item.captain_b
    match.weather = item.weather
    match.humidity = item.humidity
    match.is_day_night = item.is_day_night
    match.home_team = item.home_team
    match.updated_at = now
    db.commit()
    db.refresh(match)
    return match


def accuracy_snapshot(db: Session) -> dict:
    wins = db.scalar(select(func.count()).select_from(TossActual).where(TossActual.was_correct.is_(True))) or 0
    losses = db.scalar(select(func.count()).select_from(TossActual).where(TossActual.was_correct.is_(False))) or 0
    total = wins + losses
    return {
        "wins": wins,
        "losses": losses,
        "accuracy": round((wins / total * 100), 1) if total else 0.0,
        "total": total,
    }


def current_streak(db: Session) -> int:
    rows = db.scalars(select(TossActual).order_by(TossActual.created_at.desc()).limit(100)).all()
    streak = 0
    for row in rows:
        if not row.was_correct:
            break
        streak += 1
    return streak


def create_prediction(db: Session, match: Match, prediction: dict) -> Prediction:
    existing = db.scalar(select(Prediction).where(Prediction.match_id == match.id))
    if existing:
        return existing
    row = Prediction(
        match_id=match.id,
        predicted_winner=prediction["predicted_winner"],
        confidence=prediction["confidence"],
        probability_a=prediction["probability_a"],
        probability_b=prediction["probability_b"],
        factors="\n".join(prediction["factors"]),
        model_version=prediction["model_version"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
