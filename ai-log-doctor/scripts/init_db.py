"""Database initialization script."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../services')))

from shared.database import Base, engine, get_db_context, User
from shared.auth import get_password_hash
from datetime import datetime


def init_db():
    """Initialize database and create tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Create default admin user
    print("Creating default admin user...")
    with get_db_context() as db:
        existing_admin = db.query(User).filter_by(username="admin").first()
        if not existing_admin:
            admin_user = User(
                username="admin",
                email="admin@logdoctor.local",
                hashed_password=get_password_hash("admin"),
                full_name="Administrator",
                role="admin",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            print("Admin user created! (username: admin, password: admin)")
        else:
            print("Admin user already exists!")
    
    print("Database initialization complete!")


if __name__ == "__main__":
    init_db()
