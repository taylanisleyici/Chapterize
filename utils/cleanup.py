import shutil
from pathlib import Path
from domain.paths import Paths


def cleanup_data_dir() -> None:
    """
    Checks for the lock file. If no lock file exists, deletes all files and subdirectories
    under the base data directory to clean it up.
    """
    lock_file = Paths.get_lock_file()
    if not lock_file.exists():
        base_dir = Paths._root
        for item in base_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)


def move_shorts_to_final() -> None:
    """
    Moves all files from the shorts output directory to the final directory without renaming.
    """
    short_dir = Paths.get_short_output_dir()
    final_dir = Paths.get_final_dir()
    for file in short_dir.iterdir():
        if file.is_file():
            shutil.move(str(file), str(final_dir / file.name))
