-- Run once in the existing Supabase SQL Editor. Does not modify existing workout/nutrition rows.
create table if not exists public.open_prep_v5_workouts (
 id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
 created_at timestamptz not null default now(), performed_on date not null default current_date,
 category text not null, title text not null, details jsonb not null default '{}'::jsonb
);
create table if not exists public.open_prep_v5_chats (
 id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
 title text not null default 'New conversation', messages jsonb not null default '[]'::jsonb,
 updated_at timestamptz not null default now()
);
create table if not exists public.open_prep_whoop_tokens (
 user_id uuid primary key references auth.users(id) on delete cascade,
 token_ciphertext text not null, updated_at timestamptz not null default now()
);
create table if not exists public.open_prep_whoop_states (
 state text primary key, user_id uuid not null references auth.users(id) on delete cascade,
 created_at timestamptz not null default now()
);
alter table public.open_prep_v5_workouts enable row level security;
alter table public.open_prep_v5_chats enable row level security;
alter table public.open_prep_whoop_tokens enable row level security;
alter table public.open_prep_whoop_states enable row level security;
-- No client policies on WHOOP secrets: service role only.
drop policy if exists "own workouts" on public.open_prep_v5_workouts;
create policy "own workouts" on public.open_prep_v5_workouts for all to authenticated using (auth.uid()=user_id) with check (auth.uid()=user_id);
drop policy if exists "own chats" on public.open_prep_v5_chats;
create policy "own chats" on public.open_prep_v5_chats for all to authenticated using (auth.uid()=user_id) with check (auth.uid()=user_id);
create index if not exists idx_v5_workouts_user_date on public.open_prep_v5_workouts(user_id,performed_on desc);
create index if not exists idx_v5_chats_user_date on public.open_prep_v5_chats(user_id,updated_at desc);
