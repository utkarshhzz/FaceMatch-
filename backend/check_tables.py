"""
Check what tables exist in database
"""

import asyncio
from sqlalchemy import text
from app.db.session import engine
from app.core.logger import logger


async def check_tables():
    """List all tables in database"""
    
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        tables = result.fetchall()
        
        logger.info(f"✅ Found {len(tables)} tables:")
        for table in tables:
            logger.info(f"  📋 {table[0]}")


if __name__ == "__main__":
    asyncio.run(check_tables())
