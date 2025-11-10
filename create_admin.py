import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import create_app function and db, bcrypt from extensions
from src.main import create_app 
from src.extensions import db, bcrypt
from src.models.user import User, UserRole, UserSector
# Import all models to ensure they are known to SQLAlchemy before drop/create
from src.models.ponto import TimeEntry
from src.models.ordem_servico import OrdemServico
from src.models.document import Document

app = create_app() # Create an app instance to work with the app context

def setup_database_and_admin():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all() # Drop existing tables
        print("Creating all tables...")
        db.create_all() # Create tables based on current models
        print("Tables created.")

        # Check if admin already exists (shouldn't after drop_all, but good practice)
        if User.query.filter_by(username="admin").first():
            print("Admin user already exists.")
            return

        # Create admin user
        print("Creating admin user...")
        admin_user = User(
            username="admin",
            email="admin@samabaja.local", # Use a placeholder email
            role=UserRole.GESTAO,
            sector=UserSector.GESTAO,
            is_active=True # Activate admin immediately
        )
        admin_user.set_password("adminpassword") # Use a secure password in a real scenario
        
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully with username 'admin' and password 'adminpassword'.")

if __name__ == "__main__":
    setup_database_and_admin()

