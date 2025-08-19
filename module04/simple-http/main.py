from http.server import BaseHTTPRequestHandler, HTTPServer



class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open("clock.html", "rb") as f:
            self.wfile.write(f.read())

server = HTTPServer(("", 8001), HTTPHandler)

try:
    server.serve_forever()
except KeyboardInterrupt:
    server.server_close()