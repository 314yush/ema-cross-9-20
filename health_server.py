"""
Health check HTTP server to prevent Railway from sleeping.
Runs in a separate thread and responds to health check requests.
"""
import http.server
import socketserver
import threading
import json
from datetime import datetime
from typing import Optional


class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for health check endpoints."""
    
    def __init__(self, *args, bot_status: Optional[dict] = None, **kwargs):
        self.bot_status = bot_status or {}
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "bot": self.bot_status.get("status", "running"),
                "checks": self.bot_status.get("checks", 0),
                "last_check": self.bot_status.get("last_check", "N/A"),
            }
            
            self.wfile.write(json.dumps(status, indent=2).encode())
        elif self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'pong')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        # Only log errors, not every request
        if args[1] != '200':
            super().log_message(format, *args)


class HealthServer:
    """Health check server that runs in a separate thread."""
    
    def __init__(self, port: Optional[int] = None, bot_status: Optional[dict] = None):
        """
        Initialize health check server.
        
        Args:
            port: Port to run the server on. If None, uses PORT env var or defaults to 8080
            bot_status: Dictionary to store bot status (shared reference)
        """
        # Railway provides PORT environment variable automatically
        # Use it if available, otherwise use HEALTH_CHECK_PORT or default to 8080
        import os
        self.port = port or int(os.getenv("PORT", os.getenv("HEALTH_CHECK_PORT", "8080")))
        self.bot_status = bot_status or {}
        self.server: Optional[socketserver.TCPServer] = None
        self.thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start the health check server in a separate thread."""
        def create_handler(*args, **kwargs):
            return HealthCheckHandler(*args, bot_status=self.bot_status, **kwargs)
        
        try:
            self.server = socketserver.TCPServer(("", self.port), create_handler)
            self.server.allow_reuse_address = True
            
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            
            print(f"✅ Health check server started on port {self.port}")
            print(f"   Health endpoint: http://0.0.0.0:{self.port}/health")
            print(f"   Ping endpoint: http://0.0.0.0:{self.port}/ping")
        except Exception as e:
            print(f"⚠️  Could not start health check server: {e}")
            print(f"   Bot will continue running, but may sleep on Railway free tier")
    
    def stop(self):
        """Stop the health check server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("🛑 Health check server stopped")
    
    def update_status(self, checks: int = 0, last_check: str = "N/A", status: str = "running"):
        """Update bot status for health check endpoint."""
        self.bot_status.update({
            "status": status,
            "checks": checks,
            "last_check": last_check,
        })

