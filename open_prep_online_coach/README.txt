OPEN PREP + ONLINE AI COACH — CLOUD ACCOUNT EDITION
===================================================

WHAT'S NEW
- Email/password athlete accounts using Supabase Auth.
- Cloud-saved training logs, custom workouts and athlete profile.
- Automatic sync after saving a log, workout edit or profile.
- Sign in on your PC and iPhone to access the same account data.
- Existing browser logs are preserved and merged into the cloud the first time you sign in. If a key exists both locally and in the cloud, the cloud version wins.
- Local browser copies remain as a fallback; export JSON backups regularly.
- AI coach receives your saved profile and recent training logs when you press Send.

PART 1 — CREATE YOUR SUPABASE PROJECT
1. Go to https://supabase.com/ and create a free account or sign in.
2. Create a new project. Choose a project name (for example, open-prep), set a strong database password and choose a region near you.
3. Wait for the project to finish provisioning.
4. In the Supabase dashboard, open SQL Editor > New query.
5. Open the file supabase_setup.sql from this folder, copy its entire contents into the SQL Editor and click Run.
6. In Supabase, open Project Settings > API (or Data API / API Keys, depending on dashboard layout).
7. Copy the Project URL and the publishable key. If the dashboard shows the legacy anon/public key instead, that is also suitable.
   IMPORTANT: Do NOT use or paste the secret/service_role key. The browser app must only use the publishable/anon key. Row Level Security policies in the SQL file restrict each account to its own row.
8. Optional: for a simpler first login, open Authentication > Providers > Email and turn off email confirmation while testing. If email confirmation stays on, check your inbox after creating an account before logging in.

PART 2 — CONNECT OPEN PREP
1. Start Open Prep on your PC as before (double-click start_windows.bat).
2. Open the app in your PC browser.
3. In Cloud account & sync, paste the Supabase Project URL and publishable/anon key.
4. Click Save cloud settings.
5. Enter your email and create a password, then click Create account. If confirmation is enabled, confirm the email and then log in.
6. Once logged in, Open Prep uploads your existing local logs and workout edits and loads the saved athlete profile. Watch for the Cloud sync ready status.
7. Fill in Athlete profile if needed and click Save athlete profile.

PART 3 — USE IT ON YOUR IPHONE
1. Open the same Open Prep address on your iPhone (the local PC address works only on the same Wi-Fi while the PC server is running).
2. In Cloud account & sync, enter the same Supabase URL and publishable/anon key and click Save cloud settings. These are project-level public client settings, not your account password.
3. Log in using the same email and password.
4. Your saved training logs, workout edits and athlete profile should load from the cloud.
5. Save sessions normally. They sync automatically after a short delay. Use Sync now if you want to force a save.

IMPORTANT ABOUT ACCESS
- Cloud storage syncs the data, but this version is still served by your Windows PC. For access when away from home, the web app itself must also be deployed to an HTTPS host. Do not port-forward the local development server to the public internet.
- Your PC must remain on to serve the current app URL on home Wi-Fi. Supabase does not host this app's website; it hosts the account and data.
- Supabase publishable/anon keys are designed for browser use. Never use a secret/service_role key in this app. The SQL enables Row Level Security so each signed-in user can access only their own row.
- Use a unique strong password. Supabase account credentials are sent to Supabase Auth over HTTPS.
- This is a starter implementation. It syncs the current training data object on save; it is not a conflict-free collaborative editor. Avoid editing the same training day simultaneously on two devices. On first sign-in, cloud values take precedence where the same log/workout key already exists, while local-only keys are preserved.

AI COACH / API BILLING
- The OpenAI API key remains in the local backend .env file and is not stored in Supabase or exposed to the browser.
- API usage is billed separately from a ChatGPT subscription.
- The coach receives the athlete profile, selected session and up to 10 recent logs when you press Send.

TROUBLESHOOTING
- "relation open_prep_data does not exist": run supabase_setup.sql in the Supabase SQL Editor.
- "row-level security" / permission error: verify you ran the complete SQL script and that you are logged in.
- "Invalid API key": use the Supabase publishable key or legacy anon/public key, not the secret/service_role key.
- Email confirmation: confirm the email first, then log in.
- Sync failed: check internet connection, Project URL, key, SQL table and RLS policies.
- AI coach not connected: keep the Python backend running and check OPENAI_API_KEY in .env.

BACKUPS
Use Download full backup (JSON) regularly. Cloud sync is convenient, but it is not a substitute for an independent backup.


OPEN PREP V2 UPGRADE — IMPORTANT
===============================
1. BACK UP your current project and export your training logs before upgrading.
2. In your existing Supabase project, open SQL Editor and run UPGRADE_V2.sql ONCE.
   This adds a private nutrition JSON column to your existing open_prep_data table.
   It does not delete existing accounts, workout edits, logs or profiles.
3. Replace your existing app files with the V2 files, but KEEP YOUR EXISTING .env
   file with your working OPENAI_API_KEY. Do not share or upload the .env file.
4. Run start_windows.bat (or your usual launcher). Refresh your PC and phone browser.
5. Your existing Supabase project URL and public key are saved in each browser's
   localStorage; if you use a different URL/port/browser, re-enter them and log in.
6. Expand panels via their headers. The workout has collapsible prescriptions.
7. To change a workout, select the day and ask the AI coach e.g.
   'Replace today's conditioning with a 20 minute low-impact bike workout.'
   Review the proposed full section text, then press Apply. This saves locally
   and queues a Supabase sync. Other sections are preserved.
8. For nutrition, select a date, describe a meal, click Estimate with AI,
   review/edit calories and macros, then Save meal. Daily totals update.
   Nutrition syncs through the existing user row. AI estimates are approximate.
9. Export full JSON backup regularly. The backup now includes nutrition,
   profile and workout edits as well as logs.

Notes: AI requests require your local FastAPI server and working API key.
No actual OpenAI/Supabase end-to-end calls were made during packaging.
Cloud sync uses the existing whole-row upsert behavior; avoid editing the same
records simultaneously on two devices. The local browser retains fallback data.

OPEN PREP V3
------------
- Refreshed dark visual theme and responsive hero.
- Daily Bible verse at the top, rotating by local calendar day from a built-in
  public-domain King James Version selection (no external Bible API required).
- Nutrition estimates can use the OpenAI Responses API web_search tool to look up
  relevant nutrition data. Named restaurant/packaged foods are especially suitable.
- No weights required: the AI estimates standard serving sizes, states assumptions,
  and lets you review/edit before saving.
- Edit existing saved meal totals with the Edit button; changes update daily totals
  and sync through your existing Supabase nutrition JSON column.
- Your existing Supabase schema from V2 needs NO additional SQL changes.
- Web search incurs API usage costs and requires a model/account supporting the
  Responses API web_search tool. If a request fails, check API model access/billing.
- Estimates remain approximate, and source references in the assumptions are
  model-generated text, not independently verified citations.
- Backup the V2 folder and preserve your local .env when upgrading.

OPEN PREP V4 (November 2026)
============================
- Sidebar menu: open with Menu, click a section to jump and expand it.
- Workout logbook: filter by CrossFit, Running, Lifting, Biking, Rowing,
  Ski erg, Walking; extra activities and dated scheduled workouts are saved
  alongside existing logs. Lifting history displays highest *logged working*
  weight and sets/reps, not a certified 1RM.
- Weekly run mileage counts distance on program workouts plus extra Running
  activities. This calendar week's counter uses Monday-Sunday calendar dates.
- Workout completion progress counts program sessions, not extra activities.
- Nutrition goals are stored inside athlete_profile.nutrition_goals so your
  existing Supabase schema works unchanged. No new SQL migration required.
- Saving/editing/deleting a meal recomputes the daily macro and calorie tiles;
  nutrition entries continue syncing in the existing nutrition JSON column.
- A separate /api/nutrition/coach endpoint answers questions using saved goals,
  selected-day macro totals and logged activity. No wearable data in V4.
- A separate /api/nutrition/estimate endpoint uses nutrition-specific guidance,
  attempts live web search and falls back to model-only estimation when the
  web search tool is unavailable. Food estimates are approximate.
- Optional .env setting NUTRITION_MODEL allows a different OpenAI model for
  nutrition. It uses the SAME OPENAI_API_KEY; a separate paid service is not
  necessary. Search/model calls can incur API costs.
- Back up V3 and preserve your .env file. Test on desktop first, then mobile.
- Cloud sync uses whole JSON documents. Avoid editing simultaneously on two
  devices; concurrent writes can overwrite recent edits.
- End-to-end AI calls and live Supabase sync require your own credentials and
  have not been verified in this development environment.

V4.1 HOTFIX — NUTRITION TOTALS
- Main calorie/protein/carbs/fat counters and goal bars use the SAME saved-meal calculation.
- Save, edit, delete, date switch and cloud load all refresh daily totals.
- Correct local date key (YYYY-MM-DD), avoiding locale-dependent date mismatches.
- Clear save confirmation after the counters are recalculated.
- Cloud day merge retains locally logged meals when a cloud load arrives.
- No Supabase SQL changes required. Preserve your existing .env and keep V4 backup.

V4.12 PATCH
-----------
- GUI version now says V4.12.
- After AI estimates a meal, click the explicit "Add to Daily Counter" button.
- No meal is counted before that click. All four totals are updated from saved meals.
- Meal is assigned to the date selected when the estimate was requested.
- You can still edit a saved meal (Update meal) or delete it.
- No new SQL is required. Keep your old folder as backup and preserve .env.

OPEN PREP V4.5 — NUTRITION REBUILD
=================================
This version replaces the nutrition UI and calculation code rather than patching
V4.12. Existing V2–V4.12 nutrition data stays in the same Supabase JSONB column
and localStorage key. No new SQL migration is required.

NUTRITION FLOW
1. Open Nutrition in the sidebar, choose the correct food log date.
2. Describe a meal and click Estimate with AI. If AI is unavailable, use
   Enter meal manually instead.
3. Review or edit calories, protein, carbs, fat, and description.
4. Click Add to Daily Counter. This action saves the meal locally immediately,
   recalculates the displayed totals, and queues a cloud sync.
5. Saved meals can be edited and deleted. Deleted meals are retained internally
   as tombstones to prevent old cloud copies from reappearing.
6. Use Run counter self-test to verify calculations without altering real logs.

TESTING
- The pure calculation engine was tested with add/add/edit/delete/merge/JSON
  persistence assertions. JS syntax and Python compilation were checked.
- Browser automation could not run in the build environment due to its browser
  navigation policy. Live OpenAI and Supabase integration remain to be tested.
- Test on desktop first, then confirm the same totals on the phone. Keep a
  backup of the old project and its .env file. Do not put .env in cloud storage.
- Supabase sync requires the nutrition JSONB column already added in V2.
