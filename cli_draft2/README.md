# TinyTorch CLI (cli_draft2)

This folder contains a standalone command line interface for TinyTorch. It is
intended to be invoked as a small Python program for end-user interaction.

Development & setup
-------------------
1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run tests:

```bash
pytest -q
```

Design choices
--------------
- Minimal dependencies (standard library + requests/typer) to keep a tiny footprint.
- Local auth server uses `http.server` and runs on loopback only (127.0.0.1) for security.
- Credentials persisted to `~/.tinytorch/credentials.json` using atomic writes and secure file permissions.
- The CLI is intentionally decoupled from the web bridge; the bridge performs OAuth and redirects locally.

Commands
--------
- `login` – Launches browser to web bridge and collects tokens via a local callback server.
- `logout` – Clears local credentials.
- `status` – Shows whether the user is logged in.
- `leaderboard show` – Fetch leaderboard.
- `leaderboard submit` – Submit leaderboard score values (requires login).
