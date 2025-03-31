import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
USER_FILES_DIR = STORAGE_DIR / "user_files"
REPORTS_DIR = STORAGE_DIR / "reports"

for dir_path in [USER_FILES_DIR, REPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

BOT_TOKEN = "8021467657:AAGvNSEqyuNhiAUdV_YsYOqi-wRH7XXstww"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
OPERATOR_PERCENT = 0.5  # 0.5% для оператора