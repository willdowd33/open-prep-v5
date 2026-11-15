OPEN PREP V4.6 — NUTRITION REPAIR AND VISUAL REFRESH

1. Stop all old servers (Ctrl+C) before launching this version.
2. Extract this ZIP to a NEW folder. Copy your existing .env into it.
3. Launch start_windows.bat. Open http://localhost:8000/api/version — should show {"version":"4.6"}.
4. Open the app and confirm the top banner and sidebar show V4.6.
5. Test MANUAL entry first: type "test meal", press Enter meal manually, enter 500 calories, then Add to Daily Counter.
6. Confirm the counter shows 500, and the meal appears in the saved food log. Refresh and confirm it remains.
7. Try AI estimate. If it fails, the page now shows an error. Check /api/health to see if the API key is configured.
8. Supabase requires the nutrition jsonb column added in V2; no new SQL for V4.6.
9. Keep V4.5 as backup. Do not delete existing localStorage data.

Important: The nutrition core is now INLINE in the HTML to avoid old cached scripts on iPhone.
The daily counter saves locally first; cloud sync is a separate later operation.
AI and Supabase calls require live credentials and must be tested on your machine.
