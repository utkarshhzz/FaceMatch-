"""
Create tables with new schema and seed admin user
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.core.config import settings

def recreate_tables():
    """Drop and recreate all tables"""
    # Use sync engine
    sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
    engine = create_engine(sync_url)
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("✅ Dropped all tables")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Created all tables with new schema")
    
    return engine

def seed_admin_user(engine):
    """Create root admin user from .env"""
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == settings.ROOT_ADMIN_EMAIL).first()
        
        if not admin:
            admin = User(
                employee_id=settings.ROOT_ADMIN_ID,
                full_name="Root Administrator",
                email=settings.ROOT_ADMIN_EMAIL,
                hashed_password=hash_password(settings.ROOT_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            
            db.add(admin)
            db.commit()
            
            print("\n✅ Root Admin created:")
            print(f"   Employee ID: {settings.ROOT_ADMIN_ID}")
            print(f"   Email: {settings.ROOT_ADMIN_EMAIL}")
            print(f"   Password: (from .env - keep it safe!)")
            print(f"   Role: ADMIN")
        else:
            print("\n✅ Root admin already exists")
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 Recreating database schema...\n")
    engine = recreate_tables()
    seed_admin_user(engine)
    print("\n✅ Database setup complete!")
