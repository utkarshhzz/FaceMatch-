"""
FaceMatch++ System Health Check
Comprehensive test script to verify all features and services
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.logger import logger
from app.utils.redis_cache import redis_cache
from app.utils.email_service import email_service
from app.db.session import AsyncSessionLocal
from sqlalchemy import select, text
from app.models.user import User
from app.core.security import hash_password, verify_password

class HealthChecker:
    def __init__(self):
        self.results = {}
        self.passed = 0
        self.failed = 0
    
    def test(self, name: str):
        """Decorator for test functions"""
        def wrapper(func):
            async def inner():
                try:
                    print(f"\n🔍 Testing: {name}...")
                    result = await func()
                    if result:
                        print(f"   ✅ PASSED: {name}")
                        self.passed += 1
                        self.results[name] = "PASSED"
                    else:
                        print(f"   ❌ FAILED: {name}")
                        self.failed += 1
                        self.results[name] = "FAILED"
                    return result
                except Exception as e:
                    print(f"   ❌ ERROR in {name}: {str(e)}")
                    self.failed += 1
                    self.results[name] = f"ERROR: {str(e)}"
                    return False
            return inner
        return wrapper

checker = HealthChecker()

@checker.test("Configuration Loading")
async def test_config():
    """Test if configuration is loaded properly"""
    assert settings.PROJECT_NAME == "FaceMatch++", "Project name mismatch"
    assert settings.DATABASE_URL, "Database URL not configured"
    assert settings.REDIS_URL, "Redis URL not configured"
    assert settings.SECRET_KEY, "Secret key not configured"
    print(f"      Database: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
    print(f"      Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    print(f"      Environment: {settings.ENVIRONMENT}")
    return True

@checker.test("Database Connection")
async def test_database():
    """Test database connectivity"""
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT 1"))
            assert result.scalar() == 1, "Database query failed"
            
            # Check tables exist
            result = await db.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name IN ('users', 'faces', 'attendances', 'encodings')
            """))
            table_count = result.scalar()
            print(f"      Found {table_count} tables (expected 4)")
            
            # Check user count
            result = await db.execute(select(User))
            users = result.scalars().all()
            print(f"      Total users: {len(users)}")
            
            return True
    except Exception as e:
        print(f"      Database error: {str(e)}")
        return False

@checker.test("Redis Connection")
async def test_redis():
    """Test Redis connectivity"""
    if not redis_cache.is_available():
        print("      Redis not available")
        return False
    
    # Test set/get
    test_key = "test:health_check"
    test_value = "test_value_123"
    
    try:
        redis_cache.redis_client.set(test_key, test_value, ex=10)
        retrieved = redis_cache.redis_client.get(test_key)
        
        if retrieved == test_value:
            print("      Redis read/write working")
            redis_cache.redis_client.delete(test_key)
            return True
        else:
            print(f"      Redis value mismatch: {retrieved} != {test_value}")
            return False
    except Exception as e:
        print(f"      Redis error: {str(e)}")
        return False

@checker.test("Email Service Configuration")
async def test_email_config():
    """Test email service configuration"""
    smtp_configured = bool(
        email_service.smtp_user and 
        email_service.smtp_password and 
        email_service.from_email
    )
    
    if smtp_configured:
        print(f"      SMTP Host: {email_service.smtp_host}:{email_service.smtp_port}")
        print(f"      From: {email_service.from_name} <{email_service.from_email}>")
        print("      ✓ Email service configured")
    else:
        print("      ⚠ Email service not configured (optional)")
    
    return True  # Email is optional

@checker.test("Password Hashing")
async def test_password_security():
    """Test password hashing and verification"""
    test_password = "TestPassword123!"
    hashed = hash_password(test_password)
    
    # Verify correct password
    if not verify_password(test_password, hashed):
        print("      Failed to verify correct password")
        return False
    
    # Verify incorrect password
    if verify_password("WrongPassword", hashed):
        print("      Incorrectly verified wrong password")
        return False
    
    print("      Password hashing and verification working")
    return True

@checker.test("Face Recognition Models")
async def test_face_models():
    """Test if face recognition models can be loaded"""
    try:
        from app.utils.face_detector import face_detector
        from app.utils.face_encoder import face_encoder
        
        print(f"      Face Detector: {face_detector.detector_backends}")
        print(f"      Face Encoder: {face_encoder.model_name}")
        print("      ✓ Models initialized")
        return True
    except Exception as e:
        print(f"      Model loading error: {str(e)}")
        return False

@checker.test("File System Permissions")
async def test_file_system():
    """Test file system access"""
    test_dirs = [
        "./data/uploads",
        "./data/temp",
        "./data/faces",
        "./logs"
    ]
    
    all_ok = True
    for dir_path in test_dirs:
        os.makedirs(dir_path, exist_ok=True)
        
        # Test write permission
        test_file = os.path.join(dir_path, ".test_write")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print(f"      ✓ {dir_path}: writable")
        except Exception as e:
            print(f"      ✗ {dir_path}: {str(e)}")
            all_ok = False
    
    return all_ok

@checker.test("Root Admin Exists")
async def test_root_admin():
    """Test if root admin account exists"""
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User).where(User.employee_id == settings.ROOT_ADMIN_ID)
            )
            admin = result.scalar_one_or_none()
            
            if admin:
                print(f"      Admin found: {admin.full_name} ({admin.email})")
                print(f"      Role: {admin.role.value}")
                print(f"      Active: {admin.is_active}")
                return True
            else:
                print("      ⚠ Root admin not found - run setup_admin_system.py")
                return False
    except Exception as e:
        print(f"      Error checking admin: {str(e)}")
        return False

async def run_all_tests():
    """Run all health checks"""
    print("="*70)
    print("🚀 FaceMatch++ System Health Check")
    print("="*70)
    
    # Run tests
    await test_config()
    await test_database()
    await test_redis()
    await test_email_config()
    await test_password_security()
    await test_face_models()
    await test_file_system()
    await test_root_admin()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {checker.passed}")
    print(f"❌ Failed: {checker.failed}")
    print(f"📈 Success Rate: {checker.passed}/{checker.passed + checker.failed} ({100*checker.passed/(checker.passed + checker.failed):.1f}%)")
    print("="*70)
    
    if checker.failed == 0:
        print("\n🎉 All tests passed! System is healthy.")
        return 0
    else:
        print(f"\n⚠️  {checker.failed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
