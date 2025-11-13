# Session Storage Implementation Summary

## ✅ What Was Implemented

### 1. **JSON Session Storage**
- **File:** `~/.tito/session.json`
- **Format:**
```json
{
  "access_token": "eyJhbGc...",
  "user_id": "uuid-here",
  "expires_in": 3600
}
```

### 2. **Minimal Fields Stored**
- ✅ `access_token` - JWT token for API authentication
- ✅ `user_id` - Required for RLS (Row Level Security) in Supabase
- ✅ `expires_in` - Token expiration time (for future use)

**Skipped (can add later):**
- `created_at` - Not needed for now
- `email` - Not needed for now
- `username` - Not needed for now

### 3. **Backward Compatibility**
- ✅ Automatically migrates old `~/.tito/token` file to new format
- ✅ `get_token()` function still works (for existing code)
- ✅ Old token files are automatically removed after migration

### 4. **Logout Functionality**
- ✅ `tito logout` clears entire session file
- ✅ All session data removed (token, user_id, expires_in)

---

## Code Changes

### New Functions
- `save_session(session_data)` - Save full session to JSON
- `load_session()` - Load session from JSON
- `clear_session()` - Remove session file
- `get_user_id()` - Get user ID from session
- `migrate_old_token()` - Migrate old token file

### Updated Functions
- `api_login()` - Now returns full session data (not just token)
- `cmd_login()` - Saves full session data
- `cmd_logout()` - Clears session file
- `cmd_status()` - Shows token + user_id

### Backward Compatible
- `get_token()` - Still works, extracts token from session

---

## Usage Examples

### Login
```bash
tito login
# Saves: access_token, user_id, expires_in to ~/.tito/session.json
```

### Check Status
```bash
tito status
# Shows: Token and User ID if logged in
```

### Logout
```bash
tito logout
# Removes: ~/.tito/session.json (clears everything)
```

### Using in Code
```python
from login_test import get_token, get_user_id, load_session

# Get token (backward compatible)
token = get_token()

# Get user ID (new)
user_id = get_user_id()

# Get full session
session = load_session()
token = session["access_token"]
user_id = session["user_id"]
expires_in = session["expires_in"]
```

---

## File Structure

```
~/.tito/
├── session.json    # New: Full session data (JSON)
└── token           # Old: Migrated automatically, then deleted
```

---

## Migration Flow

1. User runs any command
2. Code checks for `session.json` → if exists, use it
3. If not, check for old `token` file
4. If old token exists:
   - Read token
   - Create `session.json` with token (user_id=None)
   - Delete old `token` file
5. Next login will populate `user_id` properly

---

## Security

- ✅ File permissions: `600` (owner read/write only)
- ✅ Directory permissions: `700` (owner only)
- ✅ Logout clears all data
- ✅ No sensitive data logged

---

## Next Steps (For Future)

When you need to make API calls with user_id:

```python
session = load_session()
if not session:
    print("Not logged in. Run 'tito login' first.")
    sys.exit(1)

token = session["access_token"]
user_id = session["user_id"]

# Make API call with user_id for RLS
headers = {"Authorization": f"Bearer {token}"}
payload = {
    "user_id": user_id,  # Required for Supabase RLS
    "score": 100
}
```

---

## Testing Checklist

- [x] Login saves session.json
- [x] Status shows token + user_id
- [x] Logout clears session.json
- [x] Old token file migration works
- [x] Backward compatibility maintained

---

## Summary

✅ **Minimal implementation** - Only stores what's needed  
✅ **Backward compatible** - Migrates old token files  
✅ **Logout clears everything** - As requested  
✅ **Ready for RLS** - user_id available for Supabase  
✅ **Extensible** - Easy to add fields later  

**Total code:** ~240 lines (clean, modular, maintainable)
