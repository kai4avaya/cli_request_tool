# Leaderboard Setup Guide

## Quick Start

### 1. Login
```bash
tito login
```

### 2. View Leaderboard
```bash
# View top 10 (default)
tito leaderboard

# View top 20
tito leaderboard 20
```

### 3. Submit Score
```bash
tito submit --overall-score 100.5 --optimization-score 50.0 --accuracy-score 75.0
```

**That's it!** No configuration needed - uses your Next.js API endpoint.

---

## How It Works

### Display Leaderboard (Public Read)
- ✅ **No login required** - Public API endpoint
- ✅ Calls Next.js API: `GET /api/leaderboard`
- ✅ Orders by `overall_score` descending
- ✅ Shows: Rank, User ID, Scores, Submissions

### Submit Score (Authenticated)
- ✅ **Requires login** - Uses Bearer token from session
- ✅ Calls Next.js API: `POST /api/leaderboard`
- ✅ API handles authentication and RLS automatically
- ✅ API extracts `user_id` from token (you don't send it)
- ✅ RLS policy ensures users can only update their own rows

---

## API Details

### Next.js API Endpoint
```
POST https://tinytorch.netlify.app/api/leaderboard
```

### Headers
```json
{
  "Authorization": "Bearer <session-token>",
  "Content-Type": "application/json"
}
```

### Payload
```json
{
  "overall_score": 100.5,
  "optimization_score": 50.0,
  "accuracy_score": 75.0,
  "successful_submissions": 10
}
```

**Note:** `user_id` is automatically extracted from the token by the API - you don't include it in the payload!

---

## Code Structure

### Functions Added
- `fetch_leaderboard()` - GET leaderboard via Next.js API (public)
- `upsert_leaderboard()` - POST score via Next.js API (authenticated)
- `cmd_leaderboard()` - CLI command to display
- `cmd_submit()` - CLI command to submit

### Minimal Implementation
- ✅ ~70 lines of code added
- ✅ Uses existing session management
- ✅ No Supabase credentials needed
- ✅ Proper error handling
- ✅ API handles authentication and RLS automatically

---

## Examples

### View Top 10
```bash
tito leaderboard
```

### View Top 50
```bash
tito leaderboard 50
```

### Submit Overall Score Only
```bash
tito submit --overall-score 100.5
```

### Submit All Scores
```bash
tito submit \
  --overall-score 100.5 \
  --optimization-score 50.0 \
  --accuracy-score 75.0 \
  --successful-submissions 10
```

### Update Existing Score
```bash
# Upsert automatically updates if user_id exists
tito submit --overall-score 150.0
```

---

## Troubleshooting

### "Not logged in" (when submitting)
Run `tito login` first.

### "Token not found in session"
Login again - the API should return access_token.

### API Errors
- Check that your Next.js API endpoint is deployed and accessible
- Verify token is valid (try logging in again)
- Check API response for specific error messages

---

## Security Notes

- ✅ **No Supabase credentials needed** - API handles everything
- ✅ Token stored securely in `~/.tito/session.json` (600 permissions)
- ✅ API extracts `user_id` from token (never trust client-provided user_id)
- ✅ RLS policies enforce user can only update own rows
- ✅ API verifies token before any database operation

---

## Next Steps

1. Run `tito login`
2. Test: `tito leaderboard`
3. Test: `tito submit --overall-score 100.0`

**No configuration needed!** The CLI uses your Next.js API endpoint which handles all authentication and security.
