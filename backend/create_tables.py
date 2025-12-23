"""
Create all database tables
"""

import asyncio
from app.db.init_db import init_db
from app.core.logger import logger

# Import all models so SQLAlchemy knows about them
from app.models import User, Face, Encoding, AuditLog


async def create_all_tables():
    """Create all database tables"""
    
    logger.info("Creating database tables...")
    
    try:
        await init_db()
        logger.info("✅ All tables created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(create_all_tables())
