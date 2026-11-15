# Open Prep V5.0 — Render Cloud Deployment

## What's implemented
- V4.8 training plan and nutrition logging preserved; updated V5 visual navigation.
- AI workout analysis with editable draft, explicit approval, cloud saved log and delete action.
- Separate AI coaching conversations saved per user in Supabase.
- WHOOP 4.0 OAuth connect, refresh, encrypted server-side token storage, recovery/cycle/sleep/workout summary and disconnect.
- All AI POST endpoints require a valid Supabase user session; no anonymous AI spending.
- GitHub → Render deploy, `/api/version` version check, no-cache HTML and service worker.
- Versioned SQL migration and rollback instructions.

## Deploy checklist
1. Back up your current V4.8 ZIP, GitHub commit and Supabase data. **Do not overwrite your only working copy.**
2. Unzip and commit **the files inside** `open_prep_online_coach` to your GitHub repository root. If the repo has the folder itself, set Render Root Directory to `open_prep_online_coach`.
3. Supabase Dashboard → SQL Editor: run `migrations/001_v5.sql` **once**. It adds separate V5 tables and does not alter V4 nutrition rows.
4. Render → Environment: configure `OPENAI_API_KEY`, `OPENAI_MODEL` (choose a model your account supports), `SUPABASE_URL` and `SUPABASE_ANON_KEY` (Supabase publishable/legacy anon). Redeploy. These two Supabase server values are REQUIRED for the new authenticated AI routes, including the existing V4 AI buttons.
5. For WHOOP: create a developer application at https://developer.whoop.com. Configure its callback URL as `https://YOUR-RENDER-HOST.onrender.com/api/v5/whoop/callback`. On Render add `WHOOP_CLIENT_ID`, `WHOOP_CLIENT_SECRET`, `WHOOP_REDIRECT_URI`, `SUPABASE_SERVICE_ROLE_KEY`, and `WHOOP_TOKEN_ENCRYPTION_KEY` (generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`). **Never expose these secrets in frontend, GitHub or chat.** Do not rotate the encryption key without reauthorizing WHOOP.
6. Ensure Render service Root Directory and build/start commands match README_RENDER_V4_8.md. Confirm `https://YOUR-HOST/api/version` returns 5.0.
7. In Open Prep, enter your existing Supabase project URL and publishable/anon key in Cloud Account and sign in. Verify existing nutrition totals and workouts before logging new data.
8. Test AI workout analysis → edit → approve → refresh → history persists → delete; test separate AI chat → refresh → history persists; connect WHOOP and refresh metrics.

## Limitations and operational notes
- WHOOP API gives periodic recovery/sleep/strain/HR statistics, **not live heart-rate streaming**. WHOOP 4.0 BLE broadcast requires a Bluetooth-capable client; iPhone PWA does not support direct BLE pairing reliably. No fake Bluetooth button is included.
- WHOOP integration requires valid developer app credentials and real device authorization; it cannot be live-tested without your credentials.
- Render Free can sleep after inactivity; data is stored in Supabase, not Render filesystem.
- Current chat/workout history uses direct authenticated Supabase client operations; Supabase RLS must remain enabled. New V5 tables have per-user RLS.
- Legacy workout logs and V5 AI workout logs are separate histories. V5 AI logs do not yet feed V4 dashboard totals; merging requires a data migration and reconciliation plan.
- V5 does not implement live iOS push notifications, automated Supabase database backups, or one-click transactional rollback. These require additional infrastructure.
- If you encounter `401`, sign in again. `503` means Render environment configuration is missing. `404` from WHOOP summary means you have not connected yet.

## Rollback
- In Render, redeploy your saved V4.8 commit (or revert the V5 commit in GitHub). Keep the V5 SQL tables: they are additive and do not affect V4.8.
- Do not drop V5 tables if you want to retain V5 logs/chats. To remove them later, export first, then drop manually after verifying the backup.
- Database migrations are versioned in `migrations/`; run them explicitly before deploying dependent code. Supabase SQL Editor changes are not automatically reversed by a Render rollback.

## Version/update strategy
- `GET /api/version` reports the backend version. Browser HTML uses `Cache-Control: no-store` and a network-only service worker.
- GitHub commits trigger Render deployments when automatic deploy is enabled. To release safely, test in a separate Render staging service first and then promote the commit.
- Future releases should add a UI update banner and integration tests in CI; these are **not yet implemented** in this package.
