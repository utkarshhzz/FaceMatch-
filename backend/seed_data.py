"""
Insert sample data for testing
"""

import asyncio
from app.db.session import AsyncSessionLocal
from app.models import User, UserRole
from app.core.security import hash_password
from app.core.logger import logger


async def seed_database():
    """Insert sample users"""
    
    async with AsyncSessionLocal() as db:
        try:
            # Create admin user
            admin = User(
                email="admin@facematch.com",
                hashed_password=hash_password("Admin123!"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            
            # Create regular user
            user = User(
                email="john@email.com",
                hashed_password=hash_password("Pass123!"),
                full_name="John Doe",
                role=UserRole.USER,
                is_active=True,
                is_verified=True
            )
            
            db.add(admin)
            db.add(user)
            
            await db.commit()
            await db.refresh(admin)
            await db.refresh(user)
            
            logger.info(f"✅ Created admin user (ID: {admin.id})")
            logger.info(f"   Email: {admin.email} | Password: Admin123!")
            logger.info(f"✅ Created regular user (ID: {user.id})")
            logger.info(f"   Email: {user.email} | Password: Pass123!")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to seed data: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
