from flask import Flask, send_from_directory
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
# Inicializando a db
db = SQLAlchemy()

def create_app(config_name=None):
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    if config_name == 'testing':
        app.config.from_mapping(
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:',
            TESTING=True,
            DEBUG=False
        )
    else:
        app.config.from_mapping(
            SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db'
        )

    db.init_app(app)

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
    
    with app.app_context():
        db.create_all()

    return app
