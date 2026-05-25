"""Lightweight SQL migrations run on API startup (safe to re-run)."""

import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


logger = logging.getLogger(__name__)

PRODUCT_COLUMN_STATEMENTS = [
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS material text",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS dimensions text",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS stock integer NOT NULL DEFAULT 0",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS is_admin_uploaded boolean NOT NULL DEFAULT false",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS article_number text NOT NULL DEFAULT ''",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS price text NOT NULL DEFAULT '0'",
]

PRODUCT_INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_products_article_number ON products(article_number)",
    "CREATE INDEX IF NOT EXISTS idx_products_is_admin_uploaded ON products(is_admin_uploaded)",
]

ENSURE_PRICE_IS_TEXT = """
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = current_schema()
      AND table_name = 'products'
      AND column_name = 'price'
      AND data_type NOT IN ('text', 'character varying')
  ) THEN
    ALTER TABLE products ALTER COLUMN price TYPE text USING price::text;
  END IF;
END $$;
"""


def run_product_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    if "products" not in inspector.get_table_names():
        logger.info("product_migrations_skipped reason=products_table_missing")
        return

    with engine.begin() as conn:
        for statement in PRODUCT_COLUMN_STATEMENTS:
            conn.execute(text(statement))
        conn.execute(text(ENSURE_PRICE_IS_TEXT))
        for statement in PRODUCT_INDEX_STATEMENTS:
            conn.execute(text(statement))

    logger.info("product_migrations_complete")
