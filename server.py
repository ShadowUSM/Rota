#!/usr/bin/env python3
"""ROTA local/static server with token-isolated SQLite sync and optimistic locking.
Run: python3 server.py. For remote access use HTTPS reverse proxy and ROTA_ORIGIN.
No third party Python dependencies. Database lives outside dist/.
"""
import argparse, hashlib, json, os, re, sqlite3, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parent
LOCK = threading.Lock()
MAX_BYTES = 8 * 1024 * 1024
class Handler(BaseHTTPRequestHandler):
    server_version = 'Rota/2.0'
    def log_message(self, fmt, *args):
        # Never include authorization headers or body in logs.
        super().log_message(fmt, *args)
    def origin_ok(self):
        origin = self.headers.get('Origin')
        if not origin: return True
        allowed = {self.server.rota_origin, 'http://' + self.headers.get('Host', '')}
        return origin in allowed
    def send_headers(self, status, content_type='application/json', length=0):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(length))
        self.send_header('Cache-Control', 'no-store' if self.path.startswith('/api/') else 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        origin = self.headers.get('Origin')
        if origin and self.origin_ok():
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Vary', 'Origin')
            self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, If-Match')
            self.send_header('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
        self.end_headers()
    def respond(self, status, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_headers(status, length=len(body)); self.wfile.write(body)
    def room(self):
        if not self.origin_ok():
            self.respond(403, {'error': 'Origin not allowed'}); return None
        auth = self.headers.get('Authorization', '')
        token = auth[7:] if auth.startswith('Bearer ') else ''
        if not re.fullmatch(r'[A-Za-z0-9_-]{32,128}', token):
            self.respond(401, {'error': 'Valid access key required'}); return None
        return hashlib.sha256(token.encode()).hexdigest()
    def do_OPTIONS(self):
        if not self.origin_ok(): return self.respond(403, {'error': 'Origin not allowed'})
        self.send_headers(204)
    def do_GET(self):
        if urlsplit(self.path).path == '/api/sync':
            room = self.room()
            if room is None: return
            with sqlite3.connect(self.server.rota_db) as con:
                row = con.execute('SELECT version, data FROM rooms WHERE room=?', (room,)).fetchone()
            if not row: return self.respond(404, {'version': 0, 'data': None})
            return self.respond(200, {'version': row[0], 'data': json.loads(row[1])})
        path = urlsplit(self.path).path
        # Fixed allowlist prevents serving DB, source, credentials and arbitrary files.
        allowed = {'/': ('index.html', 'text/html; charset=utf-8'), '/index.html': ('index.html', 'text/html; charset=utf-8'),
                   '/sw.js': ('sw.js', 'application/javascript'), '/manifest.webmanifest': ('manifest.webmanifest', 'application/manifest+json'),
                   '/icon-192.png': ('icon-192.png', 'image/png'), '/icon-512.png': ('icon-512.png', 'image/png')}
        if path not in allowed: return self.respond(404, {'error': 'Not found'})
        filename, mime = allowed[path]
        try: body = (ROOT / 'dist' / filename).read_bytes()
        except OSError: return self.respond(404, {'error': 'Build not found'})
        self.send_headers(200, mime, len(body)); self.wfile.write(body)
    def do_PUT(self):
        if urlsplit(self.path).path != '/api/sync': return self.respond(404, {'error': 'Not found'})
        room = self.room()
        if room is None: return
        try: length = int(self.headers.get('Content-Length', '0'))
        except ValueError: return self.respond(400, {'error': 'Invalid content length'})
        if not 0 < length <= MAX_BYTES: return self.respond(413, {'error': 'Maximum 8 MB'})
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json': return self.respond(415, {'error': 'JSON required'})
        try:
            match = int(self.headers.get('If-Match', '-1'))
            obj = json.loads(self.rfile.read(length))
            if not isinstance(obj, dict) or obj.get('schemaVersion') != 2: raise ValueError()
            if not isinstance(obj.get('revision'), str) or len(obj['revision']) > 100: raise ValueError()
            if not isinstance(obj.get('profiles'), list) or not 1 <= len(obj['profiles']) <= 30: raise ValueError()
            if not all(isinstance(p, dict) and isinstance(p.get('base'), dict) for p in obj['profiles']): raise ValueError()
            data = json.dumps(obj, ensure_ascii=False)
        except (ValueError, UnicodeError, TypeError): return self.respond(400, {'error': 'Invalid ROTA backup'})
        with LOCK, sqlite3.connect(self.server.rota_db) as con:
            con.execute('BEGIN IMMEDIATE')
            row = con.execute('SELECT version FROM rooms WHERE room=?', (room,)).fetchone()
            current = row[0] if row else 0
            if match != current: return self.respond(409, {'error': 'Version conflict', 'version': current})
            version = current + 1
            con.execute('INSERT INTO rooms(room,version,data) VALUES(?,?,?) ON CONFLICT(room) DO UPDATE SET version=excluded.version,data=excluded.data', (room, version, data))
        self.respond(200, {'version': version})
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8787)
    parser.add_argument('--db', default=str(ROOT / 'rota-sync.sqlite3'))
    args = parser.parse_args()
    os.umask(0o077)
    with sqlite3.connect(args.db) as con:
        con.execute('PRAGMA journal_mode=WAL')
        con.execute('CREATE TABLE IF NOT EXISTS rooms(room TEXT PRIMARY KEY, version INTEGER NOT NULL, data TEXT NOT NULL)')
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.rota_db = args.db
    server.rota_origin = os.environ.get('ROTA_ORIGIN', f'http://localhost:{args.port}')
    print(f'ROTA: http://{args.host}:{args.port}', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
if __name__ == '__main__': main()
