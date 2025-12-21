from pathlib import Path
from core.config import BASE_DATA_DIR


AUDIO_DIR_NAME = "audio"
TRANSCRIPT_DIR_NAME = "transcripts"
CHAPTER_DIR_NAME = "chapters"
VIDEO_DIR_NAME = "video"
SUBTITLE_DIR_NAME = "subtitles"
SHORTS_DIR_NAME = "shorts"


def _ensure(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_audio_dir(base_dir: Path | None = None) -> Path:
    root = base_dir or BASE_DATA_DIR
    return _ensure(root / AUDIO_DIR_NAME)


def get_transcript_dir(base_dir: Path | None = None) -> Path:
    root = base_dir or BASE_DATA_DIR
    return _ensure(root / TRANSCRIPT_DIR_NAME)


def get_chapter_dir(base_dir: Path | None = None) -> Path:
    root = base_dir or BASE_DATA_DIR
    return _ensure(root / CHAPTER_DIR_NAME)


def get_video_dir(base_dir: Path | None = None) -> Path:
    root = base_dir or BASE_DATA_DIR
    path = root / VIDEO_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_subtitle_dir(base_dir: Path | None = None) -> Path:
    root = base_dir or BASE_DATA_DIR
    return _ensure(root / SUBTITLE_DIR_NAME)


def get_short_output_dir(base_dir: Path | None = None) -> Path:
    root = base_dir or BASE_DATA_DIR
    return _ensure(root / SHORTS_DIR_NAME)

