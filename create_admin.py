"""
Create Admin User Script
========================
Run this once to promote an existing user to admin, OR to create a brand-new admin account.

Usage:
    python create_admin.py

Make sure your .env file is present and DATABASE_URL is configured before running.
"""

import sys
import os

# Add the project root to Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.core.security import get_password_hash

# ─── Configuration ────────────────────────────────────────────────────────────
# Change these values before running the script

ADMIN_EMAIL = "pratik@meetzy.com"
ADMIN_PASSWORD = "pratik@1234"       # Change this to something strong!
ADMIN_NAME = "ViceAdmin"

# ─────────────────────────────────────────────────────────────────────────────


def create_admin():
    # Ensure all tables exist (including the new is_admin column)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()

        if existing:
            # Promote existing user to admin
            if existing.is_admin:
                print(f"✅ '{existing.name}' ({ADMIN_EMAIL}) is already an admin.")
            else:
                existing.is_admin = True
                existing.is_active = True
                db.commit()
                print(f"✅ Promoted existing user '{existing.name}' ({ADMIN_EMAIL}) to admin.")
        else:
            # Create a new admin user
            admin_user = User(
                email=ADMIN_EMAIL,
                password_hash=get_password_hash(ADMIN_PASSWORD),
                name=ADMIN_NAME,
                is_active=True,
                is_verified=True,
                is_admin=True,
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ Admin user created successfully!")
            print(f"   Email:    {ADMIN_EMAIL}")
            print(f"   Password: {ADMIN_PASSWORD}")
            print(f"   Name:     {ADMIN_NAME}")
            print()
            print("⚠️  Please change the password after first login!")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
