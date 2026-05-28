from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class MatchInfo:
    source_id: str
    title: str
    team_a: str
    team_b: str
    short_a: str
    short_b: str
    venue: str = "Unknown venue"
    league: str = "Cricket"
    match_format: str = "T20"
    starts_at: datetime | None = None
    captain_a: str | None = None
    captain_b: str | None = None
    weather: str = "Partly cloudy"
    humidity: float = 55.0
    is_day_night: bool = True
    home_team: str | None = None
    raw: dict = field(default_factory=dict)


@dataclass(slots=True)
class TossResult:
    source_id: str
    winner: str
    decision: str | None = None
    found: bool = False
