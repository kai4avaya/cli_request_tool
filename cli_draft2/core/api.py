# src/tinytorch/main.py
import typer
import webbrowser
from rich.console import Console
from core.auth_server import AuthReceiver
from core import storage 
import config
app = typer.Typer()
console = Console()

WEB_BRIDGE_URL = config.ENDPOINTS['cli_login']

@app.command()
def login():
    """
    Log in to TinyTorch via the web browser.
    """
    receiver = AuthReceiver()
    
    # 1. Start local listener
    try:
        port = receiver.start()
    except Exception as e:
        console.print(f"[red]Error starting local server: {e}[/red]")
        raise typer.Exit(1)

    # 2. Construct URL
    target_url = f"{WEB_BRIDGE_URL}?redirect_port={port}"
    
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

if __name__ == "__main__":
    app()