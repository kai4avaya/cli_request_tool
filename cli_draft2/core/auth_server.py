import http.server
import threading
import socket
import time
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict

import config
from core import storage

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    """
    Handles the single request from the browser.
    Extracts query parameters and stores them in the server instance.
    """
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Handle logout route - redirects to frontend logout
        if parsed_path.path == "/logout":
            self.send_response(302)  # Redirect
            self.send_header('Location', f"{config.API_BASE_URL}/logout")
            self.end_headers()
            return
        
        if parsed_path.path != config.AUTH_CALLBACK_PATH:
            self.send_error(404, "Not Found")
            return
        query_params = parse_qs(parsed_path.query)

        if 'access_token' in query_params and 'refresh_token' in query_params:
            self.server.auth_data = {
                'access_token': query_params['access_token'][0],
                'refresh_token': query_params['refresh_token'][0],
                'user_email': query_params.get('email', [''])[0]
            }
            
            # 5. Send "Success" Page to Browser
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = """
            <html>
            <head>
                <title>Login Successful</title>
            </head>
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1 style="color: green;">Login Successful</h1>
                <p>TinyTorch CLI is now authenticated.</p>
                <p>You can close this tab and return to your terminal.</p>
                <p style="margin-top: 30px;">
                    <a href="https://tinytorch.netlify.app/dashboard" target="_blank" style="color: #6b8bd6; text-decoration: none; font-weight: bold; padding: 10px 20px; border: 2px solid #6b8bd6; border-radius: 5px; display: inline-block; margin-right: 10px;">
                        View Leaderboard ->
                    </a>
                    <a href="/logout" style="color: #d66b6b; text-decoration: none; font-weight: bold; padding: 10px 20px; border: 2px solid #d66b6b; border-radius: 5px; display: inline-block;">
                        Logout & Switch Account
                    </a>
                </p>
                <p style="margin-top: 20px; color: #666; font-size: 0.9em;">
                    Need to switch accounts? Click "Logout & Switch Account" above, then run <code>tinytorch login</code> again.
                </p>
                <p style="margin-top: 30px; color: #666;">
                    This window will close automatically in <span id="countdown" style="font-weight: bold; color: #333;">20</span> seconds.
                </p>
                <p style="color: #999; font-size: 0.9em; margin-top: 10px;">
                    (You can close it manually if you'd like)
                </p>
                <script>
                    let timeLeft = 20;
                    const countdownElement = document.getElementById('countdown');
                    
                    const timer = setInterval(function() {
                        timeLeft--;
                        countdownElement.textContent = timeLeft;
                        
                        if (timeLeft <= 0) {
                            clearInterval(timer);
                            window.close();
                        }
                    }, 1000);
                </script>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
            self.wfile.flush()  # Ensure response is sent before server might shut down
            # Persist immediately as a fail-safe
            try:
                storage.save_credentials(self.server.auth_data)
            except Exception:
                pass
        else:
            # Handle error case
            self.send_error(400, "Missing tokens in callback URL")

    # Suppress default logging to keep CLI clean
    def log_message(self, format, *args):
        pass


class LocalAuthServer(http.server.HTTPServer):
    """
    Extended HTTPServer that holds the captured auth data.
    """
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.auth_data: Optional[Dict[str, str]] = None


class AuthReceiver:
    """
    The public interface for the CLI to use.
    Manages the thread and the server lifecycle.
    """
    def __init__(self, start_port: int = None):
        # Use default from config if not supplied
        self.start_port = start_port if start_port is not None else config.AUTH_START_PORT
        self.server: Optional[LocalAuthServer] = None
        self.thread: Optional[threading.Thread] = None
        self.port: int = 0
        # Ensure any previous instance is cleaned up
        self._cleanup_previous()

    def _cleanup_previous(self):
        """Clean up any previous server instances that might be lingering."""
        # This is a safety measure - in practice, stop() should be called
        # but this ensures we don't have orphaned servers
        pass
    
    def start(self)  -> int:
        """
        Finds an available port, starts the server in a background thread.
        Returns the port number used.
        """
        port = self.start_port
        max_port = self.start_port + config.AUTH_PORT_HUNT_RANGE
        while True:
            try:
                self.server = LocalAuthServer((config.LOCAL_SERVER_HOST, port), CallbackHandler)
                # If we bound to port 0 the OS picked a free port; use the actual
                # socket address returned by the server to get the bound port.
                self.port = self.server.server_address[1]
                break
            except OSError:
                port += 1
                if port > max_port:
                    raise Exception("Could not find an open port for authentication.")

        # Start server in background thread with error handling
        def serve_with_error_handling():
            try:
                self.server.serve_forever()
            except Exception as e:
                # Log error if server fails (could add logging here)
                pass
        
        self.thread = threading.Thread(target=serve_with_error_handling, daemon=True)
        self.thread.start()
        
        # Wait a moment to ensure server is ready to accept connections
        # Give the thread a moment to start
        time.sleep(0.2)
        
        # Check if server socket is actually listening by trying to connect
        max_wait = 2.0  # seconds
        wait_interval = 0.1
        waited = 0.0
        server_ready = False
        
        while waited < max_wait:
            try:
                # Check if thread is still alive
                if not self.thread.is_alive():
                    break
                    
                # Try to connect to verify server is listening
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.settimeout(0.2)
                result = test_socket.connect_ex((config.LOCAL_SERVER_HOST, self.port))
                test_socket.close()
                if result == 0:  # Connection successful means server is listening
                    server_ready = True
                    break
            except Exception:
                pass
            time.sleep(wait_interval)
            waited += wait_interval
        
        if not server_ready:
            # Server didn't become ready, clean up and raise error
            self.stop()
            raise Exception(f"Server failed to start listening on port {self.port} within {max_wait} seconds")

        return self.port

    
    def wait_for_tokens(self, timeout: int = 120) -> Optional[Dict[str, str]]:
        """
        Waits for the authentication tokens to be received or until timeout.
        Returns the auth data dictionary or None if timeout occurs.
        """
        import time
        start_time = time.time()

        try:
            while getattr(self.server, "auth_data", None) is None:
                if time.time() - start_time > timeout:
                    return None
                time.sleep(0.25)
            
            # Persist again (defense in depth) before returning
            try:
                storage.save_credentials(self.server.auth_data)
            except Exception:
                pass
            
            # Wait long enough to ensure the browser receives the success page
            # and the countdown timer can run. This prevents "connection refused" errors
            # in the browser even though login was successful.
            # The page auto-closes after 20 seconds, so we wait 22 seconds to be safe.
            time.sleep(22.0)
            
            return self.server.auth_data
        finally:
            self.stop() # Ensure server is stopped after waiting
        
    def stop(self):
        """
        Stops the server and joins the thread.
        """
        if self.server:
            try:
                self.server.shutdown()
            except Exception:
                pass
            finally:
                try:
                    self.server.server_close()
                except Exception:
                    pass
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        
