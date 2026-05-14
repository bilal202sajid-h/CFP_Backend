#!/usr/bin/env python3
"""Verify new product columns were added"""

from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.database_url)

# Direct SQL query to check all columns
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'products' 
        ORDER BY ordinal_position
    """))
    
    print("\n📋 All Products Table Columns:")
    all_cols = []
    for row in result:
        all_cols.append(row[0])
        print(f"  ✓ {row[0]} ({row[1]})")
    
    print("\n✅ Checking for new columns:")
    if 'material' in all_cols:
        print("  ✓ material - ADDED")
    else:
        print("  ✗ material - MISSING")
        
    if 'dimensions' in all_cols:
        print("  ✓ dimensions - ADDED")
    else:
        print("  ✗ dimensions - MISSING")
        
    if 'stock' in all_cols:
        print("  ✓ stock - ADDED")
    else:
        print("  ✗ stock - MISSING")

print("\n✅ Verification complete!\n")
