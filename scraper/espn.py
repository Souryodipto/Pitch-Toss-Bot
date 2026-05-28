from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from config import get_settings
from scraper.models import MatchInfo, TossResult
from utils.datetime_parser import parse_match_start
from utils.text import clean_text, short_name, stable_id


class ESPNScraper:
    def __init__(self) -> None:
        self.settings = get_settings()

    def fetch_upcoming_matches(self) -> list[MatchInfo]:
        response = requests.get(self.settings.espn_url, timeout=20, headers={"User-Agent": "PitchTossAI/1.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        blocks = [clean_text(node.get_text(" ")) for node in soup.select("article, .ds-p-4, .ci-team-score, .ds-border-line")]
        matches: list[MatchInfo] = []
        seen: set[str] = set()
        pattern = re.compile(r"([A-Z][A-Za-z .&'-]+)\s+(?:v|vs)\s+([A-Z][A-Za-z .&'-]+)", re.I)
        for block in blocks:
            found = pattern.search(block)
            if not found:
                continue
            team_a, team_b = clean_text(found.group(1)), clean_text(found.group(2))
            source_id = stable_id("espn", team_a, team_b, datetime.utcnow().date().isoformat())
            if source_id in seen:
                continue
            seen.add(source_id)
            matches.append(
                MatchInfo(
                    source_id=source_id,
                    title=f"{team_a} vs {team_b}",
                    team_a=team_a,
                    team_b=team_b,
                    short_a=short_name(team_a),
                    short_b=short_name(team_b),
                    venue=self._venue(block),
                    league="Cricket",
                    match_format=self._format(block),
                    starts_at=parse_match_start(block, self.settings.timezone),
                    raw={"source": "espncricinfo", "text": block[:1000]},
                )
            )
        return matches

    def fetch_toss_result(self, source_id: str, team_a: str, team_b: str) -> TossResult:
        response = requests.get(self.settings.espn_url, timeout=20, headers={"User-Agent": "PitchTossAI/1.0"})
        response.raise_for_status()
        text = clean_text(BeautifulSoup(response.text, "html.parser").get_text(" "))
        pattern = re.compile(rf"({re.escape(team_a)}|{re.escape(team_b)}).*won the toss.*?(bat|bowl|field)?", re.I)
        found = pattern.search(text)
        if not found:
            return TossResult(source_id=source_id, winner="", found=False)
        winner = team_a if found.group(1).lower() == team_a.lower() else team_b
        return TossResult(source_id=source_id, winner=winner, decision=found.group(2), found=True)

    @staticmethod
    def _venue(block: str) -> str:
        if " at " in block:
            return clean_text(block.split(" at ", 1)[1].split(",", 1)[0])[:220] or "Unknown venue"
        return "Unknown venue"

    @staticmethod
    def _format(block: str) -> str:
        lowered = block.lower()
        if "test" in lowered:
            return "Test"
        if "odi" in lowered:
            return "ODI"
        return "T20"
