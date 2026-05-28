from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from config import get_settings
from bot.messages import daily_schedule_post, engagement_post, pre_match_post, result_post, vip_teaser_post
from bot.telegram_client import TelegramPublisher
from database.models import Match, Prediction, TossActual
from database.repository import accuracy_snapshot, create_prediction, current_streak, upsert_match
from database.session import get_db
from graphics.cards import prediction_card, streak_card
from ml_engine.predictor import TossPredictor
from scraper.aggregator import CricketDataAggregator


class AutomationJobs:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.aggregator = CricketDataAggregator()
        self.predictor = TossPredictor()
        self.publisher = TelegramPublisher()

    async def scan_and_publish(self) -> None:
        db = get_db()
        try:
            for item in self.aggregator.upcoming_matches():
                match = upsert_match(db, item)
                if match.prediction:
                    continue
                if not self._inside_prediction_window(match):
                    continue
                prediction_data = self.predictor.predict(match).as_dict()
                if prediction_data["confidence"] < self.settings.confidence_threshold:
                    continue
                prediction = create_prediction(db, match, prediction_data)
                image_path = prediction_card(match, prediction)
                caption = pre_match_post(match, prediction, accuracy_snapshot(db))
                photo_id = await self.publisher.send_photo(image_path, caption, pin=self.settings.pin_predictions)
                prediction.telegram_photo_message_id = photo_id
                prediction.pinned = bool(photo_id and self.settings.pin_predictions)
                db.commit()
        finally:
            db.close()

    async def check_toss_results(self) -> None:
        db = get_db()
        try:
            rows = db.scalars(
                select(Prediction)
                .join(Match)
                .outerjoin(TossActual)
                .where(TossActual.id.is_(None))
                .order_by(Prediction.created_at.desc())
                .limit(25)
            ).all()
            for prediction in rows:
                match = prediction.match
                toss = self.aggregator.toss_result(match.source_id, match.team_a, match.team_b)
                if not toss.found:
                    continue
                was_correct = prediction.predicted_winner.lower() == toss.winner.lower()
                actual = TossActual(
                    prediction_id=prediction.id,
                    actual_winner=toss.winner,
                    decision=toss.decision,
                    was_correct=was_correct,
                )
                db.add(actual)
                match.status = "toss_done"
                db.commit()
                stats = accuracy_snapshot(db)
                text = result_post(match, prediction, toss.winner, stats)
                msg_id = await self.publisher.send_message(text)
                actual.posted_update_message_id = msg_id
                db.commit()
        finally:
            db.close()

    async def post_daily_schedule(self) -> None:
        db = get_db()
        try:
            matches = db.scalars(select(Match).where(Match.status == "upcoming").order_by(Match.created_at.desc()).limit(12)).all()
            await self.publisher.send_message(daily_schedule_post(matches))
        finally:
            db.close()

    async def post_engagement(self) -> None:
        db = get_db()
        try:
            stats = accuracy_snapshot(db)
            streak = current_streak(db)
            text = engagement_post(streak, stats)
            await self.publisher.send_message(text)
            image_path = streak_card(streak, stats["accuracy"])
            await self.publisher.send_photo(image_path, "🔥 *Pitch & Toss AI Streak Board*")
        finally:
            db.close()

    async def post_vip_teaser(self) -> None:
        await self.publisher.send_message(vip_teaser_post())

    async def delete_outdated_posts(self) -> None:
        if self.settings.auto_delete_hours <= 0:
            return
        cutoff = datetime.utcnow() - timedelta(hours=self.settings.auto_delete_hours)
        db = get_db()
        try:
            rows = db.scalars(select(Prediction).where(Prediction.created_at < cutoff).limit(50)).all()
            for prediction in rows:
                for message_id in (prediction.telegram_message_id, prediction.telegram_photo_message_id):
                    if message_id:
                        await self.publisher.delete_message(message_id)
                prediction.telegram_message_id = None
                prediction.telegram_photo_message_id = None
            db.commit()
        finally:
            db.close()

    def _inside_prediction_window(self, match: Match) -> bool:
        if match.starts_at is None:
            return self.settings.post_without_start_time
        starts_at = match.starts_at
        if starts_at.tzinfo is None:
            starts_at = starts_at.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        window_start = starts_at - timedelta(hours=self.settings.prediction_lead_hours)
        return window_start <= now < starts_at
