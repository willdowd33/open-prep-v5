# Open Prep V4.8 — Render Free Cloud Deployment

This release ports the working V4.6 app to a cloud-hosted FastAPI web service and makes it installable from Safari as a Home Screen web app. Existing Supabase data stays in your existing project.

## Deploy

1. Create a GitHub repository (prefer **private**). Extract this ZIP and upload the *contents* of `open_prep_online_coach` into the repository root, including `render.yaml`. Do not upload `.env`, passwords, or secret keys.
2. Create an account at https://dashboard.render.com and connect GitHub.
3. In Render choose **New > Blueprint** and select the repository, or **New > Web Service** with:
   - Language: Python 3
   - Plan: Free
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. In Render's **Environment** add `OPENAI_API_KEY` as a secret. Set `OPENAI_MODEL` and `NUTRITION_MODEL` to models available to your API account. Do not upload `.env` to GitHub.
5. Deploy and open `https://YOUR-SERVICE.onrender.com/api/version`; expect `4.8`.
6. Open the main site. In **Cloud account & sync**, enter your existing Supabase Project URL and **publishable/anon** key, then log into the same Supabase account as on your laptop. These settings are browser-local, so you must enter them once per new origin/device.
7. Confirm that your prior workouts and meals appear before relying on the new URL. Data previously saved *only* in the old browser's localStorage will not automatically migrate to a new domain. Export from the old app first if necessary.
8. iPhone: Safari > Share > Add to Home Screen > Open as Web App (if offered) > Add. Use the HTTPS Render URL, not your local IP.

## Important limitations
- Free Render services sleep after ~15 minutes idle and may take about a minute to wake.
- The filesystem is ephemeral. Keep all durable user data in Supabase, not local server files.
- Your OpenAI API usage is billed separately. The existing `/api/coach` and `/api/nutrition/*` endpoints do not enforce server-side Supabase JWT authentication or per-user rate limits. Do not share the public app URL widely until these protections are implemented; a public URL can be abused and incur API charges.
- Supabase row-level security should remain enabled. Do not place a Supabase service_role key in the browser.
- No new Supabase SQL required beyond your existing `nutrition` column.
- The web app is installable; this is not yet a native App Store application.
- The service worker deliberately avoids caching HTML so app updates aren't stuck on old versions.
