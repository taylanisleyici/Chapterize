from pathlib import Path
import json
from core.config import ENGAGEMENT_THRESHOLD


def load_high_engagement_chapters(chapter_path: Path) -> list[dict]:
    with open(chapter_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [
        c for c in data["chapters"]
        if c["engagement_score"] >= ENGAGEMENT_THRESHOLD
    ]
