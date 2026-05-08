#!/usr/bin/env python3
"""
Script to create an admin user in the database.
Usage: python create_admin.py
"""

import secrets
import string

from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.admin_user import AdminUser


def generate_password(length=20):
    """Generate a secure random password (max 72 chars for bcrypt)."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(min(length, 72)))
    return password


def create_admin():
    """Create a new admin user."""
    db = SessionLocal()
    
    try:
        print("\n=== Create Admin User ===\n")
        
        # Get username
        username = input("Enter admin username: ").strip()
        if not username:
            print("❌ Username cannot be empty!")
            return
        
        # Check if user already exists
        existing_user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if existing_user:
            print(f"❌ Admin user '{username}' already exists!")
            return
        
        # Generate password
        password = generate_password()
        
        # Create new admin user
        hashed_password = hash_password(password)
        new_admin = AdminUser(
            username=username,
            password_hash=hashed_password,
            is_active=True
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        print(f"\n✅ Admin user created successfully!")
        print(f"\n📋 SAVE THESE CREDENTIALS:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"\n   ID: {new_admin.id}")
        print(f"   Created at: {new_admin.created_at}")
        
    except IntegrityError:
        db.rollback()
        print("❌ Error: Username already exists or database constraint violation!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
