from pydantic import BaseModel, Field
from typing import Dict
import sys

carts: Dict[str, list] = {}

class Handover(BaseModel):
    """Эта функция позволяет передать диалог человеку-оператору поддержки"""

    reason: str = Field(
        description="Причина для вызова оператора", default="не указана"
    )

    def process(self, session_id):
        global handover
        handover = True
        return f"Я побежала вызывать оператора, ваш {session_id=}, причина: {self.reason}"


class ShowCart(BaseModel):
    """Эта функция позволяет показать содержимое корзины"""

    def process(self, session_id):
        if session_id not in carts or len(carts[session_id]) == 0:
            return "Корзина пуста"
        return "В корзине находятся следующие вина:\n" + "\n".join(
            [f"{x.wine_name}, число бутылок: {x.count}" for x in carts[session_id]]
        )

class AddToCart(BaseModel):
    """Эта функция позволяет положить или добавить вино в корзину"""

    wine_name: str = Field(
        description="Точное название вина, чтобы положить в корзину", default=None
    )
    count: int = Field(
        description="Количество бутылок вина, которое нужно положить в корзину",
        default=1,
    )

    def process(self, session_id):
        if session_id not in carts:
            carts[session_id] = []
        carts[session_id].append(self)
        return f"Вино {self.wine_name} добавлено в корзину, число бутылок: {self.count}"