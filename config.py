"""Shared configuration for Tito CLI"""

# API Configuration
API_BASE_URL = "https://tinytorch.netlify.app"

# API Endpoints
ENDPOINTS = {
    "login": f"{API_BASE_URL}/api/auth/login",
    "leaderboard": f"{API_BASE_URL}/api/leaderboard",
}

# Defaults
DEFAULT_LEADERBOARD_LIMIT = 10
