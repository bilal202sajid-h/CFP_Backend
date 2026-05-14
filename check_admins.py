#!/usr/bin/env python3
"""Check if any admin users exist in the database"""

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.database_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, username, is_active, created_at FROM admin_users"))
    
    admins = result.fetchall()
    
    print("\n=== Admin Users Check ===\n")
    
    if admins:
        print(f"✅ Found {len(admins)} admin user(s):\n")
        for admin in admins:
            print(f"  ID: {admin[0]}")
            print(f"  Username: {admin[1]}")
            print(f"  Active: {admin[2]}")
            print(f"  Created: {admin[3]}")
            print()
    else:
        print("❌ No admin users found in database.\n")
        print("You need to create an admin user first.")
        print("Run: python create_admin.py\n")
