from dataclasses import dataclass
from typing import List


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    language: str
    segments: List[TranscriptSegment]
