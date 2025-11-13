# Tito CLI Tool

CLI tool for TinyTorch Systems authentication and management.

## Installation

### Option 1: Quick Start (Development)

```bash
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# or
uv pip install -r requirements.txt

# Run directly
python login_test.py login
```

### Option 2: Install as package (Production)

```bash
# Install in editable mode (for development)
pip install -e .
# or
uv pip install -e .

# Then use the 'tito' command
tito login
tito status
tito logout
```

### Option 3: Build and install package

```bash
# Build the package
pip install build
python -m build

# Install the built package
pip install dist/tito_cli-0.1.0-py3-none-any.whl

# Use the 'tito' command
tito login
```

## Usage

```bash
# Login
tito login

# Check status
tito status

# Logout
tito logout

# Show help
tito help
```

## How Dependencies Work

When you install this package via `pip` or `uv`, the installer automatically:

1. Reads `pyproject.toml` (or `setup.py`)
2. Finds the `dependencies` list
3. Installs all required packages (like `requests`)
4. Installs your package

**You don't bundle dependencies** - you declare them, and pip/uv handles installation automatically!

## Development

```bash
# Install in editable mode
pip install -e .

# Make changes to code
# Changes are immediately available (no reinstall needed)
```

## Project Structure

```
.
├── login_test.py      # Main CLI code
├── pyproject.toml     # Package metadata & dependencies
├── requirements.txt   # Development dependencies
└── README.md          # This file
```
