# CLI Authentication Persistence Plan

## Current Implementation (File-Based Token Storage)

**What we have now:**
- Username/password login → API returns token → Save to `~/.tito/token`
- Token stored in plain text file with secure permissions (600)
- Simple, works immediately

**Pros:**
- ✅ Minimum complexity - just save/load a file
- ✅ No dependencies beyond standard library
- ✅ Works offline (once logged in)
- ✅ Fast and reliable

**Cons:**
- ❌ Requires users to share password with CLI
- ❌ Less secure (password in memory during login)
- ❌ No token refresh mechanism
- ❌ If password changes, user must re-login

---

## Alternative: OAuth Flow with Local Server (Like Wrangler/Netlify)

**How it works:**
1. User runs `tito login`
2. CLI opens browser → redirects to your auth server
3. User logs in via web UI (more secure)
4. Auth server redirects to `http://localhost:PORT/callback?token=...`
5. CLI runs local server to catch the callback
6. Token saved to file

**Pros:**
- ✅ More secure (password never touches CLI)
- ✅ Better UX (web login form)
- ✅ Can implement token refresh
- ✅ Industry standard (used by AWS CLI, GitHub CLI, etc.)

**Cons:**
- ❌ More complex (need local server, browser opening)
- ❌ Requires network connectivity
- ❌ More code to maintain
- ❌ Port conflicts possible

---

## Recommendation: **Start Simple, Upgrade Later**

### Phase 1: File-Based (Current) ✅
**Use this if:**
- You want to ship fast
- Your API already supports username/password login
- Security requirements are moderate
- You want minimum code

**Implementation:** ✅ Already done!

### Phase 2: OAuth Flow (Future)
**Upgrade to this when:**
- You need better security
- You want token refresh
- You're building a public-facing tool
- You have time for the extra complexity

---

## Best Practices for Token Persistence

### 1. **File Storage Location**
```
~/.tito/token          # Token file
~/.tito/config.json    # Optional: other config
```
- ✅ Standard location (follows XDG conventions)
- ✅ Easy to find/backup
- ✅ Works across platforms

### 2. **Security**
- ✅ File permissions: `600` (owner read/write only)
- ✅ Directory permissions: `700` (owner only)
- ✅ Never log tokens
- ✅ Clear token on logout

### 3. **Token Usage Pattern**
```python
# In other commands, always check for token first
def some_command():
    token = load_token()
    if not token:
        print("Not logged in. Run 'tito login' first.")
        sys.exit(1)
    
    # Use token for API calls
    headers = {"Authorization": f"Bearer {token}"}
    # ... make API call
```

### 4. **Error Handling**
- ✅ Handle expired tokens gracefully
- ✅ Prompt to re-login if token invalid
- ✅ Don't crash on file permission errors

---

## Implementation Plan: Minimum Complexity Path

### Current State ✅
- [x] File-based token storage
- [x] Login/logout commands
- [x] Status command
- [x] Secure file permissions

### Next Steps (If Needed)

#### Option A: Keep It Simple (Recommended)
**Just use what we have!** File-based auth is fine for:
- Internal tools
- MVP/prototypes
- Tools where security is moderate

**Enhancements you could add:**
1. Token validation before API calls
2. Auto-refresh if API supports it
3. Better error messages

#### Option B: Add OAuth Flow (Later)
**Only if you need:**
- Public-facing tool
- Better security
- Token refresh

**Implementation would add:**
- ~100-150 lines of code
- Local HTTP server
- Browser opening logic
- Callback handling

---

## Code Structure (Current - Clean & Modular)

```
login_test.py
├── Token Persistence (3 functions)
│   ├── get_token_file_path()
│   ├── save_token()
│   ├── load_token()
│   └── clear_token()
│
├── API Authentication (1 function)
│   └── api_login()
│
└── CLI Commands (4 functions)
    ├── cmd_login()
    ├── cmd_logout()
    ├── cmd_status()
    └── show_help()
```

**Total: ~160 lines** - Clean, readable, maintainable!

---

## Comparison: Your Tool vs Others

| Tool | Method | Complexity |
|------|--------|------------|
| **Your CLI (current)** | File-based token | ⭐ Simple |
| Git | SSH keys / Credential helper | ⭐⭐ Medium |
| Wrangler | OAuth + local server | ⭐⭐⭐ Complex |
| Netlify CLI | OAuth + local server | ⭐⭐⭐ Complex |
| AWS CLI | File-based credentials | ⭐ Simple |

**Your approach is similar to AWS CLI** - simple and effective!

---

## Final Recommendation

**✅ Stick with file-based token storage** for now because:

1. **Minimum complexity** - You asked for this!
2. **Works immediately** - No extra infrastructure needed
3. **Easy to understand** - Anyone can read the code
4. **Sufficient security** - For most use cases
5. **Easy to upgrade** - Can add OAuth later if needed

**When to upgrade:**
- If you get security requirements that demand it
- If you need token refresh
- If you're building a public SaaS tool

**For now:** Your current implementation is clean, secure enough, and follows best practices! 🎉
