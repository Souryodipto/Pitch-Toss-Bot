from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from config import get_settings
from scraper.models import MatchInfo
from utils.datetime_parser import parse_match_start
from utils.text import clean_text, short_name, stable_id


class CricbuzzScraper:
    def __init__(self) -> None:
        self.settings = get_settings()

    def fetch_upcoming_matches(self) -> list[MatchInfo]:
        response = requests.get(self.settings.cricbuzz_url, timeout=20, headers={"User-Agent": "PitchTossAI/1.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text_blocks = [clean_text(node.get_text(" ")) for node in soup.select(".cb-mtch-lst, .cb-col, .cb-schdl")]
        matches: list[MatchInfo] = []
        seen: set[str] = set()
        pattern = re.compile(r"([A-Z][A-Za-z .&'-]+)\s+vs\s+([A-Z][A-Za-z .&'-]+)", re.I)
        for block in text_blocks:
            found = pattern.search(block)
            if not found:
                continue
            team_a, team_b = clean_text(found.group(1)), clean_text(found.group(2))
            if len(team_a) > 50 or len(team_b) > 50:
                continue
            source_id = stable_id("cricbuzz", team_a, team_b, datetime.utcnow().date().isoformat())
            if source_id in seen:
                continue
            seen.add(source_id)
            venue = self._extract_venue(block)
            league = self._extract_league(block)
            matches.append(
                MatchInfo(
                    source_id=source_id,
                    title=f"{team_a} vs {team_b}",
                    team_a=team_a,
                    team_b=team_b,
                    short_a=short_name(team_a),
                    short_b=short_name(team_b),
                    venue=venue,
                    league=league,
                    match_format=self._extract_format(block),
                    starts_at=parse_match_start(block, self.settings.timezone),
                    raw={"source": "cricbuzz", "text": block[:1000]},
                )
            )
        return matches

    @staticmethod
    def _extract_venue(block: str) -> str:
        markers = [" at ", "Venue:"]
        for marker in markers:
            if marker in block:
                return clean_text(block.split(marker, 1)[1].split(",", 2)[0])[:220] or "Unknown venue"
        return "Unknown venue"

    @staticmethod
    def _extract_league(block: str) -> str:
        for token in ["IPL", "Indian Premier League", "T20 World Cup", "ODI", "Test"]:
            if token.lower() in block.lower():
                return "IPL 2026" if token == "IPL" else token
        return "Cricket"

    @staticmethod
    def _extract_format(block: str) -> str:
        lowered = block.lower()
        if "test" in lowered:
            return "Test"
        if "odi" in lowered:
            return "ODI"
        return "T20"
