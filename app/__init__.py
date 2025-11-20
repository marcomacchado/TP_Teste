from flask import Flask
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

    # Registrar o blueprint de rotas
    from .routes import task_bp
    app.register_blueprint(task_bp, url_prefix='/tasks')

    return app
