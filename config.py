import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
USER_FILES_DIR = STORAGE_DIR / "user_files"
REPORTS_DIR = STORAGE_DIR / "reports"

for dir_path in [USER_FILES_DIR, REPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


BOT_TOKEN = os.getenv("BOT_TOKEN", "FAKE_TOKEN_FOR_LOCAL") #Чтение из окружения
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
OPERATOR_PERCENT = float(os.getenv("OPERATOR_PERCENT", "0.5"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mydatabase")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")
