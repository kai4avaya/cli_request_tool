# Tito CLI Tool

Simple CLI tool for interacting with TinyTorch leaderboard API.

## Structure

```
cli/
├── main.py           # Entry point
├── config.py         # Configuration (API URLs, defaults)
├── auth.py           # Authentication & session management
├── leaderboard.py    # Leaderboard API operations
├── cli.py            # CLI command handlers
└── tests/            # Test suite
    ├── test_auth.py
    ├── test_leaderboard.py
    ├── test_cli.py
    └── run_tests.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Login
python main.py login

# View leaderboard (top 10)
python main.py leaderboard

# View top 20
python main.py leaderboard 20

# Submit score
python main.py submit --overall-score 100.5 --optimization-score 50.0

# Check status
python main.py status

# Logout
python main.py logout
```

## Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Or run individual test files
python -m unittest tests.test_auth
python -m unittest tests.test_leaderboard
python -m unittest tests.test_cli
```

## Commands

- `login` - Authenticate and save session
- `logout` - Clear saved session
- `status` - Show current login status
- `leaderboard [N]` - Display top N entries (default: 10)
- `submit` - Submit/update leaderboard score
  - `--overall-score NUM`
  - `--optimization-score NUM`
  - `--accuracy-score NUM`
  - `--successful-submissions NUM`
- `help` - Show help message

## Examples

```bash
tito leaderboard 20
tito submit --overall-score 100.5 --optimization-score 50.0
```
