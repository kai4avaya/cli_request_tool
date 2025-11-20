"""Submissions helpers for the CLI.

Provides fetch and submit helpers that use `core.auth.get_token` for
authentication and `core.config` for endpoints.
"""
import requests
from typing import Optional, List, Dict

import config
from core import auth as core_auth


def fetch_submissions(limit: int = 10, mine: bool = False) -> Optional[List[Dict]]:
    """Fetch submissions from the API.
    
    Args:
        limit: Maximum number of submissions to return (default: 10)
        mine: If True, only fetch current user's submissions (requires auth)
    
    Returns:
        List of submission dictionaries or None on error
    """
    token = core_auth.get_token()
    headers = {}
    
    # Always send auth token if available (for RLS policies)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    params = {"limit": limit}
    if mine:
        params["mine"] = "true"
        if not token:
            return None
    
    url = config.ENDPOINTS["submissions"]
    
    # Log the request details
    print(f"[DEBUG] Fetching submissions from: {url}")
    print(f"[DEBUG] Params: {params}")
    print(f"[DEBUG] Has auth token: {bool(token)}")
    print(f"[DEBUG] Mine: {mine}")
    
    try:
        response = requests.get(
            url,
            headers=headers if headers else None,
            params=params
        )
        
        # Log response details
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response headers: {dict(response.headers)}")
        
        response.raise_for_status()
        data = response.json()
        
        # Log response data structure
        print(f"[DEBUG] Response type: {type(data)}")
        if isinstance(data, dict):
            print(f"[DEBUG] Response keys: {list(data.keys())}")
        if isinstance(data, list):
            print(f"[DEBUG] Response array length: {len(data)}")
        else:
            print(f"[DEBUG] Response data (first 500 chars): {str(data)[:500]}")
        
        # Handle both {"data": [...]} and direct array responses
        if isinstance(data, list):
            result = data
        elif "submissions" in data:
            result = data["submissions"]
        else:
            result = data.get("data", [])
        
        print(f"[DEBUG] Returning {len(result)} submissions")
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"[DEBUG] HTTP Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"[DEBUG] Error response status: {e.response.status_code}")
            try:
                error_body = e.response.text[:500]
                print(f"[DEBUG] Error response body: {error_body}")
            except:
                pass
        # Return empty list instead of None to distinguish between error and no results
        if hasattr(e, 'response') and e.response.status_code == 404:
            return []  # Endpoint doesn't exist yet
        return None
    except Exception as e:
        print(f"[DEBUG] Exception: {type(e).__name__}: {e}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return None


def submit_code(problem_id: str, code: str, language: Optional[str] = None) -> bool:
    """Submit code for a problem.
    
    Args:
        problem_id: UUID of the problem
        code: The code to submit
        language: Optional language identifier
    
    Returns:
        True if successful, False otherwise
    """
    token = core_auth.get_token()
    if not token:
        return False
    
    payload = {
        "problem_id": problem_id,
        "code": code
    }
    if language:
        payload["language"] = language
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            config.ENDPOINTS["submissions"],
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return True
    except Exception:
        return False
