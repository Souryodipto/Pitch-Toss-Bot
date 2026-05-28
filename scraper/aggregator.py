from scraper.cricbuzz import CricbuzzScraper
from scraper.espn import ESPNScraper
from scraper.models import MatchInfo, TossResult


class CricketDataAggregator:
    def __init__(self) -> None:
        self.cricbuzz = CricbuzzScraper()
        self.espn = ESPNScraper()

    def upcoming_matches(self) -> list[MatchInfo]:
        matches: dict[str, MatchInfo] = {}
        for fetcher in (self.cricbuzz.fetch_upcoming_matches, self.espn.fetch_upcoming_matches):
            try:
                for match in fetcher():
                    key = f"{match.team_a.lower()}:{match.team_b.lower()}"
                    matches.setdefault(key, match)
            except Exception as exc:
                print(f"scraper warning: {fetcher.__qualname__}: {exc}")
        return list(matches.values())

    def toss_result(self, source_id: str, team_a: str, team_b: str) -> TossResult:
        try:
            return self.espn.fetch_toss_result(source_id, team_a, team_b)
        except Exception as exc:
            print(f"toss result warning: {exc}")
            return TossResult(source_id=source_id, winner="", found=False)
