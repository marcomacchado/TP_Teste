from flask import Flask, send_from_directory
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

    # Rotas para servir o frontend
    @app.route('/')
    def serve_index():
        return send_from_directory('../frontend', 'index.html')

    @app.route('/<path:filename>')
    def serve_static_files(filename):
        return send_from_directory('../frontend', filename)

    return app
