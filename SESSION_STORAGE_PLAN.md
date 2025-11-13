# Session Storage Plan: Storing Additional Login Info

## Current State

**What we store now:**
- ✅ `access_token` → saved to `~/.tito/token`

**What the API returns:**
- `access_token` (JWT) ✅ Currently saved
- `user.id` ❌ Not saved (needed for user_id in payloads)
- `expires_in` ❌ Not saved (useful for token expiration)

---

## Options for Storing Additional Info

### Option 1: JSON Session File (Recommended) ⭐

**Structure:**
```
~/.tito/session.json
```

**Content:**
```json
{
  "access_token": "eyJhbGc...",
  "user_id": "uuid-here",
  "expires_in": 3600,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Pros:**
- ✅ Single file, easy to manage
- ✅ Easy to extend (add email, username, etc. later)
- ✅ Can validate structure
- ✅ Can track expiration times
- ✅ Standard approach (like AWS CLI credentials)

**Cons:**
- ❌ Need to parse JSON (minimal overhead)
- ❌ Breaking change from current token-only approach

**Migration:** Easy - can read old `token` file and migrate to JSON

---

### Option 2: Separate Files

**Structure:**
```
~/.tito/token          # access_token
~/.tito/user_id        # user.id
~/.tito/expires_in     # expires_in (optional)
```

**Pros:**
- ✅ Simple, one value per file
- ✅ Backward compatible (keep token file)
- ✅ Easy to read individual values

**Cons:**
- ❌ Multiple files to manage
- ❌ Harder to keep in sync
- ❌ More file operations
- ❌ Less organized

---

### Option 3: Hybrid (Token + Config)

**Structure:**
```
~/.tito/token          # access_token (keep for compatibility)
~/.tito/config.json    # { user_id, expires_in, ... }
```

**Pros:**
- ✅ Backward compatible
- ✅ Token still accessible as plain text
- ✅ Other info in structured format

**Cons:**
- ❌ Two files to manage
- ❌ Can get out of sync
- ❌ More complex

---

## Recommendation: Option 1 (JSON Session File) ⭐

**Why:**
1. **Minimum complexity** - One file, one format
2. **Easy to extend** - Add fields later without restructuring
3. **Industry standard** - Similar to AWS CLI, GitHub CLI
4. **Better organization** - All session data together
5. **Can track expiration** - Useful for auto-refresh later

**Implementation:**
```python
# Save session
save_session({
    "access_token": token,
    "user_id": user_id,
    "expires_in": expires_in,
    "created_at": datetime.now().isoformat()
})

# Load session
session = load_session()
token = session["access_token"]
user_id = session["user_id"]
```

---

## Migration Strategy

**Step 1:** Check if old `token` file exists
**Step 2:** If yes, read it and create `session.json` with token + defaults
**Step 3:** Delete old `token` file
**Step 4:** Use `session.json` going forward

**Backward compatibility:** Can read both formats during transition

---

## Code Structure

```python
# Session management functions
def get_session_file_path() -> Path
def save_session(session_data: dict) -> bool
def load_session() -> dict | None
def clear_session() -> bool

# Convenience functions (for backward compatibility)
def get_token() -> str | None  # Extracts from session
def get_user_id() -> str | None  # Extracts from session
```

---

## Security Considerations

- ✅ File permissions: `600` (owner read/write only)
- ✅ Directory permissions: `700` (owner only)
- ✅ Never log sensitive data
- ✅ Clear on logout

---

## Example Usage After Update

```python
# Login
session = api_login(email, password)
# Returns: { "access_token": "...", "user_id": "...", "expires_in": 3600 }
save_session(session)

# Use in API calls
session = load_session()
headers = {
    "Authorization": f"Bearer {session['access_token']}",
    "Content-Type": "application/json"
}
payload = {
    "user_id": session["user_id"],  # Required for RLS
    "score": 100
}
```

---

## Next Steps

1. ✅ Discuss approach (this document)
2. ⏳ Update `api_login()` to return full response
3. ⏳ Create session management functions
4. ⏳ Update `cmd_login()` to save full session
5. ⏳ Add migration from old token file
6. ⏳ Update `load_token()` to work with session
7. ⏳ Test login/logout flow

---

## Questions to Consider

1. **Do we need backward compatibility?** 
   - If yes: Support reading old `token` file
   - If no: Clean break, require re-login

2. **Do we need to track expiration?**
   - If yes: Store `expires_in` and `created_at`
   - If no: Can skip for now

3. **Do we need user email/username?**
   - If yes: Store in session.json
   - If no: Can add later

**My recommendation:** Start simple with JSON file, add fields as needed.
