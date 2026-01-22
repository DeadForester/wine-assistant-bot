carts = {}

def add_to_cart(session_id, wine_name, count):
    if session_id not in carts:
        carts[session_id] = []
    carts[session_id].append({"wine_name": wine_name, "count": count})
    return f"Вино {wine_name} добавлено в корзину, число бутылок: {count}"

def show_cart(session_id):
    items = carts.get(session_id, [])
    if not items:
        return "Корзина пуста"
    lines = [f"{item['wine_name']}, число бутылок: {item['count']}" for item in items]
    return "В корзине находятся следующие вина:\n" + "\n".join(lines)