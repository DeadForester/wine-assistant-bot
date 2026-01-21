import os
import json
from config import FOLDER_ID, API_KEY, PROJECT_ROOT, TELEGRAM_TOKEN
from auth import get_iam
from services import create_vector_store, upload_text_files, upload_food_wine_table, Agent
from models import AddToCart, Handover, ShowCart
from bot import run_telegram_bot

auth_file = os.path.join(PROJECT_ROOT, 'authorized_key.json')
if os.path.exists(auth_file):
    with open(auth_file) as f:
        auth_key = json.load(f)
    API_KEY = get_iam(auth_key['service_account_id'], auth_key['id'], auth_key['private_key'])
    FOLDER_ID = auth_key['folder_id']

vector_store = create_vector_store()
upload_text_files(vector_store.id)
upload_food_wine_table(vector_store.id)

mcp_wine_tool = {
    "type": "mcp",
    "server_label": "Wine-Shop",
    "server_description": "Функция для запроса цен на вино в винном магазине",
    "server_url": "http://localhost:3000/sse",
    "require_approval": "never",
}

mcp_rest_tool = {
    "type": "mcp",
    "server_label": "Restaurant-Menu",
    "server_description": "Получить меню блюд и напитков ресторана",
    "server_url": "http://localhost:3001/sse",
    "require_approval": "never",
}

search_tool = {
    "type": "file_search",
    "vector_store_ids": [vector_store.id],
    "max_num_results": 5
}

instruction = """
Ты - опытный сомелье, продающий вино в магазине. Твоя задача - отвечать на вопросы пользователя
про вина, рекомендовать лучшие вина к еде, а также искать вина в прайс-листе нашего магазина,
а также проактивно предлагать пользователю приобрести вина, отвечающие его потребностям. В ответ
на сообщение /start поинтересуйся, что нужно пользователю, предложи ему какой-то
интересный вариант сочетания еды и вине, и попытайся продать ему вино.
Посмотри на всю имеющуюся в твоем распоряжении информацию
и выдай одну или несколько лучших рекомендаций.
Если вопрос касается конкретных вин или цены, то вызови функцию MCP-сервера Wine-Shop.
Для передачи управления оператору - вызови фукцию Handover. Для добавления вина в корзину
используй AddToCart. Для просмотра корзины: ShowCart. Все названия вин, цветов, кислотности
пиши на русском языке.
Если что-то непонятно, то лучше уточни информацию у пользователя. Общайся достаточно короткими 
разговорными фразами, не используй перечисления, списки, длинные выдержки текста.
"""

agent = Agent(
    instruction=instruction,
    tools=[search_tool, AddToCart, Handover, ShowCart]
)

if __name__ == "__main__":
    run_telegram_bot(agent)