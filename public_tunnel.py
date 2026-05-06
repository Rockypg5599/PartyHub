import argparse
import functools
import os
import socket
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pyngrok import ngrok
from pyngrok.exception import PyngrokNgrokError


class QuietHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


def port_is_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def start_server(port, directory):
    handler = functools.partial(QuietHandler, directory=str(directory))
    server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main():
    parser = argparse.ArgumentParser(description="Serve HackerArena publicly through ngrok.")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--directory", default="build/web")
    args = parser.parse_args()

    directory = Path(args.directory).resolve()
    if not directory.exists():
        raise SystemExit(f"Missing web build directory: {directory}")

    token = os.environ.get("NGROK_AUTHTOKEN")
    if token:
        ngrok.set_auth_token(token)

    server = None
    if port_is_open(args.port):
        print(f"Using existing local server on http://localhost:{args.port}/")
    else:
        server = start_server(args.port, directory)
        print(f"Serving {directory} on http://localhost:{args.port}/")

    try:
        tunnel = ngrok.connect(addr=args.port, proto="http")
    except PyngrokNgrokError as exc:
        raise SystemExit(
            "Ngrok needs an authtoken before it can open a public URL.\n"
            "Set it for this terminal, then run this script again:\n\n"
            "  export NGROK_AUTHTOKEN='your-token-here'\n"
            "  ./venv/bin/python public_tunnel.py --port 8001\n\n"
            "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
        ) from exc
    print(f"Public URL: {tunnel.public_url}")
    print("Press Ctrl+C to stop the tunnel.")

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nStopping tunnel...")
    finally:
        ngrok.disconnect(tunnel.public_url)
        ngrok.kill()
        if server:
            server.shutdown()


if __name__ == "__main__":
    main()
