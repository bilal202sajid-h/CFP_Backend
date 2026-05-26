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


PRODUCT_IMAGES_TABLE = """
CREATE TABLE IF NOT EXISTS product_images (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  product_id bigint NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  image_url text NOT NULL,
  public_id text,
  label text,
  sort_order integer NOT NULL DEFAULT 0,
  is_cover boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
)
"""

PRODUCT_IMAGES_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_product_images_product_id ON product_images(product_id)",
    "CREATE INDEX IF NOT EXISTS idx_product_images_is_cover ON product_images(is_cover)",
]


def run_product_image_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    if "products" not in inspector.get_table_names():
        logger.info("product_image_migrations_skipped reason=products_table_missing")
        return

    with engine.begin() as conn:
        conn.execute(text(PRODUCT_IMAGES_TABLE))
        for statement in PRODUCT_IMAGES_INDEXES:
            conn.execute(text(statement))

        conn.execute(
            text(
                """
                INSERT INTO product_images (product_id, image_url, sort_order, is_cover)
                SELECT p.id, p.image_url, 0, true
                FROM products p
                WHERE p.image_url IS NOT NULL
                  AND p.image_url <> ''
                  AND NOT EXISTS (
                    SELECT 1 FROM product_images pi WHERE pi.product_id = p.id
                  )
                """
            )
        )

    logger.info("product_image_migrations_complete")
