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
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_products_category on products(category);
create index if not exists idx_products_featured on products(featured);
create index if not exists idx_products_collection_id on products(collection_id);
create index if not exists idx_collections_sort_order on collections(sort_order);

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