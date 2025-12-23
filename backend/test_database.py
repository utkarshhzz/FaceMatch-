import asyncio
from sqlalchemy import text
from app.db.session import engine
from app.core.logger import logger

async def test_connection():
    try:
        async with engine.begin() as conn:
            #Execute simple query
            result = await conn.execute(text("SELECT version()"))
            row = result.fetchone()
            version = row[0] if row else "Unknown"
            
            logger.info(f"✅ Connected to PostgreSQL!")
            logger.info(f"Version: {version}")
            #test database name
            
            result = await conn.execute(text("SELECT current_database()"))
            row = result.fetchone()
            db_name = row[0] if row else "Unknown"
            logger.info(f"Database: {db_name}")
            
            return True
    
    except Exception as e:
        logger.error(f"Connection failed {e}")
        return False
    
if __name__=="__main__":
    asyncio.run(test_connection())