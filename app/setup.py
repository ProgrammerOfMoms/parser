import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


def setup() -> None:
    """Установить настройки перед запуском"""
    files_dir = BASE_DIR / "files"
    for folder in ("In", "Out", "Err", "Ok"):
        if not os.path.exists(files_dir / folder):
            os.makedirs(files_dir / folder)
