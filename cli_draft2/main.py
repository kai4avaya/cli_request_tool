# src/tinytorch/main.py
import typer
import webbrowser
from rich.console import Console
from rich.table import Table
from core.auth_server import AuthReceiver
from core import storage
from core import auth as core_auth
from core import leaderboard as core_leaderboard
from core import submissions as core_submissions
from core import colors
import config


app = typer.Typer()
console = Console()
leaderboard_app = typer.Typer()
app.add_typer(leaderboard_app, name="leaderboard")
submissions_app = typer.Typer()
app.add_typer(submissions_app, name="submissions", invoke_without_command=True)


@app.command()
def login():
    """
    Log in to TinyTorch via the web browser.
    """
    # If already logged in, bail early
    if core_auth.is_logged_in():
        s = core_auth.load_session()
        console.print(f"[{colors.COLOR_SUCCESS}]Already logged in as {s.get('user_email')}[/{colors.COLOR_SUCCESS}]")
        return

    receiver = AuthReceiver()
    
    # 1. Start local listener
    try:
        port = receiver.start()
    except Exception as e:
        console.print(f"[{colors.COLOR_ERROR}]Error starting local server: {e}[/{colors.COLOR_ERROR}]")
        raise typer.Exit(1)

    # 2. Construct URL
    target_url = f"{config.ENDPOINTS['cli_login']}?redirect_port={port}"
    
    console.print(f"Opening browser to: [{colors.COLOR_INFO}]{target_url}[/{colors.COLOR_INFO}]")
    console.print("Waiting for authentication...")
    
    # 3. Open Browser
    webbrowser.open(target_url)
    
    # 4. Wait (Block)
    tokens = receiver.wait_for_tokens()
    
    if tokens:
        # 5. Save to disk
        storage.save_credentials(tokens)
        console.print(f"[{colors.COLOR_SUCCESS}]Success! Logged in as {tokens['user_email']}[/{colors.COLOR_SUCCESS}]")
    else:
        console.print(f"[{colors.COLOR_ERROR}]Login timed out.[/{colors.COLOR_ERROR}]")
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
    
    # Create a Rich table with color scheme
    table = Table(title="Leaderboard", show_header=True, header_style=f"bold {colors.COLOR_HEADER}")
    
    # Add columns with color scheme
    table.add_column("Rank", style=colors.COLOR_RANK, justify="right")
    table.add_column("User ID", style=colors.COLOR_NAME, no_wrap=True, max_width=36)
    table.add_column("Overall Score", style=colors.COLOR_TOTAL, justify="right")
    
    # Add optional columns if they exist in data
    has_optimization = any("optimization_score" in row for row in data)
    has_accuracy = any("accuracy_score" in row for row in data)
    has_submissions = any("successful_submissions" in row for row in data)
    
    if has_optimization:
        table.add_column("Optimization", style=colors.COLOR_SPEED, justify="right")
    if has_accuracy:
        table.add_column("Accuracy", style=colors.COLOR_ACCURACY, justify="right")
    if has_submissions:
        table.add_column("Submissions", style=colors.COLOR_RANK, justify="right")
    
    # Add rows
    for idx, row in enumerate(data, start=1):
        user_id = str(row.get("user_id", ""))[:36]
        overall_score = row.get("overall_score", "N/A")
        
        row_data = [str(idx), user_id, str(overall_score)]
        
        if has_optimization:
            row_data.append(str(row.get("optimization_score", "N/A")))
        if has_accuracy:
            row_data.append(str(row.get("accuracy_score", "N/A")))
        if has_submissions:
            row_data.append(str(row.get("successful_submissions", "N/A")))
        
        table.add_row(*row_data)
    
    console.print(table)


@leaderboard_app.command("submit")
def leaderboard_submit(overall_score: float = None, optimization_score: float = None,
                       accuracy_score: float = None, successful_submissions: int = None):
    """Submit/update leaderboard score (requires login)"""
    ok = core_leaderboard.submit_score(overall_score, optimization_score, accuracy_score, successful_submissions)
    if ok:
        console.print(f"[{colors.COLOR_SUCCESS}]Submitted leaderboard score.[/{colors.COLOR_SUCCESS}]")
    else:
        console.print(f"[{colors.COLOR_ERROR}]Failed to submit leaderboard. Make sure you are logged in and provided at least one score.[/{colors.COLOR_ERROR}]")


@submissions_app.command("submit")
def submissions_submit(
    problem_id: str = typer.Argument(..., help="UUID of the problem"),
    code: str = typer.Option(..., "--code", "-c", help="Code to submit"),
    language: str = typer.Option(None, "--language", "-l", help="Programming language")
):
    """Submit code for a problem (requires login)"""
    if not core_auth.is_logged_in():
        console.print(f"[{colors.COLOR_ERROR}]Error: You must be logged in to submit code.[/{colors.COLOR_ERROR}]")
        raise typer.Exit(1)
    
    ok = core_submissions.submit_code(problem_id, code, language)
    if ok:
        console.print(f"[{colors.COLOR_SUCCESS}]Successfully submitted code.[/{colors.COLOR_SUCCESS}]")
    else:
        console.print(f"[{colors.COLOR_ERROR}]Failed to submit code. Please check your problem_id and try again.[/{colors.COLOR_ERROR}]")
        raise typer.Exit(1)


@submissions_app.callback(invoke_without_command=True)
def submissions_callback(
    ctx: typer.Context,
    mine: bool = typer.Option(False, "--mine", "-m", help="Show only your submissions"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of submissions to show")
):
    """Show submissions (default: shows up to 10 recent submissions, use --mine for your submissions)"""
    if ctx.invoked_subcommand is not None:
        return
    
    if mine and not core_auth.is_logged_in():
        console.print(f"[{colors.COLOR_ERROR}]Error: You must be logged in to view your submissions.[/{colors.COLOR_ERROR}]")
        raise typer.Exit(1)
    
    data = core_submissions.fetch_submissions(limit=limit, mine=mine)
    if data is None:
        console.print(f"[{colors.COLOR_ERROR}]Error: Failed to fetch submissions. The API endpoint may not be available yet.[/{colors.COLOR_ERROR}]")
        raise typer.Exit(1)
    
    if not data:
        if mine:
            console.print("No submissions found for your account.")
        else:
            console.print("No submissions found.")
        return
    
    # Create a Rich table with color scheme
    table = Table(
        title="Submissions" if not mine else "My Submissions", 
        show_header=True, 
        header_style=f"bold {colors.COLOR_HEADER}"
    )
    
    # Add columns with color scheme
    table.add_column("ID", style=colors.COLOR_RANK, no_wrap=True, max_width=36)
    table.add_column("Problem ID", style=colors.COLOR_NAME, no_wrap=True, max_width=36)
    table.add_column("Language", style=colors.COLOR_SPEED)
    table.add_column("Status", style=colors.COLOR_ACCURACY)
    table.add_column("Created At", style=colors.COLOR_TOTAL)
    
    # Add rows
    for row in data:
        submission_id = str(row.get("id", ""))[:36]
        problem_id = str(row.get("problem_id", ""))[:36]
        language = row.get("language", "N/A")
        status = row.get("status", "N/A")
        created_at = row.get("created_at", "N/A")
        
        # Format created_at if it's a timestamp
        if created_at and created_at != "N/A":
            try:
                # Try to format timestamp if it's a string
                if "T" in created_at:
                    created_at = created_at.split("T")[0] + " " + created_at.split("T")[1].split(".")[0]
            except:
                pass
        
        table.add_row(submission_id, problem_id, language, status, created_at)
    
    console.print(table)

if __name__ == "__main__":
    app()