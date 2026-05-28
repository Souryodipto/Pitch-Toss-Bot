from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: str = Field("", alias="TELEGRAM_BOT_TOKEN")
    telegram_channel_id: str = Field("", alias="TELEGRAM_CHANNEL_ID")
    database_url: str = Field("sqlite:///data/pitch_toss_ai.db", alias="DATABASE_URL")
    posting_interval_minutes: int = Field(15, alias="POSTING_INTERVAL_MINUTES")
    run_scan_on_startup: bool = Field(True, alias="RUN_SCAN_ON_STARTUP")
    timezone: str = Field("Asia/Kolkata", alias="TIMEZONE")
    auto_delete_hours: int = Field(8, alias="AUTO_DELETE_HOURS")
    confidence_threshold: float = Field(0.52, alias="CONFIDENCE_THRESHOLD")
    prediction_lead_hours: int = Field(6, alias="PREDICTION_LEAD_HOURS")
    post_without_start_time: bool = Field(False, alias="POST_WITHOUT_START_TIME")
    pin_predictions: bool = Field(True, alias="PIN_PREDICTIONS")
    dry_run: bool = Field(True, alias="DRY_RUN")
    cricbuzz_url: str = Field("https://www.cricbuzz.com/cricket-match/live-scores/upcoming-matches", alias="CRICBUZZ_URL")
    espn_url: str = Field("https://www.espncricinfo.com/live-cricket-score", alias="ESPN_URL")
    brand_name: str = Field("Pitch & Toss AI", alias="BRAND_NAME")
    theme_primary: str = Field("#D6A84F", alias="THEME_PRIMARY")
    theme_background: str = Field("#070707", alias="THEME_BACKGROUND")
    theme_text: str = Field("#FFFFFF", alias="THEME_TEXT")


@lru_cache
def get_settings() -> Settings:
    return Settings()
