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
            <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
                <h1 style="color: green;">Login Successful</h1>
                <p>TinyTorch CLI is now authenticated.</p>
                <p>You can close this tab and return to your terminal.</p>
                <script>window.close()</script>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))
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

        # Start server in background thread
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

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
            finally:
                try:
                    self.server.server_close()
                except Exception:
                    pass
        if self.thread:
            self.thread.join(timeout=1)
        
