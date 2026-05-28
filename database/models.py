from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("source_id", name="uq_matches_source_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[str] = mapped_column(String(240), index=True)
    title: Mapped[str] = mapped_column(String(300))
    team_a: Mapped[str] = mapped_column(String(120))
    team_b: Mapped[str] = mapped_column(String(120))
    short_a: Mapped[str] = mapped_column(String(20))
    short_b: Mapped[str] = mapped_column(String(20))
    venue: Mapped[str] = mapped_column(String(240), default="Unknown venue")
    league: Mapped[str] = mapped_column(String(120), default="Cricket")
    match_format: Mapped[str] = mapped_column(String(40), default="T20")
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    captain_a: Mapped[str | None] = mapped_column(String(120), nullable=True)
    captain_b: Mapped[str | None] = mapped_column(String(120), nullable=True)
    weather: Mapped[str] = mapped_column(String(80), default="Partly cloudy")
    humidity: Mapped[float] = mapped_column(Float, default=55.0)
    is_day_night: Mapped[bool] = mapped_column(Boolean, default=True)
    home_team: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="upcoming")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    prediction: Mapped["Prediction"] = relationship(back_populates="match", uselist=False)


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    predicted_winner: Mapped[str] = mapped_column(String(120))
    confidence: Mapped[float] = mapped_column(Float)
    probability_a: Mapped[float] = mapped_column(Float)
    probability_b: Mapped[float] = mapped_column(Float)
    factors: Mapped[str] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(String(60), default="ensemble-v1")
    telegram_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    telegram_photo_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    match: Mapped[Match] = relationship(back_populates="prediction")
    result: Mapped["TossActual"] = relationship(back_populates="prediction", uselist=False)


class TossActual(Base):
    __tablename__ = "toss_actuals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"), index=True)
    actual_winner: Mapped[str] = mapped_column(String(120))
    decision: Mapped[str | None] = mapped_column(String(40), nullable=True)
    was_correct: Mapped[bool] = mapped_column(Boolean)
    posted_update_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    prediction: Mapped[Prediction] = relationship(back_populates="result")


class VenueStat(Base):
    __tablename__ = "venue_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    venue: Mapped[str] = mapped_column(String(240), unique=True)
    team_a_bias: Mapped[float] = mapped_column(Float, default=0.50)
    day_night_bias: Mapped[float] = mapped_column(Float, default=0.50)
    samples: Mapped[int] = mapped_column(Integer, default=0)


class CaptainStat(Base):
    __tablename__ = "captain_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    captain: Mapped[str] = mapped_column(String(120), unique=True)
    toss_win_rate: Mapped[float] = mapped_column(Float, default=0.50)
    samples: Mapped[int] = mapped_column(Integer, default=0)
