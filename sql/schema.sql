create table if not exists admin_users (
  id bigint generated always as identity primary key,
  username text not null unique,
  password_hash text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists collections (
  id bigint generated always as identity primary key,
  title text not null,
  subtitle text not null,
  description text not null,
  image_url text not null,
  categories jsonb not null default '[]'::jsonb,
  sort_order integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists products (
  id bigint generated always as identity primary key,
  name text not null,
  subtitle text not null,
  category text not null,
  description text not null,
  details text,
  image_url text not null,
  badge text,
  featured boolean not null default false,
  collection_id bigint references collections(id) on delete set null,
  material text,
  dimensions text,
  stock integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists categories (
  id bigint generated always as identity primary key,
  name text not null unique,
  display_name text not null,
  description text,
  icon text,
  sort_order bigint not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists frontend_configs (
  id bigint generated always as identity primary key,
  config_key text not null unique,
  config_value jsonb not null,
  description text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Add new columns to products table if they don't exist
alter table products add column if not exists material text;
alter table products add column if not exists dimensions text;
alter table products add column if not exists stock integer not null default 0;
alter table products add column if not exists is_admin_uploaded boolean not null default false;
alter table products add column if not exists article_number text not null default '';
alter table products add column if not exists price text not null default '0';

create index if not exists idx_products_category on products(category);
create index if not exists idx_products_article_number on products(article_number);
create index if not exists idx_products_featured on products(featured);
create index if not exists idx_products_collection_id on products(collection_id);
create index if not exists idx_products_is_admin_uploaded on products(is_admin_uploaded);
create index if not exists idx_collections_sort_order on collections(sort_order);
create index if not exists idx_categories_sort_order on categories(sort_order);
create index if not exists idx_categories_name on categories(name);
create index if not exists idx_frontend_configs_key on frontend_configs(config_key);

create or replace function set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_admin_users_updated_at on admin_users;
create trigger trg_admin_users_updated_at
before update on admin_users
for each row execute function set_updated_at();

drop trigger if exists trg_collections_updated_at on collections;
create trigger trg_collections_updated_at
before update on collections
for each row execute function set_updated_at();

drop trigger if exists trg_products_updated_at on products;
create trigger trg_products_updated_at
before update on products
for each row execute function set_updated_at();

drop trigger if exists trg_categories_updated_at on categories;
create trigger trg_categories_updated_at
before update on categories
for each row execute function set_updated_at();

drop trigger if exists trg_frontend_configs_updated_at on frontend_configs;
create trigger trg_frontend_configs_updated_at
before update on frontend_configs
for each row execute function set_updated_at();

create table if not exists reviews (
  id bigint generated always as identity primary key,
  author_name text not null,
  rating integer not null,
  comment text not null,
  city text,
  is_approved boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_reviews_is_approved on reviews(is_approved);
create index if not exists idx_reviews_created_at on reviews(created_at);

drop trigger if exists trg_reviews_updated_at on reviews;
create trigger trg_reviews_updated_at
before update on reviews
for each row execute function set_updated_at();