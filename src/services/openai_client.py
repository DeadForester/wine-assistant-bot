from openai import OpenAI
from src.config import api_key, folder_id

client = OpenAI(
    base_url="https://rest-assistant.api.cloud.yandex.net/v1",
    api_key=api_key,
    project=folder_id
)

model = f"gpt://{folder_id}/qwen3-235b-a22b-fp8/latest"