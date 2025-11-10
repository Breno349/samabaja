import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template, g # Import g for context
from flask_login import current_user # Import current_user
from datetime import datetime # Import datetime for footer year

# Import extensions from the new file
from src.extensions import db, login_manager, bcrypt
from src.models.user import User, UserRole # Import User model and UserRole

# Import specific blueprints
from src.routes.auth import auth_bp
from src.routes.ponto import ponto_bp
from src.routes.ordem_servico import ordem_bp
from src.routes.admin import admin_bp
from src.routes.docs import docs_bp
from src.routes.user import user_bp

# Create a main blueprint for general pages
from flask import Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('index.html')

@main_bp.route('/historia')
def historia():
    return render_template('historia.html')

def create_app():
    # Adjust Flask app initialization to use a templates folder
    app = Flask(__name__, 
                static_folder=os.path.join(os.path.dirname(__file__), 'static'),
                template_folder=os.path.join(os.path.dirname(__file__), 'templates')) # Add template_folder

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "a_very_secret_key_that_should_be_in_env" # Use environment variable or default
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'flask_user')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = "auth.login" # Redirect to login page if @login_required fails

    @app.context_processor
    def inject_pending_users():
        """Deixa o contador de pendentes disponível em todos os templates."""
        pending_count = 0
        try:
            if current_user.is_authenticated and current_user.role == UserRole.GESTAO:
                pending_count = User.query.filter_by(role=UserRole.PENDING).count()
        except Exception:
            # Caso a consulta falhe (por exemplo, em páginas sem DB), apenas ignora
            pending_count = 0
        return dict(pending_users=pending_count)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Make current_user and UserRole available to all templates
    @app.context_processor
    def inject_user_and_role():
        return dict(current_user=current_user, UserRole=UserRole, now=datetime.utcnow)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(ponto_bp, url_prefix="/ponto")
    app.register_blueprint(ordem_bp, url_prefix="/ordens")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(docs_bp, url_prefix="/docs")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(main_bp)

    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy before create_all
        from src.models.user import User
        from src.models.ponto import TimeEntry
        from src.models.ordem_servico import OrdemServico
        from src.models.document import Document
        # Ensure all tables are created according to the models
        db.create_all() 

    return app

app = create_app() # Create the app instance

if __name__ == '__main__':
    # db.create_all() is now called within create_app's context
    app.run(host='0.0.0.0', port=5000, debug=True)

