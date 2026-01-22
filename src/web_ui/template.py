def get_admin_list_template(session_ids):
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>🍷 Админка: Заказы</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }}
            h1 {{ color: #5a2d82; }}
            .session-list {{ background: white; padding: 20px; border-radius: 8px; max-width: 600px; }}
            .session-item {{
                padding: 10px;
                margin: 8px 0;
                background: #e8f4fd;
                border-radius: 6px;
                cursor: pointer;
            }}
            .session-item:hover {{
                background: #d0e8fa;
            }}
        </style>
    </head>
    <body>
        <h1>Активные заказы</h1>
        <div class="session-list">
            {"".join(f'<div class="session-item" onclick="window.location=\'/admin/session/{sid}\'"> 🆔 Session ID: <strong>{sid}</strong> </div>' for sid in session_ids) if session_ids else "<p>Нет активных заказов.</p>"}
        </div>
        <script>
            setTimeout(() => location.reload(), 10000);
        </script>
    </body>
    </html>
    '''


def get_session_detail_template(session_id, cart, history):
    cart_html = "".join(
        f'<div class="cart-item">• {item["wine_name"]} ({item["count"]} шт.)</div>'
        for item in cart
    ) if cart else "<p>Корзина пуста</p>"

    history_html = "".join(
        f'''
        <div class="msg">
            <span class="role-{'user' if msg['role'] == 'user' else 'assistant'}">
                [{msg['role']}]:
            </span>
            {msg['content']}
        </div>
        '''
        for msg in history
    )

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Session {session_id} — Заказ</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }}
            h1 {{ color: #5a2d82; }}
            .back {{ margin-bottom: 15px; }}
            .back a {{ text-decoration: none; color: #1976d2; }}
            .section {{ background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            .cart-item {{ margin: 6px 0; font-size: 1.1em; }}
            .history {{ background: #f0f0f0; padding: 12px; border-radius: 6px; }}
            .msg {{ margin: 8px 0; }}
            .role-user {{ color: #1976d2; font-weight: bold; }}
            .role-assistant {{ color: #388e3c; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="back">
            <a href="/admin">← Назад к списку заказов</a>
        </div>
        <h1>Заказ: Session ID {session_id}</h1>
        <div class="section">
            <h2>🛒 Корзина</h2>
            {cart_html}
        </div>
        <div class="section">
            <h2>💬 История диалога</h2>
            <div class="history">{history_html}</div>
        </div>
        <script>
            setTimeout(() => location.reload(), 10000);
        </script>
    </body>
    </html>
    '''
