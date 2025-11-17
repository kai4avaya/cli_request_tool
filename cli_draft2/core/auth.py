"""High-level auth helpers for the CLI that wrap secure storage.

This module intentionally mirrors the top-level `auth.py` helper style
but uses `core.storage` and `core.config` so the `cli_draft2` directory
can function as a standalone application.
"""
from typing import Optional, Dict

from core import storage


def save_session(session_data: Dict[str, str]) -> bool:
    try:
        storage.save_credentials(session_data)
        return True
    except Exception:
        return False


def load_session() -> Optional[Dict[str, str]]:
    return storage.load_credentials()


def clear_session() -> bool:
    try:
        storage.delete_credentials()
        return True
    except Exception:
        return False


def get_token() -> Optional[str]:
    s = load_session()
    if s:
        return s.get("access_token")
    return None


def is_logged_in() -> bool:
    return get_token() is not None
