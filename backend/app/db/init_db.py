"""
Startup database initialization: create tables + seed the root admin.

Concept — "idempotent" startup:
  create_all() only creates tables that DON'T already exist — it never
  drops or alters existing ones, so running it every startup is safe.
  The admin seeding also checks "does this admin already exist?" first,
  so it won't duplicate or reset on every restart.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import Base, AsyncSessionLocal
from app.core.security import hash_password
from app.core.logging import app_logger

# Import models so they register with Base.metadata before create_all runs.
from app.models import User, Face, FaceEncoding, Attendance  # noqa: F401


async def init_db() -> None:
    """Create all tables (if missing) and ensure a root admin exists."""
    # Create tables using the engine's begin() context.
    # run_sync lets us call the SYNC create_all inside an async connection.
    from app.core.database import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app_logger.info("Database tables ensured")

    # Seed root admin.
    async with AsyncSessionLocal() as db:
        await _seed_root_admin(db)


async def _seed_root_admin(db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.email == settings.ROOT_ADMIN_EMAIL))
    if result.scalar_one_or_none():
        app_logger.info("Root admin already exists, skipping seed")
        return

    admin = User(
        email=settings.ROOT_ADMIN_EMAIL,
        employee_id=settings.ROOT_ADMIN_ID,
        full_name="Administrator",
        password_hash=hash_password(settings.ROOT_ADMIN_PASSWORD),
        role="admin",
    )
    db.add(admin)
    await db.commit()
    app_logger.info("Seeded root admin: {}", settings.ROOT_ADMIN_EMAIL)
