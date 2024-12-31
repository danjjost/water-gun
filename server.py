#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import RPi.GPIO as GPIO

from water_gun import WaterGun

# ---------------- CONFIGURATION ----------------
SERVER_PORT = 3020
# -----------------------------------------------

# Instantiate the WaterGun (global so our handler can access it)
water_gun = WaterGun()

class SimpleRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read the POST body and parse any 'hold_time'
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8').strip()

        # Call water_gun.fire()
        water_gun.fire()

        # Send back a simple response
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Fired water gun.\n")


def run_server(port=SERVER_PORT):
    print(f"Starting server on port {port}...")
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleRequestHandler)
    print("Server started. Press Ctrl+C to stop.")
    httpd.serve_forever()


if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
        print("Cleaned up GPIO and stopped the server.")
