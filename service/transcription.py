from pathlib import Path
import json
from faster_whisper import WhisperModel

from core.paths import get_transcript_dir
from model.transcript import Transcript, TranscriptSegment


# Model'i global tutuyoruz (1 kere load edilir)
_MODEL = WhisperModel(
    "medium",              # <-- ÖNEMLİ DÜZELTME
    compute_type="int8",
)


def transcribe_audio(
    audio_path: Path,
    output_base_dir: Path | None = None,
) -> Path:
    """
    Transcribes an audio file and writes sentence-level transcript as JSON.
    """
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    transcript_dir = get_transcript_dir(output_base_dir)
    transcript_path = transcript_dir / f"{audio_path.stem}.json"

    segments, info = _MODEL.transcribe(
        str(audio_path),
        vad_filter=True,
        beam_size=5,
    )

    transcript_segments = [
        TranscriptSegment(
            start=seg.start,
            end=seg.end,
            text=seg.text.strip(),
        )
        for seg in segments
    ]

    transcript = Transcript(
        language=info.language,
        segments=transcript_segments,
    )

    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "language": transcript.language,
                "segments": [
                    {
                        "start": s.start,
                        "end": s.end,
                        "text": s.text,
                    }
                    for s in transcript.segments
                ],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    return transcript_path
