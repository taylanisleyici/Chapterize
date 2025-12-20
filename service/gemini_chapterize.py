from pathlib import Path
import json
from google import genai
from google.genai import types

from core.config import GEMINI_API_KEY, GEMINI_MODEL
from core.gemini import resolve_model
from model.chapter import Chapter, ChapterizeResult
from service.chapter_writer import write_chapters


def load_system_prompt() -> str:
    path = Path("prompt/chapterize_system.md")
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def load_transcript(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_json(text: str) -> dict:
    """
    Safely extract JSON from Gemini response.
    Handles ```json``` fenced outputs.
    """
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].strip()
    return json.loads(text)


def chapterize_transcript(
    transcript_path: Path,
    output_base_dir: Path | None = None,
) -> Path:
    """
    Runs Gemini chapterization and writes chapters JSON to disk.

    Returns:
        Path: written chapter file path
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=GEMINI_API_KEY)
    model = resolve_model(GEMINI_MODEL)

    system_prompt = load_system_prompt()
    transcript = load_transcript(transcript_path)

    response = client.models.generate_content(
        model=model.value,  # gemini-3-flash-preview
        contents=[
            system_prompt,
            json.dumps(transcript, ensure_ascii=False),
        ],
        config=types.GenerateContentConfig(
            temperature=0.4,
            # thinking_level="low",  # opsiyonel
        ),
    )

    data = _extract_json(response.text)

    chapters = [
        Chapter(
            title=c["title"],
            start=float(c["start"]),
            end=float(c["end"]),
            engagement_score=float(c["engagement_score"]),
        )
        for c in data["chapters"]
    ]

    result = ChapterizeResult(chapters=chapters)

    payload = {
        "chapters": [
            {
                "title": ch.title,
                "start": ch.start,
                "end": ch.end,
                "engagement_score": ch.engagement_score,
            }
            for ch in result.chapters
        ]
    }

    output_path = write_chapters(
        transcript_path=transcript_path,
        chapters_payload=payload,
        output_base_dir=output_base_dir,
    )

    return output_path
