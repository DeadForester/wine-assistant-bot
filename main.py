from src.config import DATA_DIR
from src.models.cart import AddToCart, Handover, ShowCart
from src.models.wine_search import SearchWinePriceList
from src.services.vector_store import setup_vector_store
from src.agent.wine_agent import Agent
from src.bot.telegram_bot import run_telegram_bot

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
используй AddToCart. Если пользователь просит показать, посмотреть, отобразить, рассказать о содержимом корзины — обязательно вызови функцию ShowCart. Никогда не отвечай на такие вопросы без вызова этой функции. Все названия вин, цветов, кислотности
пиши на русском языке.
Если что-то непонятно, то лучше уточни информацию у пользователя. Общайся достаточно короткими 
разговорными фразами, не используй перечисления, списки, длинные выдержки текста.
"""

if __name__ == "__main__":
    vector_store = setup_vector_store()

    search_tool = {
        "type": "file_search",
        "vector_store_ids": [vector_store.id],
        "max_num_results": 5
    }

    mcp_wine_tool = {
        "type": "mcp",
        "server_label": "Wine-Shop",
        "server_description": "Функция для запроса цен на вино в винном магазине",
        "server_url": "http://localhost:3000/sse",
        "require_approval": "never",
    }

    def make_function_tool(cls):
        return {
            "type": "function",
            "name": cls.__name__,
            "description": cls.__doc__ or "",
            "parameters": cls.model_json_schema(),
        }

    wine_agent = Agent(
        instruction=instruction,
        tools=[
            search_tool,
            SearchWinePriceList,
            AddToCart,
            Handover,
            ShowCart,
        ],
        tool_choice='auto'
    )

    run_telegram_bot(wine_agent)