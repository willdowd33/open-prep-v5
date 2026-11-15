-- Run this once in Supabase SQL Editor to enable nutrition syncing.
alter table public.open_prep_data
add column if not exists nutrition jsonb not null default '{}'::jsonb;
