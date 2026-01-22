from .app import create_app
from .views import register_routes, set_agent

def run_admin_panel(agent, host='127.0.0.1', port=8080):
    set_agent(agent)
    app = create_app()
    register_routes(app)
    print(f"✅ Админка запущена: http://{host}:{port}/admin")
    app.run(host=host, port=port, debug=False)