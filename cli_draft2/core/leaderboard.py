"""Leaderboard helpers for the CLI (standalone implementation).

Provides basic fetch and submit helpers that use `core.auth.get_token` for
authentication and `core.config` for endpoints so this code is self-contained
within `cli_draft2`.
"""
import requests
from typing import Optional, List, Dict

import config
from core import auth as core_auth


def fetch_leaderboard(limit: int = 10) -> Optional[List[Dict]]:
    try:
        response = requests.get(
            config.ENDPOINTS["leaderboard"],
            params={"limit": limit}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.HTTPError as e:
        # Bubble up or log
        return None
    except Exception:
        return None


def submit_score(overall_score: Optional[float] = None,
                 optimization_score: Optional[float] = None,
                 accuracy_score: Optional[float] = None,
                 successful_submissions: Optional[int] = None) -> bool:
    token = core_auth.get_token()
    if not token:
        return False

    payload = {}
    if overall_score is not None:
        payload["overall_score"] = float(overall_score)
    if optimization_score is not None:
        payload["optimization_score"] = float(optimization_score)
    if accuracy_score is not None:
        payload["accuracy_score"] = float(accuracy_score)
    if successful_submissions is not None:
        payload["successful_submissions"] = int(successful_submissions)

    if not payload:
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            config.ENDPOINTS["leaderboard"],
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return True
    except Exception:
        return False
