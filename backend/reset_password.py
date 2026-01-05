"""
Reset user password
"""
import asyncio
from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash

async def reset_password():
    email = "unofficialutkarsh.06@gmail.com"
    new_password = "password123"
    
    async with AsyncSessionLocal() as db:
        # Find user
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User {email} not found")
            return
        
        # Update password
        hashed_password = get_password_hash(new_password)
        await db.execute(
            update(User)
            .where(User.email == email)
            .values(hashed_password=hashed_password)
        )
        await db.commit()
        
        print(f"✅ Password reset successfully!")
        print(f"📧 Email: {email}")
        print(f"🔑 New Password: {new_password}")

if __name__ == "__main__":
    asyncio.run(reset_password())
