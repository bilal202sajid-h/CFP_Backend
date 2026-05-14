# Chiniot Furniture Point Backend

FastAPI backend for the Chiniot Furniture Point storefront.

## What this backend provides

- JWT-based admin login at `POST /admin`
- Admin CRUD for collections and products
- Public read endpoints for collections and products
- Supabase Postgres schema for the database

## Environment variables

Create a `.env` file from `.env.example` and set:

- `DATABASE_URL` - Supabase Postgres connection string
- `JWT_SECRET_KEY` - secret used to sign admin tokens
- `JWT_ALGORITHM` - defaults to `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES` - defaults to `120`
- Cloudinary config for image storage:
	- `CLOUDINARY_URL` (recommended), or
	- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
	- `CLOUDINARY_UPLOAD_FOLDER` - defaults to `chiniot-furniture/products`

## Run locally

```bash
pip install -r requirements.txt
python run.py
```

## Folder structure

- `app/core` - settings and security helpers
- `app/db` - database base and session wiring
- `app/models` - SQLAlchemy models
- `app/schemas` - Pydantic request and response schemas
- `app/crud` - core database logic
- `app/api/endpoints` - route handlers
- `run.py` - project entrypoint

## Database

Run `sql/schema.sql` in your Supabase SQL editor to create the tables.

You also need at least one admin user in `admin_users`. Insert the first admin from the Supabase SQL editor or dashboard with a hashed password.

## API outline

- `POST /admin` - admin login
- `GET /admin` - login instructions
- `GET /admin/me` - current admin profile
- `GET /products` - public product list
- `GET /products/{id}` - public product detail
- `GET /collections` - public collections list
- `GET /collections/{id}` - public collection detail
- `POST /admin/products` - create product
- `PATCH /admin/products/{id}` - update product
- `DELETE /admin/products/{id}` - delete product
- `POST /admin/uploads/product-image` - upload image to Cloudinary (admin auth required)
- `DELETE /admin/uploads/product-image?public_id=...` - delete image from Cloudinary (admin auth required)
- `POST /admin/collections` - create collection
- `PATCH /admin/collections/{id}` - update collection
- `DELETE /admin/collections/{id}` - delete collection

## Product image upload flow

1. Call `POST /admin/uploads/product-image` with `multipart/form-data` and a `file` field.
2. Use the returned `image_url` as `image_url` when creating/updating products.
3. When replacing/deleting a product image, call `DELETE /admin/uploads/product-image?public_id=<old_public_id>`.
