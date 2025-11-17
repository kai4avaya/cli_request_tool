"""Leaderboard API operations"""

import requests
from config import ENDPOINTS
from auth import get_token


def fetch_leaderboard(limit=10):
    """Fetch leaderboard data (public, no auth required)"""
    try:
        response = requests.get(
            ENDPOINTS["leaderboard"],
            params={"limit": limit}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.HTTPError as e:
        if e.response:
            try:
                error_msg = e.response.json().get("error", str(e))
            except:
                error_msg = e.response.text or str(e)
            print(f"Error fetching leaderboard: {error_msg}")
        else:
            print(f"Error fetching leaderboard: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def submit_score(overall_score=None, optimization_score=None, 
                 accuracy_score=None, successful_submissions=None):
    """Submit/update leaderboard score (requires authentication)"""
    token = get_token()
    if not token:
        print("Error: Not logged in. Run 'tito login' first.")
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
        print("Error: At least one score field required.")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            ENDPOINTS["leaderboard"],
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        if e.response:
            try:
                error_msg = e.response.json().get("error", str(e))
            except:
                error_msg = e.response.text or str(e)
            print(f"Error submitting score: {error_msg}")
        else:
            print(f"Error submitting score: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
