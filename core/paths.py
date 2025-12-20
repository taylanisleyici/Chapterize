from pathlib import Path
from core.config import BASE_DATA_DIR


AUDIO_DIR_NAME = "audio"
TRANSCRIPT_DIR_NAME = "transcripts"


def get_audio_dir(base_dir: Path | None = None) -> Path:
    """
    Returns audio output directory.
    Can be overridden for testing or custom runs.
    """
    root = base_dir or BASE_DATA_DIR
    path = root / AUDIO_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_transcript_dir(base_dir: Path | None = None) -> Path:
    """
    Returns transcript output directory.
    Can be overridden for testing or custom runs.
    """
    root = base_dir or BASE_DATA_DIR
    path = root / TRANSCRIPT_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path
