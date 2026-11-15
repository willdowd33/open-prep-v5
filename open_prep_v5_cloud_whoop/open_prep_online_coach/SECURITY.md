# Security checklist
- Server verifies Supabase access tokens through `/auth/v1/user` for every AI endpoint and WHOOP operation.
- WHOOP OAuth uses a random single-use state stored in a service-role-only table and expires after 10 minutes.
- WHOOP access/refresh tokens are encrypted with Fernet and stored in a service-role-only Supabase table. Service-role key must never be placed in browser code.
- WHOOP disconnect deletes stored credentials locally. Revoke access in WHOOP settings too.
- Do not share your API keys or service-role key. Restrict WHOOP developer app callback URLs to your Render domain.
- Per-user AI quotas and abuse rate limits are NOT implemented. Authentication is a baseline, not a full public-production abuse defense.
- Old V4 coach and nutrition AI endpoints now require login; nutrition local manual entry still works without login.
- For public launch: add rate limits, spend caps, structured monitoring, content-length limits and account abuse detection.
