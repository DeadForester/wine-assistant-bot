import json
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

if not os.path.exists(DATA_DIR):
    raise FileNotFoundError(f"Папка данных не найдена: {DATA_DIR}")

folder_id = None
api_key = None

if os.path.exists(os.path.join(PROJECT_ROOT, 'authorized_key.json')):
    try:
        from util.iam_auth import get_iam
        with open(os.path.join(PROJECT_ROOT, 'authorized_key.json')) as f:
            auth_key = json.load(f)
        api_key = get_iam(auth_key['service_account_id'], auth_key['id'], auth_key['private_key'])
        folder_id = auth_key['folder_id']
        print(f"Using IAM Token Auth with folder_id={folder_id}")
    except ImportError:
        pass

if not api_key or not folder_id:
    folder_id = os.environ["folder_id"]
    api_key = os.environ["api_key"]

TELEGRAM_TOKEN = os.environ["tg_token"]