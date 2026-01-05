"""
Test login to debug the issue
"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import verify_password

async def test_login():
    email = "unofficialutkarsh.06@gmail.com"
    
    # Test different password possibilities
    test_passwords = [
        input("Enter the password you're trying: ").strip()
    ]
    
    async with AsyncSessionLocal() as db:
        # Find user
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User {email} not found in database")
            return
        
        print(f"\n✅ User found: {user.full_name}")
        print(f"📧 Email: {user.email}")
        print(f"🔐 Hashed password in DB: {user.hashed_password[:50]}...")
        print(f"✓ Active: {user.is_active}")
        print(f"✓ Verified: {user.is_verified}")
        
        print("\n🔍 Testing password...")
        for password in test_passwords:
            result = verify_password(password, user.hashed_password)
            print(f"   Password '{password}': {'✅ CORRECT' if result else '❌ WRONG'}")
            
            if result:
                print("\n🎉 Password is correct! Login should work.")
                print(f"\nUse these credentials:")
                print(f"Email: {email}")
                print(f"Password: {password}")
                return

        print("\n❌ None of the passwords matched.")
        print("\nWould you like me to reset it? (The reset script is ready)")

if __name__ == "__main__":
    asyncio.run(test_login())
