from database.models import Match, Prediction


def pre_match_post(match: Match, prediction: Prediction, stats: dict | None = None) -> str:
    factors = "\n".join(f"• {line}" for line in prediction.factors.splitlines()[:3])
    confidence = round(prediction.confidence * 100)
    tracker = ""
    if stats:
        tracker = (
            f"\n\n📊 *Success Rate:*\n"
            f"Wins: {stats['wins']} | Losses: {stats['losses']}\n"
            f"Accuracy: {stats['accuracy']}%"
        )
    return (
        f"🏏 *{match.league}*\n\n"
        f"🔥 *Match:*\n{match.team_a} vs {match.team_b}\n\n"
        f"🎯 *AI Toss Prediction:*\n{prediction.predicted_winner}\n\n"
        f"📊 *Confidence:*\n{confidence}%\n\n"
        f"📈 *Key Factors:*\n{factors}\n\n"
        f"⏱ *Timing:*\nPosted inside the 6-hour pre-match window"
        f"{tracker}\n\n"
        f"🤖 Powered by *Pitch & Toss AI*"
    )


def result_post(match: Match, prediction: Prediction, actual_winner: str, stats: dict) -> str:
    won = prediction.predicted_winner.lower() == actual_winner.lower()
    label = "✅ *TOSS WON*" if won else "❌ *TOSS MISSED*"
    return (
        f"{label}\n\n"
        f"🏏 *Match:*\n{match.short_a} vs {match.short_b}\n\n"
        f"🎯 *Prediction:*\n{prediction.predicted_winner}\n\n"
        f"🏆 *Actual Toss Winner:*\n{actual_winner}\n\n"
        f"📊 *Accuracy Tracker:*\n"
        f"Wins: {stats['wins']}\n"
        f"Losses: {stats['losses']}\n"
        f"Accuracy: {stats['accuracy']}%\n\n"
        f"🚀 *Pitch & Toss AI*"
    )


def daily_schedule_post(matches: list[Match]) -> str:
    if not matches:
        return "🏏 *Pitch & Toss AI Daily Board*\n\nNo upcoming tracked matches found yet. Monitoring continues automatically."
    rows = "\n".join(f"• {m.team_a} vs {m.team_b} · {_match_time(m)} · {m.venue}" for m in matches[:12])
    return f"🏏 *Pitch & Toss AI Daily Board*\n\n{rows}\n\nPredictions will be posted automatically before toss."


def engagement_post(streak: int, stats: dict) -> str:
    return (
        "🔥 *AI Toss Desk Update*\n\n"
        f"Current winning streak: {streak}\n"
        f"Tracked accuracy: {stats['accuracy']}% over {stats['total']} settled tosses.\n\n"
        "Premium toss insights are monitored 24/7."
    )


def vip_teaser_post() -> str:
    return (
        "💎 *VIP Toss Radar*\n\n"
        "High-confidence fixtures, venue movement and captain trend alerts are being scanned automatically.\n\n"
        "🚀 Pitch & Toss AI"
    )


def _match_time(match: Match) -> str:
    if not match.starts_at:
        return "time TBA"
    return match.starts_at.strftime("%b %d, %I:%M %p")
