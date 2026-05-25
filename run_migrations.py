#!/usr/bin/env python3
"""Apply product table migrations. Usage: python run_migrations.py"""

from app.db.migrations import run_product_migrations
from app.db.session import engine


def main() -> None:
    run_product_migrations(engine)
    print("Product migrations applied successfully.")


if __name__ == "__main__":
    main()
