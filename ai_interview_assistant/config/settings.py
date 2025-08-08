"""Settings configuration for AI Interview Assistant."""

from pathlib import Path

class Settings:
    """Settings for the AI Interview Assistant."""
    BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Go up to project root
    LOG_DIR = BASE_DIR / "logs"
    DATA_DIR = BASE_DIR / "data/conversations"
    ENV_FILE = BASE_DIR / ".env"
    GOOGLE_CREDENTIALS = BASE_DIR / "google-cloud-credentials.json"

    @staticmethod
    def init_logging(log_name="interview_assistant.log"):
        import logging
        Settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Settings.LOG_DIR / log_name),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

