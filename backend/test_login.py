"""Test login credentials"""
import asyncio
from sqlalchemy import select
from app.core.security import verify_password
from app.models.user import User
from app.db.session import AsyncSessionLocal
from app.core.config import settings

async def test_login():
    async with AsyncSessionLocal() as db:
        # Find user
        result = await db.execute(
            select(User).where(User.employee_id == '245816470')
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User not found!")
            return
        
        print(f"✅ User found: {user.email}")
        print(f"   Full name: {user.full_name}")
        print(f"   Role: {user.role}")
        print(f"   Is active: {user.is_active}")
        print(f"   Hash (first 50 chars): {user.hashed_password[:50]}")
        
        # Test password from settings
        password = settings.ROOT_ADMIN_PASSWORD
        print(f"\n🔐 Testing password: '{password}'")
        
        is_valid = verify_password(password, user.hashed_password)
        
        if is_valid:
            print("✅ Password verification PASSED!")
        else:
            print("❌ Password verification FAILED!")
            
            # Try some variations
            print("\n Testing variations:")
            for test_pwd in ['Admin@123', 'admin@123', 'ADMIN@123', ' Admin@123', 'Admin@123 ']:
                result = verify_password(test_pwd, user.hashed_password)
                print(f"  '{test_pwd}': {result}")

if __name__ == "__main__":
    asyncio.run(test_login())
