import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/health', '/ping'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"Hisab Kitab Telegram Bot","bot":"@Hisab_Kitab_1Bot","online":true}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence access logs to keep bot output clean
        return

def run_server(port: int):
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"[HTTP] Keep-alive server listening on 0.0.0.0:{port}")
        server.serve_forever()
    except Exception as e:
        print(f"Keep-alive server error: {e}")

def start_keep_alive() -> threading.Thread:
    port = int(os.environ.get("PORT", 8080))
    thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    import time
    start_keep_alive()
    print("Healthcheck server running standalone. Press Ctrl+C to stop.")
    while True:
        time.sleep(3600)
