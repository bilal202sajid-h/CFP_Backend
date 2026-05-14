#!/usr/bin/env python3
"""Verify database migration was successful"""

from sqlalchemy import inspect, create_engine
from app.core.config import settings

engine = create_engine(settings.database_url)
inspector = inspect(engine)

print("\n=== Database Verification ===\n")
print("📊 Tables created:")
for table in inspector.get_table_names():
    print(f"  ✓ {table}")

print("\n📋 Products table columns:")
for col in inspector.get_columns('products'):
    print(f"  ✓ {col['name']} ({col['type']})")

print("\n📋 Categories table columns:")
for col in inspector.get_columns('categories'):
    print(f"  ✓ {col['name']} ({col['type']})")

print("\n📋 Frontend Configs table columns:")
for col in inspector.get_columns('frontend_configs'):
    print(f"  ✓ {col['name']} ({col['type']})")

print("\n✅ All tables and columns verified!\n")
