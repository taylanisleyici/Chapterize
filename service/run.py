from pathlib import Path

from utils.video_merge import merge_video_audio
from utils.chapter_filter import load_high_engagement_chapters
from utils.video_cut import cut_subclip
from utils.video_vertical import crop_to_vertical
from utils.subtitle_burn import burn_in_ass_subtitle

from service.youtube_audio import download_audio
from service.youtube_video import download_video
from service.transcription import transcribe_audio
from service.gemini_chapterize import chapterize_transcript
from service.ass_subtitle import generate_ass

from core.transcription import TranscriptionMode
from core.video import VideoQuality
from core.paths import (
    get_audio_dir,
    get_transcript_dir,
    get_chapter_dir,
    get_subtitle_dir,
    get_video_dir,
    get_short_output_dir,
)


def cleanup_dir(dir_path: Path):
    for p in dir_path.iterdir():
        if p.is_file():
            p.unlink(missing_ok=True)


def run_youtube_chapterize_pipeline(
    youtube_url: str,
    *,
    base_dir: Path | None = None,
    video_quality: VideoQuality = VideoQuality.P1080,
    clean: bool = True,
):
    """
    FULL PROJECT PIPELINE

    YouTube URL
      → audio
      → transcript
      → chapters
      → video
      → subclip
      → crop
      → subtitle burn-in
      → FINAL SHORTS
    """

    print("Pipeline started")
    print(f"YouTube URL: {youtube_url}")

    audio_dir = get_audio_dir(base_dir)
    transcript_dir = get_transcript_dir(base_dir)
    chapter_dir = get_chapter_dir(base_dir)
    subtitle_dir = get_subtitle_dir(base_dir)
    video_dir = get_video_dir(base_dir)
    output_dir = get_short_output_dir(base_dir)

    print(f"Audio dir: {audio_dir}")
    print(f"Transcript dir: {transcript_dir}")
    print(f"Chapter dir: {chapter_dir}")
    print(f"Subtitle dir: {subtitle_dir}")
    print(f"Video dir: {video_dir}")
    print(f"Output dir: {output_dir}")

    print("Downloading audio...")
    audio_path = download_audio(
        youtube_url,
        output_dir=base_dir,
    )
    print(f"Audio downloaded: {audio_path}")

    print("Transcribing audio (sentence + word)...")
    transcript_paths = transcribe_audio(
        audio_path,
        output_base_dir=base_dir,
        mode=TranscriptionMode.BOTH,
    )

    sentence_transcript = next(p for p in transcript_paths if ".sentence." in p.name)
    word_transcript = next(p for p in transcript_paths if ".word." in p.name)

    print(f"Sentence transcript: {sentence_transcript}")
    print(f"Word transcript: {word_transcript}")

    print("Generating chapters with Gemini...")

    chapter_path = chapterize_transcript(sentence_transcript)
    print(f"Chapters written: {chapter_path}")

    print(f"Downloading video ({video_quality.name})...")
    video_path = download_video(
        youtube_url,
        quality=video_quality,
        output_base_dir=base_dir,
    )
    print(f"Video downloaded: {video_path}")

    print("Merging video and audio...")
    merged_video_path = video_dir / f"{video_path.stem}_merged.mp4"

    merge_video_audio(
        video_path=video_path,
        audio_path=audio_path,
        output_path=merged_video_path,
    )

    print(f"Merged video created: {merged_video_path}")

    print("Filtering chapters by engagement threshold...")
    chapters = load_high_engagement_chapters(chapter_path)
    print(f"Selected chapters: {len(chapters)}")

    final_videos = []

    video_id = video_path.stem

    for i, ch in enumerate(chapters, start=1):
        print(f"\n--- Processing chapter {i} ---")

        raw_clip = output_dir / f".{video_id}_{i}_raw.mp4"
        vertical_clip = output_dir / f".{video_id}_{i}_vertical.mp4"

        final_clip = output_dir / f"{video_id}_{i}.mp4"
        subtitle_path = subtitle_dir / f"{video_id}_{i}.ass"
        title_path = output_dir / f"{video_id}_{i}.txt"

        chapter_title = ch.get("title", "").strip()
        title_path.write_text(chapter_title, encoding="utf-8")
        print(f"Chapter title written: {title_path}")

        print("Generating ASS subtitle...")
        generate_ass(
            word_transcript_path=word_transcript,
            output_path=subtitle_path,
            start=float(ch["start"]),
            end=float(ch["end"]),
        )
        print(f"Subtitle written: {subtitle_path}")

        print("Cutting subclip...")
        cut_subclip(
            video_path=merged_video_path,
            start=float(ch["start"]),
            end=float(ch["end"]),
            output_path=raw_clip,
        )

        print("Cropping to vertical (9:16)...")
        crop_to_vertical(
            input_path=raw_clip,
            output_path=vertical_clip,
        )

        print("Burning subtitles into video...")
        burn_in_ass_subtitle(
            video_path=vertical_clip,
            subtitle_path=subtitle_path,
            output_path=final_clip,
        )

        print(f"Final short created: {final_clip}")
        final_videos.append(final_clip)

        raw_clip.unlink(missing_ok=True)
        vertical_clip.unlink(missing_ok=True)

    print("\nPipeline finished successfully")

    if clean:
        print("Cleaning up intermediate files...")

        cleanup_dir(audio_dir)
        cleanup_dir(chapter_dir)
        cleanup_dir(video_dir)
        cleanup_dir(transcript_dir)
        cleanup_dir(subtitle_dir)

    return final_videos
