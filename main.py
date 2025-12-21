from service.run import run_youtube_chapterize_pipeline


def main():
    run_youtube_chapterize_pipeline(
        youtube_url="https://www.youtube.com/watch?v=6jKGclan4LE"  # Example URL :D
    )


if __name__ == "__main__":
    main()
