"""
Lightweight HTTP health-check server.
Render requires a port to be open even for worker processes.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os
import logging

logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - MindCare Bot is running")

    def log_message(self, format, *args):
        pass  # suppress access logs to keep console clean

def start_health_server(port: int = 8080):
    try:
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        logger.info(f"[Health] Server running on port {port}")
        print(f"[Health] Server running on port {port}")
    except Exception as e:
        logger.warning(f"[Health] Could not start health server: {e}")