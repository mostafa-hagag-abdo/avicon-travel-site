-- Avicon Travel control panel: trips & packages content, revisions, publishing, team access, images.
-- Run once in Supabase → SQL Editor (safe to re-run). Needs schema.sql (form_requests) to exist first.
--
-- Access model: only users listed in public.admins can read or change anything here (RLS).
-- The public site never reads these tables: "Publish" runs a GitHub Action that writes the pages.

-- ---------------------------------------------------------------- team
create table if not exists public.admins (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  email      text not null,
  name       text,
  role       text not null default 'editor' check (role in ('owner', 'editor')),
  created_at timestamptz not null default now()
);
alter table public.admins enable row level security;

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.admins where user_id = auth.uid());
$$;
revoke all on function public.is_admin() from public;
grant execute on function public.is_admin() to authenticated;

drop policy if exists "team reads team" on public.admins;
create policy "team reads team" on public.admins for select to authenticated using (public.is_admin());

-- ---------------------------------------------------------------- products (one row per trip page)
create table if not exists public.products (
  slug         text primary key check (slug ~ '^(tours|nile-cruises|packages)/[a-z0-9]+(-[a-z0-9]+)*$'),
  section      text not null check (section in ('tours', 'nile-cruises', 'packages')),
  status       text not null default 'hidden' check (status in ('published', 'hidden')),  -- what the team wants
  template     text,                       -- existing trip a new trip is copied from
  data         jsonb not null,             -- the team's copy: {blocks, seo, card} — see _dev/cms/sync.py
  live_data    jsonb,                      -- what the website has (set by publish / import)
  live_status  text check (live_status in ('published', 'hidden')),
  has_changes  boolean generated always as (           -- something waits for "Publish"
                 case when status = 'hidden' and coalesce(live_status, 'hidden') = 'hidden' then false
                      else status <> coalesce(live_status, 'hidden') or live_data is null or data <> live_data end) stored,
  sort_order   integer not null default 0,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),
  updated_by   uuid references auth.users(id),
  published_at timestamptz
);
create index if not exists products_section_idx on public.products (section, sort_order);

create table if not exists public.product_revisions (
  id         bigint generated always as identity primary key,
  slug       text not null references public.products(slug) on update cascade on delete cascade,
  status     text,
  data       jsonb not null,
  created_at timestamptz not null default now(),
  created_by uuid references auth.users(id)
);
create index if not exists product_revisions_slug_idx on public.product_revisions (slug, created_at desc);

-- keep the previous version on every change, and stamp who/when
create or replace function public.products_before_update() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (new.data is distinct from old.data) or (new.status is distinct from old.status) then
    insert into public.product_revisions (slug, status, data, created_by) values (old.slug, old.status, old.data, auth.uid());
    new.updated_at := now();
    new.updated_by := coalesce(auth.uid(), old.updated_by);
  end if;
  return new;
end $$;
drop trigger if exists products_before_update on public.products;
create trigger products_before_update before update on public.products
  for each row execute function public.products_before_update();

-- ---------------------------------------------------------------- publish jobs
create table if not exists public.publish_jobs (
  id           bigint generated always as identity primary key,
  requested_at timestamptz not null default now(),
  requested_by uuid references auth.users(id),
  status       text not null default 'queued' check (status in ('queued', 'running', 'deploying', 'success', 'failed')),
  message      text,
  changed      text[],                     -- slugs written by this job
  run_url      text,
  commit_sha   text,
  finished_at  timestamptz
);

-- ---------------------------------------------------------------- row level security
alter table public.products enable row level security;
alter table public.product_revisions enable row level security;
alter table public.publish_jobs enable row level security;

drop policy if exists "team manages products" on public.products;
create policy "team manages products" on public.products for all to authenticated
  using (public.is_admin()) with check (public.is_admin());

drop policy if exists "team reads revisions" on public.product_revisions;
create policy "team reads revisions" on public.product_revisions for select to authenticated using (public.is_admin());

drop policy if exists "team reads publish jobs" on public.publish_jobs;
create policy "team reads publish jobs" on public.publish_jobs for select to authenticated using (public.is_admin());

-- the website form inbox (table from schema.sql): the team reads it and updates status / notes
drop policy if exists "team reads requests" on public.form_requests;
create policy "team reads requests" on public.form_requests for select to authenticated using (public.is_admin());
drop policy if exists "team updates requests" on public.form_requests;
create policy "team updates requests" on public.form_requests for update to authenticated
  using (public.is_admin()) with check (public.is_admin());
revoke all on public.admins, public.products, public.product_revisions, public.publish_jobs from anon;
grant select, update (status, notes) on public.form_requests to authenticated;
grant select, insert, update, delete on public.products to authenticated;
grant select on public.product_revisions, public.publish_jobs, public.admins to authenticated;

-- ---------------------------------------------------------------- images (Storage bucket, public read)
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('site-images', 'site-images', true, 10485760, array['image/jpeg', 'image/png', 'image/webp'])
on conflict (id) do update set public = true, file_size_limit = excluded.file_size_limit, allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "team uploads images" on storage.objects;
create policy "team uploads images" on storage.objects for insert to authenticated
  with check (bucket_id = 'site-images' and public.is_admin());
drop policy if exists "team updates images" on storage.objects;
create policy "team updates images" on storage.objects for update to authenticated
  using (bucket_id = 'site-images' and public.is_admin());
drop policy if exists "team deletes images" on storage.objects;
create policy "team deletes images" on storage.objects for delete to authenticated
  using (bucket_id = 'site-images' and public.is_admin());
