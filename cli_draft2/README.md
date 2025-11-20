# TinyTorch CLI (cli_draft2)

A standalone command line interface for TinyTorch. This CLI provides a clean interface for interacting with TinyTorch services including authentication, leaderboards, and code submissions.

## Development & Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Run tests:

```bash
pytest -q
```

3. Run the CLI:

```bash
python main.py --help
```

## Backend API Access

The CLI communicates with the TinyTorch backend API at `https://tinytorch.netlify.app`. API endpoints are configured in `config.py`:

- **Authentication**: `/api/auth/login` - User authentication
- **Leaderboard**: `/api/leaderboard` - GET (public) and POST (authenticated)
- **Submissions**: `/api/submissions` - GET (public or authenticated) and POST (authenticated)
- **CLI Login Bridge**: `/cli-login` - Web bridge for OAuth-style login flow

### Authentication Flow

1. User runs `login` command
2. CLI starts a local HTTP server on `127.0.0.1` (port 54321+)
3. Opens browser to `/cli-login?redirect_port={port}`
4. Web bridge handles OAuth and redirects back to local server with tokens
5. Tokens are saved to `~/.tinytorch/credentials.json`
6. Subsequent API calls include `Authorization: Bearer {access_token}` header

### API Request Pattern

- **Public endpoints** (leaderboard show, submissions show without `--mine`): No authentication required
- **Authenticated endpoints** (submissions submit, leaderboard submit, submissions show with `--mine`): 
  - Token retrieved from `core.auth.get_token()`
  - Added as `Authorization: Bearer {token}` header
  - Returns `None`/`False` if authentication fails

All API calls use the `requests` library and handle errors gracefully, returning `None` or `False` on failure.

## Commands

### Authentication

- **`login`** – Launches browser to web bridge and collects tokens via a local callback server.
  ```bash
  python main.py login
  ```

- **`logout`** – Clears local credentials.
  ```bash
  python main.py logout
  ```

- **`status`** – Shows whether the user is logged in and displays current user email.
  ```bash
  python main.py status
  ```

### Leaderboard

- **`leaderboard show [--limit LIMIT]`** – Display the leaderboard in a formatted table (default: 10 entries).
  ```bash
  python main.py leaderboard show
  python main.py leaderboard show --limit 20
  ```
  Shows: Rank, User ID, Overall Score, and optionally Optimization Score, Accuracy Score, and Successful Submissions.

- **`leaderboard submit [--overall-score SCORE] [--optimization-score SCORE] [--accuracy-score SCORE] [--successful-submissions COUNT]`** – Submit or update leaderboard score values (requires login).
  ```bash
  python main.py leaderboard submit --overall-score 95.5 --optimization-score 90.0
  ```

### Submissions

- **`submissions submit <problem_id> --code CODE [--language LANGUAGE]`** – Submit code for a problem (requires login).
  ```bash
  python main.py submissions submit <problem-uuid> --code "def solution(): ..." --language python
  ```

- **`submissions show [--mine] [--limit LIMIT]`** – Display submissions in a formatted table.
  ```bash
  python main.py submissions show              # Shows up to 10 recent submissions
  python main.py submissions show --mine       # Shows only your submissions (requires login)
  python main.py submissions show --limit 20  # Show up to 20 submissions
  ```
  Shows: ID, Problem ID, Language, Status, and Created At timestamp.
