-- Avicon Travel: website form requests (booking, contact, tailor-made, transfer).
-- Run once in Supabase → SQL Editor. Safe to re-run.
-- Rows are written only by the Edge Function "submit-request" (service role). RLS is on with no policies,
-- so the public anon key can neither read nor write this table; the owner reads it in Table Editor.

create table if not exists public.form_requests (
  id              bigint generated always as identity primary key,
  created_at      timestamptz not null default now(),
  form_type       text not null check (form_type in ('booking', 'contact', 'tailor_made', 'transfer', 'test')),
  status          text not null default 'new' check (status in ('new', 'contacted', 'booked', 'closed', 'spam')),
  tour_package    text,
  subject         text,
  name            text not null,
  email           text,
  phone           text,
  travel_date     text,
  travel_time     text,
  adults          integer,
  children        integer,
  travelers       text,
  destination     text,
  pickup          text,
  service         text,
  estimated_total text,
  message         text,
  page_url        text,
  extra           jsonb not null default '{}'::jsonb,
  user_agent      text,
  email_sent      boolean not null default false,
  whatsapp_sent   boolean not null default false,
  notify_error    text,
  notes           text
);

comment on table public.form_requests is 'Website form submissions (avicontravel.com). Written by the submit-request Edge Function.';
comment on column public.form_requests.status is 'new → contacted → booked / closed; spam for junk.';

create index if not exists form_requests_created_at_idx on public.form_requests (created_at desc);
create index if not exists form_requests_status_idx on public.form_requests (status);
create index if not exists form_requests_email_idx on public.form_requests (email);
create index if not exists form_requests_phone_idx on public.form_requests (phone);

alter table public.form_requests enable row level security;
revoke all on public.form_requests from anon, authenticated;
