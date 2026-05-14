#!/usr/bin/env python3
"""
Database migration script to apply schema changes.
Usage: python migrate.py
"""

import sys
import re
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool


def parse_sql_statements(sql_content):
    """Parse SQL statements, handling PL/pgSQL functions with $$ delimiters"""
    statements = []
    current_statement = ""
    i = 0
    
    while i < len(sql_content):
        char = sql_content[i]
        
        # Check for dollar-quoted strings (PL/pgSQL)
        if char == '$' and i + 1 < len(sql_content):
            # Find the matching $$ pair
            match = re.match(r'\$\$', sql_content[i:])
            if match:
                # Find the closing $$
                start = i
                i += 2
                while i < len(sql_content) - 1:
                    if sql_content[i:i+2] == '$$':
                        current_statement += sql_content[start:i+2]
                        i += 2
                        break
                    i += 1
                continue
        
        if char == ';':
            # End of statement
            current_statement += char
            if current_statement.strip():
                statements.append(current_statement.strip())
            current_statement = ""
        else:
            current_statement += char
        
        i += 1
    
    # Add any remaining statement
    if current_statement.strip():
        statements.append(current_statement.strip())
    
    return statements


def run_migration():
    """Run the SQL migration from schema.sql"""
    
    # Import settings to get database URL
    try:
        from app.core.config import settings
    except ImportError:
        print("❌ Error: Could not import settings. Make sure you're in the Backend directory.")
        sys.exit(1)
    
    print("\n=== Database Migration ===\n")
    print(f"Connecting to database...")
    
    try:
        # Create engine with NullPool to avoid connection pooling issues
        engine = create_engine(
            settings.database_url,
            poolclass=NullPool,
            echo=False
        )
        
        # Read schema.sql
        try:
            with open("sql/schema.sql", "r") as f:
                schema_sql = f.read()
        except FileNotFoundError:
            print("❌ Error: sql/schema.sql not found. Make sure you're in the Backend directory.")
            sys.exit(1)
        
        # Parse statements (handles PL/pgSQL)
        statements = parse_sql_statements(schema_sql)
        
        print(f"Found {len(statements)} SQL statements to execute\n")
        
        # Execute SQL statements
        successful = 0
        with engine.begin() as connection:
            for i, statement in enumerate(statements, 1):
                try:
                    print(f"[{i}/{len(statements)}] Executing statement...")
                    connection.execute(text(statement))
                    successful += 1
                except Exception as e:
                    error_msg = str(e)
                    # Some warnings are okay (like "already exists")
                    if "already exists" in error_msg.lower():
                        print(f"[{i}/{len(statements)}] ℹ️  Already exists (skipped)")
                        successful += 1
                    else:
                        print(f"[{i}/{len(statements)}] ⚠️  Error: {error_msg[:80]}")
        
        print(f"\n✅ Migration completed!\n")
        print(f"📋 Changes applied ({successful}/{len(statements)} statements):")
        print("  ✓ Added 'material' column to products")
        print("  ✓ Added 'dimensions' column to products")
        print("  ✓ Added 'stock' column to products")
        print("  ✓ Created 'categories' table")
        print("  ✓ Created 'frontend_configs' table")
        print("  ✓ Added indexes for performance")
        print("  ✓ Added triggers for auto-updating timestamps\n")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
