# Using Next.js API Endpoint (Simplified Approach)

## Why Use the Next.js API Instead of Supabase Directly?

✅ **Simpler** - No Supabase credentials needed  
✅ **More secure** - API handles authentication and RLS  
✅ **Consistent** - Same endpoint for browser and CLI  
✅ **Less code** - ~70 lines vs ~100+ lines  

---

## How It Works

### Architecture

```
CLI Tool
  ↓
POST /api/leaderboard
  Authorization: Bearer <token>
  ↓
Next.js API Route
  ↓
Extracts user_id from token
  ↓
Supabase Client (with token)
  ↓
Database (RLS enforced)
```

### Key Benefits

1. **No Configuration**
   - No Supabase URL/key needed
   - Just use the API endpoint

2. **Automatic Security**
   - API extracts `user_id` from token
   - Never trust client-provided `user_id`
   - RLS policies enforced automatically

3. **Single Source of Truth**
   - Browser and CLI use same endpoint
   - Consistent behavior everywhere

---

## Implementation

### Before (Supabase Direct)
```python
# Needed Supabase config
config = load_config()
supabase_url = config.get("supabase_url")
supabase_key = config.get("supabase_key")

# Complex headers
headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {token}",
    "Prefer": "resolution=merge-duplicates"
}

# Had to include user_id in payload
payload = {
    "user_id": user_id,  # Had to get from session
    "overall_score": 100.5
}

# Direct Supabase call
response = requests.post(
    f"{supabase_url}/rest/v1/leaderboard_public",
    headers=headers,
    json=payload
)
```

### After (Next.js API)
```python
# Simple headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# No user_id needed - API handles it
payload = {
    "overall_score": 100.5
}

# Call Next.js API
response = requests.post(
    f"{API_BASE_URL}/api/leaderboard",
    headers=headers,
    json=payload
)
```

**Much simpler!** 🎉

---

## Code Changes

### Removed
- ❌ `load_config()` - No longer needed
- ❌ `get_supabase_headers()` - Simplified
- ❌ Supabase URL/key configuration
- ❌ `user_id` in payload (API handles it)

### Added/Updated
- ✅ `API_BASE_URL` constant
- ✅ `fetch_leaderboard()` - Calls `/api/leaderboard`
- ✅ `upsert_leaderboard()` - Calls `/api/leaderboard` with Bearer token

---

## Usage

### Display Leaderboard
```bash
tito leaderboard
# Calls: GET /api/leaderboard
# No auth needed (public)
```

### Submit Score
```bash
tito submit --overall-score 100.5
# Calls: POST /api/leaderboard
# With: Authorization: Bearer <token>
# API extracts user_id from token automatically
```

---

## Security Flow

1. **CLI sends token** → `Authorization: Bearer <token>`
2. **API verifies token** → `supabase.auth.getUser()`
3. **API extracts user_id** → `user.id` from token
4. **API creates Supabase client** → With token (for RLS)
5. **API upserts** → With `user_id` from token (not payload)
6. **RLS checks** → `auth.uid() = user_id` ✅

**Result:** Users can only update their own rows, even if they try to send a different `user_id` in payload (which they can't anyway, since we don't accept it).

---

## Summary

**Before:** Direct Supabase calls with config, complex headers, manual user_id handling  
**After:** Simple Next.js API calls, no config, automatic user_id extraction

**Result:** Cleaner, simpler, more secure! 🚀
