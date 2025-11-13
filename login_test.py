import sys
import getpass
import asyncio
import requests
from pathlib import Path

# ============================================================================
# TOKEN PERSISTENCE UTILITIES
# ============================================================================

# Global variable to store the current session token
CURRENT_TOKEN = None

def get_token_file_path():
    """
    Get the path to the token file. 
    
    For Colab: Saves to /content/.tinytorch_token (persists during session)
    For local Jupyter: Saves to ~/.tinytorch_token (persists between sessions)
    
    NOTE: In Google Colab, this file will be lost when the runtime disconnects.
    To persist across Colab sessions, you would need to:
    1. Save to Google Drive (mounted at /content/drive/MyDrive/)
    2. Use Colab secrets (userdata.get('token'))
    3. Store in a GitHub gist or external service
    """
    try:
        import google.colab
        token_path = Path("/content/.tinytorch_token")
    except ImportError:
        token_path = Path.home() / ".tinytorch_token"
    
    return token_path

def save_token(token):
    """Save token to file and global variable"""
    global CURRENT_TOKEN
    CURRENT_TOKEN = token
    
    try:
        token_path = get_token_file_path()
        token_path.write_text(token)
        print(f"Token saved to: {token_path}")
        return True
    except Exception as e:
        print(f"Warning: Could not save token to file: {e}")
        return False

def load_token():
    """Load token from file or return global variable"""
    global CURRENT_TOKEN
    
    if CURRENT_TOKEN:
        return CURRENT_TOKEN
    
    try:
        token_path = get_token_file_path()
        if token_path.exists():
            CURRENT_TOKEN = token_path.read_text().strip()
            print(f"Token loaded from: {token_path}")
            return CURRENT_TOKEN
    except Exception as e:
        print(f"Could not load token from file: {e}")
    
    return None

def clear_token():
    """Clear token from memory and file"""
    global CURRENT_TOKEN
    CURRENT_TOKEN = None
    
    try:
        token_path = get_token_file_path()
        if token_path.exists():
            token_path.unlink()
            print("Token cleared")
    except Exception as e:
        print(f"Could not clear token file: {e}")

def show_help():
    """Prints the help message."""
    print("Welcome to Gizmo! 🚀")
    print("Usage: python gizmo.py [COMMAND]")
    print("\nCommands:")
    print("  run    : Run the main gizmo")
    print("  config : Configure gizmo settings")

def run_gizmo():
    """The function that runs the gizmo."""
    print("Gizmo is running... Vrrrrrroooom!")

def config_gizmo():
    """The function that configures the gizmo."""
    print("Configuring gizmo... beep boop.")


def api_login(email, password):
    """Authenticate with TinyTorch backend API"""
    try:
        response = requests.post(
            "https://tinytorch.netlify.app/api/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        
        token = response.json().get("access_token")
        if not token:
            return (
                None,                          # session_token
                "Login failed: No token in response.",  # status
                gr.update(visible=True),       # login_form
                gr.update(visible=False)       # main_app
            )

        # Save token to file and global variable
        save_token(token)
        
        return (
            token,                             # session_token
            "",                                # status (clear on success)
            gr.update(visible=False),          # login_form (hide)
            gr.update(visible=True)            # main_app (show)
        )
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e.response.status_code}")
        if e.response is not None:
            print(f"Response text: {e.response.text}")
        error_msg = e.response.json().get('detail', str(e)) if e.response else str(e)
        return (
            None,
            f"Login Failed: {error_msg}",
            gr.update(visible=True),
            gr.update(visible=False)
        )
        
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        if 'response' in locals() and response is not None:
            print(f"Raw response text: {response.text}")
        return (
            None,
            "Login Failed: Invalid JSON response from server. Check logs.",
            gr.update(visible=True),
            gr.update(visible=False)
        )
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return (
            None,
            f"An error occurred: {e}",
            gr.update(visible=True),
            gr.update(visible=False)
        )

def logout(session_token):
    """Handle logout"""
    clear_token()
    return (
        None,                          # Clear session_token
        "",                            # Clear status
        gr.update(visible=True),       # Show login_form
        gr.update(visible=False)       # Hide main_app
    )

def check_existing_session():
    """Check if there's an existing token on startup"""
    token = load_token()
    if token:
        print(f"Existing session found! Token: {token[:20]}...")
        return (
            token,                         # session_token
            "",                            # status
            gr.update(visible=False),      # login_form (hide)
            gr.update(visible=True)        # main_app (show)
        )
    else:
        return (
            None,
            "",
            gr.update(visible=True),
            gr.update(visible=False)
        )

# ============================================================================
# EXAMPLE: Using the token for API calls
# ============================================================================

def do_something_with_token(user_input, api_token):
    """Example function that uses the stored token"""
    if not api_token:
        return "You are not logged in."
    
    # Here you would make authenticated API calls using the token
    # Example: headers = {"Authorization": f"Bearer {api_token}"}
    return f"You said: '{user_input}'. Token available for API calls!"

    gg gg
def get_token(credentials: dict[str, str]) -> str:
    email = credentials["username"]
    password = credentials["password"]

    token = api_login(email, password):
    
    return token
def login_loop():
    try:
            creds = {}
            # This is the main loop that keeps the program active
            while True:
                print("Create an account at: https://tinytorch.netlify.app/login")
                # 1. READ: Get input from the user
                # The program will pause here and wait
                username = input("Tito username: ")
 
                if username:
                    pw = password = getpass.getpass("Password: ")  # Input is hidden
                    break
                else:
                    # Handle cases where the user just hits Enter
                    print("Please input your username and password")
                         except KeyboardInterrupt:
             # This makes sure Ctrl+C exits cleanly
             creds["username"] = username
             creds["password"] = pw
                

            print("\n\nCaught interrupt. Fleeing the well. Goodbye!")
# --- This is the main logic ---
# sys.argv is a list.
# sys.argv[0] is always the script name ("gizmo.py")
# sys.argv[1] is the *first* argument

# Try to get the command from sys.argv
try:
    command = sys.argv[1]
except IndexError:
    # If no command was given, show help and exit
    show_help()
    sys.exit(0) # Exit cleanly

# The main "router" for our CLI
if command == "run":
    run_gizmo()
elif command == "config":
    config_gizmo()
elif command == "help":
    show_help()
else:
    print(f"Error: Unknown command '{command}'")
    show_help()

# After the 'if' block finishes, the script just ends.
# It does not loop.
