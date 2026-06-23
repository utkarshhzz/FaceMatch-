"""
Forgot-password reset script.

WHAT IT DOES
    Finds a user by email OR employee_id, then OVERWRITES their password_hash
    with a brand-new bcrypt hash for a password you type at the prompt.

WHY "reset" AND NOT "recover"
    Passwords are stored as ONE-WAY bcrypt hashes (see the big comment in
    core/security.py). There is no way to read the original password back
    out of the database — the math cannot be reversed. So "forgot password"
    always means "set a new password," never "tell me the old one."

HOW BCRYPT MAKES THIS SAFE
    Each hash contains a random SALT. Even if two people pick the same
    password, their hashes differ. When we reset, bcrypt generates a fresh
    salt + fresh hash. The OLD hash is simply discarded (overwritten).

USAGE
    cd backend
    python scripts/reset_password.py
    # then answer the prompts: email or employee_id, then new password
"""
import asyncio
import getpass
import sys

# Make `app.*` imports work when running this file directly.
sys.path.insert(0, ".")

from sqlalchemy import select, or_  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import AsyncSessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User  # noqa: E402


async def reset_password(identifier: str, new_password: str) -> bool:
    """Find user by email OR employee_id; overwrite their password hash.

    Returns True on success, False if no user matched.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(or_(User.email == identifier, User.employee_id == identifier))
        )
        user = result.scalar_one_or_none()
        if user is None:
            print(f"\n❌ No user found for '{identifier}'.")
            print("   Check the email/employee_id and that the database has users.")
            return False

        # THIS is the whole "reset": replace the hash with one for the new password.
        # The old hash is gone — but anyone who already has a valid JWT keeps
        # working until it expires (we don't invalidate tokens here).
        user.password_hash = hash_password(new_password)
        await db.commit()

        print(f"\n✅ Password reset successfully for:")
        print(f"   name        : {user.full_name}")
        print(f"   email       : {user.email}")
        print(f"   employee_id : {user.employee_id}")
        print(f"   role        : {user.role}")
        print("\n   You can now log in with the new password.")
        return True


def main() -> None:
    print("=" * 60)
    print("  FaceMatch — Password Reset Tool")
    print("=" * 60)
    print("\nIdentify the user by their EMAIL or EMPLOYEE_ID.\n")

    identifier = input("Email or Employee ID: ").strip()
    if not identifier:
        print("Identifier cannot be empty.")
        return

    # getpass hides the typed password in the terminal (no echo).
    new_password = getpass.getpass("New password (min 6 chars): ")
    if len(new_password) < 6:
        print("Password too short.")
        return

    confirm = getpass.getpass("Confirm new password: ")
    if new_password != confirm:
        print("Passwords do not match. Aborting.")
        return

    # Run the async logic.
    ok = asyncio.run(reset_password(identifier, new_password))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
