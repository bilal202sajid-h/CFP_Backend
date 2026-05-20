#!/usr/bin/env python3
"""
Safe helper to delete all rows from the `products` table.

Usage:
  # dry-run (default) - shows count but does NOT delete
  python scripts/delete_all_products.py --dry-run

  # actually delete (use on the server where DATABASE_URL points to prod)
  python scripts/delete_all_products.py --yes

The script uses the project's `SessionLocal` and `Product` model.
Be absolutely sure you run with `--yes` only in the intended environment.
"""
import sys
import os
from typing import Optional

def main(argv: Optional[list[str]] = None):
    argv = argv or sys.argv[1:]
    do_delete = False
    if '--yes' in argv:
        do_delete = True

    # Discover DB session from project
    try:
        # Import here so script can be run from repo root
        from app.db.session import SessionLocal
        from app.models.product import Product
    except Exception as e:
        print("Failed to import project DB session or models:", e)
        print("Make sure to run this from the project root and activate the venv.")
        return 2

    db = SessionLocal()
    try:
        count = db.query(Product).count()
        print(f"Products in DB: {count}")
        if not do_delete:
            print("Dry-run mode. No rows were deleted. To delete, re-run with --yes in the target environment.")
            return 0

        # Confirm again in interactive mode (only if running on a tty)
        if do_delete:
            confirm = os.environ.get('CONFIRM_DELETE')
            if not confirm and sys.stdin.isatty():
                resp = input("Type DELETE to permanently remove all products: ")
                if resp != 'DELETE':
                    print("Aborted.")
                    return 1
            elif confirm != '1' and not sys.stdin.isatty():
                print("Non-interactive shell and CONFIRM_DELETE not set. To proceed, set CONFIRM_DELETE=1 and re-run with --yes")
                return 1

        deleted = db.query(Product).delete()
        db.commit()
        print(f"Deleted {deleted} products.")
        return 0

    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
