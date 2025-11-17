# src/tinytorch/main.py
import typer
import webbrowser
from rich.console import Console
from core.auth_server import AuthReceiver
from core import storage
from core import auth as core_auth
from core import leaderboard as core_leaderboard
import config


app = typer.Typer()
console = Console()
leaderboard_app = typer.Typer()
app.add_typer(leaderboard_app, name="leaderboard")


@app.command()
def login():
    """
    Log in to TinyTorch via the web browser.
    """
    # If already logged in, bail early
    if core_auth.is_logged_in():
        s = core_auth.load_session()
        console.print(f"[green]Already logged in as {s.get('user_email')}[/green]")
        return

    receiver = AuthReceiver()
    
    # 1. Start local listener
    try:
        port = receiver.start()
    except Exception as e:
        console.print(f"[red]Error starting local server: {e}[/red]")
        raise typer.Exit(1)

    # 2. Construct URL
    target_url = f"{config.ENDPOINTS['cli_login']}?redirect_port={port}"
    
    console.print(f"Opening browser to: [blue]{target_url}[/blue]")
    console.print("Waiting for authentication...")
    
    # 3. Open Browser
    webbrowser.open(target_url)
    
    # 4. Wait (Block)
    tokens = receiver.wait_for_tokens()
    
    if tokens:
        # 5. Save to disk
        storage.save_credentials(tokens)
        console.print(f"[green]Success! Logged in as {tokens['user_email']}[/green]")
    else:
        console.print("[red]Login timed out.[/red]")
        raise typer.Exit(1)


@app.command()
def status():
    """Show login status"""
    s = core_auth.load_session()
    if not s:
        console.print("Not logged in.")
    else:
        console.print(f"Logged in as: {s.get('user_email')}")


@app.command()
def logout():
    """Logout by clearing saved credentials"""
    ok = core_auth.clear_session()
    if ok:
        console.print("Logged out.")
    else:
        console.print("No session to clear.")


@leaderboard_app.command("show")
def leaderboard_show(limit: int = 10):
    """Show the leaderboard"""
    data = core_leaderboard.fetch_leaderboard(limit=limit)
    if not data:
        console.print("Leaderboard is empty.")
        return
    # Pretty print simple table (rudimentary)
    console.print("Leaderboard:")
    for row in data:
        console.print(f"- {row.get('user_id')}: {row.get('overall_score')}")


@leaderboard_app.command("submit")
def leaderboard_submit(overall_score: float = None, optimization_score: float = None,
                       accuracy_score: float = None, successful_submissions: int = None):
    """Submit/update leaderboard score (requires login)"""
    ok = core_leaderboard.submit_score(overall_score, optimization_score, accuracy_score, successful_submissions)
    if ok:
        console.print("Submitted leaderboard score.")
    else:
        console.print("Failed to submit leaderboard. Make sure you are logged in and provided at least one score.")

if __name__ == "__main__":
    app()