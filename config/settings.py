import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

FOLDER_ID = os.getenv("folder_id")
API_KEY = os.getenv("api_key")
TELEGRAM_TOKEN = os.getenv("tg_token")

MODEL_NAME = "qwen3-235b-a22b-fp8"
BASE_URL = "https://rest-assistant.api.cloud.yandex.net/v1"