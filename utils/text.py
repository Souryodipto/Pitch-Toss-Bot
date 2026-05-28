import hashlib
import re


def short_name(team: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", team)
    if not words:
        return "TBA"
    if len(words) == 1:
        return words[0][:3].upper()
    return "".join(word[0] for word in words[:4]).upper()


def stable_id(*parts: str) -> str:
    raw = "|".join(part.strip().lower() for part in parts if part)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()
