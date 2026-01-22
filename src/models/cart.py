from pydantic import BaseModel, Field
from src.domain.cart_manager import add_to_cart, show_cart, carts


class AddToCart(BaseModel):
    wine_name: str = Field(default=None)
    count: int = Field(default=1)

    def process(self, session_id):
        if session_id not in carts:
            carts[session_id] = []
        carts[session_id].append(self)
        print(f"[DEBUG] Добавлено в корзину для {session_id}: {self.wine_name} (всего: {len(carts[session_id])})")
        return f"Вино {self.wine_name} добавлено в корзину, число бутылок: {self.count}"

class ShowCart(BaseModel):
    def process(self, session_id):
        print(f"[DEBUG] ShowCart вызван для session_id={session_id}")
        print(f"[DEBUG] Доступные сессии в carts: {list(carts.keys())}")
        print(f"[DEBUG] Содержимое корзины для {session_id}: {carts.get(session_id)}")

        try:
            cart_items = carts.get(session_id, [])
            if not cart_items:
                return "Корзина пуста"

            lines = []
            for item in cart_items:
                wine_name = getattr(item, 'wine_name', '[неизвестное вино]')
                count = getattr(item, 'count', 1)
                lines.append(f"{wine_name}, число бутылок: {count}")

            return "В корзине находятся следующие вина:\n" + "\n".join(lines)

        except Exception as e:
            print(f"[ERROR] ShowCart.process завершился с исключением: {e}")
            return "Не удалось загрузить содержимое корзины. Попробуйте позже."

class Handover(BaseModel):
    reason: str = Field(default="не указана")

    def process(self, session_id):
        global handover
        handover = True
        return f"Я побежала вызывать оператора, ваш session_id={session_id}, причина: {self.reason}"