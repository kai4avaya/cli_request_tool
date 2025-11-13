# Python Package Dependency Management Explained

## Quick Answer

**You declare dependencies, you don't bundle them!**

When someone installs your package via `pip install tito-cli` or `uv pip install tito-cli`, the installer automatically reads your dependency list and installs everything needed.

---

## How It Works

### 1. **You Declare Dependencies**

In `pyproject.toml`:
```toml
[project]
dependencies = [
    "requests>=2.31.0",
]
```

### 2. **User Installs Your Package**

```bash
pip install tito-cli
# or
uv pip install tito-cli
```

### 3. **Installer Automatically:**

1. Reads `pyproject.toml`
2. Sees `requests>=2.31.0` in dependencies
3. Installs `requests` automatically
4. Installs your package
5. Done! ✅

**The user never needs to manually install `requests`!**

---

## File Types Explained

### `pyproject.toml` (Modern Standard) ✅
**Purpose:** Package metadata + dependencies  
**Used by:** pip, uv, poetry, and all modern Python tools

```toml
[project]
name = "tito-cli"
version = "0.1.0"
dependencies = [
    "requests>=2.31.0",
]
```

**When to use:** Always! This is the modern standard.

### `requirements.txt` (Simple/Development)
**Purpose:** Simple list of dependencies  
**Used by:** `pip install -r requirements.txt`

```
requests>=2.31.0
```

**When to use:** 
- Quick development setup
- CI/CD pipelines
- Docker containers
- Simple projects

### `setup.py` (Legacy)
**Purpose:** Old way to define packages  
**Used by:** pip (legacy)

```python
setup(
    install_requires=["requests>=2.31.0"]
)
```

**When to use:** Only if you need to support very old Python/pip versions.

---

## Real-World Examples

### Example 1: Installing a Package

```bash
# User runs this:
pip install requests

# What happens:
# 1. pip downloads requests
# 2. pip reads requests' pyproject.toml/setup.py
# 3. pip sees requests needs: urllib3, certifi, charset-normalizer
# 4. pip installs those automatically
# 5. pip installs requests
# Done! User never manually installed urllib3!
```

### Example 2: Your Package

```bash
# User runs this:
pip install tito-cli

# What happens:
# 1. pip downloads tito-cli
# 2. pip reads tito-cli's pyproject.toml
# 3. pip sees tito-cli needs: requests>=2.31.0
# 4. pip installs requests automatically
# 5. pip installs tito-cli
# Done! User can now run 'tito login'!
```

---

## Best Practices

### ✅ DO:
- Declare all dependencies in `pyproject.toml`
- Use version constraints: `requests>=2.31.0`
- Keep `requirements.txt` in sync (optional, for convenience)

### ❌ DON'T:
- Bundle dependencies in your package
- Assume users will install dependencies manually
- Use `requirements.txt` as your only dependency file (use `pyproject.toml`)

---

## Version Constraints

```toml
dependencies = [
    "requests>=2.31.0",        # At least version 2.31.0
    "click==8.1.0",            # Exactly version 8.1.0
    "pytest~=7.0.0",           # Compatible with 7.0.x
    "numpy>=1.20.0,<2.0.0",    # Between 1.20.0 and 2.0.0
]
```

---

## Development vs Production Dependencies

### Production Dependencies (Required)
```toml
[project]
dependencies = [
    "requests>=2.31.0",  # Needed to run the tool
]
```

### Development Dependencies (Optional)
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",     # Only needed for testing
    "black>=23.0.0",     # Only needed for formatting
]

# Install with:
# pip install tito-cli[dev]
```

---

## Your Current Setup

✅ **You have:**
- `pyproject.toml` - Declares `requests>=2.31.0`
- `requirements.txt` - For quick dev setup

✅ **When someone installs:**
```bash
pip install -e .  # Installs requests automatically!
```

✅ **When you develop:**
```bash
pip install -r requirements.txt  # Quick setup
```

**Everything is set up correctly!** 🎉

---

## Summary

1. **Declare** dependencies in `pyproject.toml`
2. **Don't bundle** them - pip/uv handles it
3. **Users install** your package → dependencies install automatically
4. **That's it!** Simple and standard.
