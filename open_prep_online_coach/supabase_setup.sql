-- Run this entire script in Supabase Dashboard > SQL Editor > New query.
-- It creates one private row per authenticated user for logs, workout edits and profile data.
create table if not exists public.open_prep_data (
  user_id uuid primary key references auth.users(id) on delete cascade,
  logs jsonb not null default '{}'::jsonb,
  workout_edits jsonb not null default '{}'::jsonb,
  athlete_profile jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.open_prep_data enable row level security;

-- Remove policies with these names if re-running this setup script.
drop policy if exists "Users can read their own Open Prep data" on public.open_prep_data;
drop policy if exists "Users can insert their own Open Prep data" on public.open_prep_data;
drop policy if exists "Users can update their own Open Prep data" on public.open_prep_data;

create policy "Users can read their own Open Prep data"
on public.open_prep_data for select to authenticated
using (auth.uid() = user_id);

create policy "Users can insert their own Open Prep data"
on public.open_prep_data for insert to authenticated
with check (auth.uid() = user_id);

create policy "Users can update their own Open Prep data"
on public.open_prep_data for update to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

grant select, insert, update on public.open_prep_data to authenticated;

-- V2 nutrition upgrade: run this ALTER statement on existing Supabase projects.
alter table public.open_prep_data
add column if not exists nutrition jsonb not null default '{}'::jsonb;
