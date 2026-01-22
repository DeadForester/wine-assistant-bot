from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['ENV'] = 'development'
    return app