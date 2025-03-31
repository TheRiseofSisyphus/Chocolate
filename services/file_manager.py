import shutil
from pathlib import Path
from datetime import datetime
import logging
from config import USER_FILES_DIR, REPORTS_DIR

logger = logging.getLogger(__name__)


class FileManager:
    @staticmethod
    def save_user_file(user_id: int, file_bytes: bytes) -> Path:
        try:
            user_dir = USER_FILES_DIR / str(user_id)
            user_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = user_dir / f"file_{timestamp}.xlsx"

            with open(file_path, 'wb') as f:
                if hasattr(file_bytes, 'read'):
                    f.write(file_bytes.read())
                else:
                    f.write(file_bytes)

            return file_path
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise

    @staticmethod
    def save_report(user_id: int, sheet_name: str, content: str) -> Path:
        try:
            reports_dir = REPORTS_DIR / str(user_id)
            reports_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = reports_dir / f"report_{timestamp}_{sheet_name}.txt"

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return report_path
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            raise

    @staticmethod
    def get_user_reports(user_id: int) -> list[Path]:
        try:
            reports_dir = REPORTS_DIR / str(user_id)
            return sorted(reports_dir.glob("*.txt"), key=lambda f: f.stat().st_mtime,
                          reverse=True) if reports_dir.exists() else []
        except Exception as e:
            logger.error(f"Error getting reports: {e}")
            return []