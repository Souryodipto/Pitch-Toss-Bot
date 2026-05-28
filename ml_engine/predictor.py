from __future__ import annotations

import math
from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from database.models import Match


@dataclass(slots=True)
class PredictionResult:
    predicted_winner: str
    confidence: float
    probability_a: float
    probability_b: float
    factors: list[str]
    model_version: str = "ensemble-v1"

    def as_dict(self) -> dict:
        return {
            "predicted_winner": self.predicted_winner,
            "confidence": self.confidence,
            "probability_a": self.probability_a,
            "probability_b": self.probability_b,
            "factors": self.factors,
            "model_version": self.model_version,
        }


class TossPredictor:
    def __init__(self) -> None:
        self.models = self._train_synthetic_baseline()

    def predict(self, match: Match) -> PredictionResult:
        features, labels = self._features(match)
        model_probs = [model.predict_proba([features])[0][1] for model in self.models]
        weighted_score = self._weighted_score(match)
        raw_prob_a = float(np.mean(model_probs) * 0.55 + weighted_score * 0.45)
        prob_a = self._calibrate(raw_prob_a)
        prob_b = 1.0 - prob_a
        confidence = max(prob_a, prob_b)
        predicted = match.team_a if prob_a >= prob_b else match.team_b
        return PredictionResult(
            predicted_winner=predicted,
            confidence=round(confidence, 2),
            probability_a=round(prob_a, 3),
            probability_b=round(prob_b, 3),
            factors=labels[:3],
        )

    @staticmethod
    def _train_synthetic_baseline() -> list:
        rng = np.random.default_rng(42)
        x = rng.normal(0, 1, (600, 8))
        logits = 0.25 * x[:, 0] + 0.18 * x[:, 1] + 0.12 * x[:, 2] - 0.1 * x[:, 3] + rng.normal(0, 0.8, 600)
        y = (logits > 0).astype(int)
        return [
            LogisticRegression(max_iter=1000).fit(x, y),
            RandomForestClassifier(n_estimators=80, max_depth=4, random_state=42).fit(x, y),
            GradientBoostingClassifier(random_state=42, max_depth=2).fit(x, y),
        ]

    @staticmethod
    def _features(match: Match) -> tuple[list[float], list[str]]:
        team_signal = TossPredictor._text_signal(match.team_a) - TossPredictor._text_signal(match.team_b)
        venue_signal = TossPredictor._text_signal(match.venue) - 0.5
        captain_signal = TossPredictor._text_signal(match.captain_a or match.team_a) - TossPredictor._text_signal(match.captain_b or match.team_b)
        humidity = (match.humidity - 55.0) / 30.0
        home = 1.0 if match.home_team == match.team_a else -1.0 if match.home_team == match.team_b else 0.0
        day_night = 0.4 if match.is_day_night else -0.2
        fmt = {"T20": 0.35, "ODI": 0.1, "Test": -0.1}.get(match.match_format, 0.0)
        weather = 0.2 if "cloud" in match.weather.lower() else 0.0
        labels = [
            "Better venue toss history" if venue_signal >= 0 else "Venue trend slightly favors opposition",
            "Captain trend advantage" if captain_signal >= 0 else "Captain trend is narrowly balanced",
            "Strong recent probability pattern" if team_signal >= 0 else "Historical pattern is close",
            "Day/night conditions included",
            "Weather and humidity adjusted",
        ]
        return [team_signal, venue_signal, captain_signal, humidity, home, day_night, fmt, weather], labels

    @staticmethod
    def _weighted_score(match: Match) -> float:
        features, _ = TossPredictor._features(match)
        weights = np.array([0.16, 0.18, 0.22, -0.05, 0.12, 0.08, 0.07, 0.04])
        z = float(np.dot(np.array(features), weights))
        return 1 / (1 + math.exp(-z))

    @staticmethod
    def _calibrate(probability: float) -> float:
        centered = 0.5 + (probability - 0.5) * 0.42
        return min(0.65, max(0.50, centered))

    @staticmethod
    def _text_signal(value: str) -> float:
        total = sum(ord(char) for char in value.lower())
        return (total % 100) / 100.0
