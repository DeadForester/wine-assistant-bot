from flask import abort
from ..web_ui.template import get_admin_list_template, get_session_detail_template
from src.domain.cart_manager import carts

# Глобальная ссылка на агент (устанавливается извне)
web_agent = None

def set_agent(agent):
    global web_agent
    web_agent = agent

def register_routes(app):
    @app.route('/admin')
    def admin_panel():
        if web_agent is None:
            return "<h2>Агент не инициализирован</h2>", 500

        session_ids = [
            sid for sid in web_agent.user_sessions
            if carts.get(sid)
        ]
        session_ids.sort(key=str)
        return get_admin_list_template(session_ids)

    @app.route('/admin/session/<int:session_id>')
    def session_detail(session_id):
        if web_agent is None:
            return "<h2>Агент не инициализирован</h2>", 500

        if session_id not in web_agent.user_sessions:
            abort(404)

        cart = carts.get(session_id, [])
        if not cart:
            abort(404)

        history = web_agent.user_sessions[session_id].get('history', [])
        return get_session_detail_template(session_id, cart, history)