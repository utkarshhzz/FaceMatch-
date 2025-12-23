"""
Test querying data from database
"""

import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models import User
from app.core.logger import logger


async def test_queries():
    """Test various database queries"""
    
    async with AsyncSessionLocal() as db:
        
        # Get all users
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        logger.info(f"✅ Found {len(users)} users:")
        for user in users:
            logger.info(f"  👤 {user.full_name} ({user.email}) - Role: {user.role.value}")
        
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == "admin@facematch.com")
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            logger.info(f"\n✅ Found admin: {admin.full_name}")
            logger.info(f"   Created at: {admin.created_at}")
            logger.info(f"   Updated at: {admin.updated_at}")


if __name__ == "__main__":
    asyncio.run(test_queries())
