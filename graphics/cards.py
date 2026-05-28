from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from config import get_settings
from database.models import Match, Prediction


OUTPUT_DIR = Path("assets/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def prediction_card(match: Match, prediction: Prediction) -> Path:
    settings = get_settings()
    width, height = 1200, 675
    bg = settings.theme_background
    gold = settings.theme_primary
    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), fill=bg)
    draw.rectangle((34, 34, width - 34, height - 34), outline=gold, width=4)
    draw.rectangle((0, 0, width, 118), fill="#111111")
    draw.text((54, 36), settings.brand_name.upper(), font=_font(42, True), fill=gold)
    draw.text((54, 150), match.league, font=_font(36, True), fill="#FFFFFF")
    draw.text((54, 220), match.team_a, font=_font(56, True), fill="#FFFFFF")
    draw.text((54, 300), "VS", font=_font(44, True), fill=gold)
    draw.text((54, 365), match.team_b, font=_font(56, True), fill="#FFFFFF")
    draw.rounded_rectangle((720, 190, 1110, 500), radius=18, fill="#151515", outline=gold, width=3)
    draw.text((755, 225), "AI TOSS PICK", font=_font(30, True), fill=gold)
    draw.text((755, 285), prediction.predicted_winner[:19], font=_font(42, True), fill="#FFFFFF")
    draw.text((755, 360), f"{round(prediction.confidence * 100)}% confidence", font=_font(34, True), fill=gold)
    draw.text((54, 560), match.venue[:60], font=_font(26), fill="#D8D8D8")
    path = OUTPUT_DIR / f"prediction-{match.id}.png"
    image.save(path)
    return path


def streak_card(streak: int, accuracy: float) -> Path:
    image = Image.new("RGB", (1000, 1000), "#070707")
    draw = ImageDraw.Draw(image)
    draw.rectangle((42, 42, 958, 958), outline="#D6A84F", width=5)
    draw.text((80, 95), "PITCH & TOSS AI", font=_font(48, True), fill="#D6A84F")
    draw.text((80, 300), "WINNING STREAK", font=_font(54, True), fill="#FFFFFF")
    draw.text((80, 390), str(streak), font=_font(180, True), fill="#D6A84F")
    draw.text((80, 650), f"Accuracy {accuracy}%", font=_font(50, True), fill="#FFFFFF")
    path = OUTPUT_DIR / "streak.png"
    image.save(path)
    return path
