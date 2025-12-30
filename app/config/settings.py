import os
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------------
# Load environment variables from .env file (if present)
# -----------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# -----------------------------------------------------------
# Basic Application Info
# -----------------------------------------------------------
APP_NAME = os.getenv("APP_NAME", "AI Recommender System")
ENV = os.getenv("APP_ENV", "development")  # development | staging | production
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "9000"))
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

# -----------------------------------------------------------
# Model Configuration
# -----------------------------------------------------------
QWEN_MODEL_NAME: str = "Qwen/Qwen2.5-7B-Instruct"
BLIP_MODEL_NAME: str = "Salesforce/blip-image-captioning-base"
EMOTION_MODEL_NAME: str = "abhilash88/face-emotion-detection"

# -----------------------------------------------------------
# NATS Configuration
# -----------------------------------------------------------
nats_url = os.getenv("NATS_URL", "nats://app:secret@localhost:4222") # nats://app:secret@68.183.88.195:4222
nats_chat_recommend_subject = os.getenv("NATS_CHAT_RECOMMEND_SUBJECT", "chat.recommendation.request")
nats_reminder_notification_subject = os.getenv("NATS_REMINDER_NOTIFICATION_SUBJECT", "reminder.notification.request")

# -----------------------------------------------------------
#HF Transformers Cache
# -----------------------------------------------------------
HF_CACHE_DIR = "/models/hf_cache"  # e.g., "/path/to/hf_cache"