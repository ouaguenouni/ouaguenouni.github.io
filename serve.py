#!/usr/bin/env python3
"""Static dev server with live reload.

Serves the site like `python -m http.server`, and additionally:
  - watches the source tree and bumps a version counter whenever a built file
    (.html/.css/.js/.svg/.png/...) changes;
  - injects a tiny polling script into every HTML page that reloads the browser
    as soon as that counter changes.

generate.py --watch still does the Markdown -> HTML compiling; this server just
notices the resulting file change and refreshes the open tab. Run via dev.sh.

    python serve.py [port]      # default 8000
"""

import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

# Only a change to one of these (the *built* outputs) should trigger a reload —
# editing a .md is what makes generate.py rewrite the .html, and THAT is what we
# react to. This avoids reloading before the compile has finished.
RELOAD_SUFFIXES = {'.html', '.css', '.js', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.json'}

_version = 0
_lock = threading.Lock()

LIVERELOAD_SNIPPET = b"""
<script>
(function () {
  let last = null;
  async function poll() {
    try {
      const r = await fetch('/__livereload', { cache: 'no-store' });
      const v = await r.text();
      if (last !== null && v !== last) { location.reload(); return; }
      last = v;
    } catch (e) { /* server busy/restarting; keep trying */ }
    setTimeout(poll, 400);
  }
  poll();
})();
</script>
"""


class ReloadWatcher(FileSystemEventHandler):
    def _bump(self, path):
        p = str(path)
        if '/.git/' in p or '/venv/' in p or p.endswith('~'):
            return
        if Path(p).suffix.lower() not in RELOAD_SUFFIXES:
            return
        global _version
        with _lock:
            _version += 1

    def on_modified(self, event):
        if not event.is_directory:
            self._bump(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self._bump(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._bump(getattr(event, 'dest_path', event.src_path))


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep the console focused on rebuild messages

    def do_GET(self):
        if self.path.split('?', 1)[0] == '/__livereload':
            with _lock:
                body = str(_version).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Inject the reload script into HTML pages (but not into the PDF export).
        raw_path = self.path.split('?', 1)[0]
        target = Path(self.translate_path(self.path))
        if target.is_dir():
            # Redirect /dir -> /dir/ (standard server behaviour). Without this,
            # serving index.html at the slash-less URL leaves the browser base at
            # the PARENT dir, so every relative path (figs/…, iframes) 404s.
            if not raw_path.endswith('/'):
                self.send_response(301)
                self.send_header('Location', raw_path + '/' + self.path[len(raw_path):])
                self.end_headers()
                return
            target = target / 'index.html'
        if target.suffix == '.html' and target.exists() and 'print-pdf' not in self.path:
            html = target.read_bytes()
            if b'</body>' in html:
                html = html.replace(b'</body>', LIVERELOAD_SNIPPET + b'</body>', 1)
            else:
                html += LIVERELOAD_SNIPPET
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        return super().do_GET()


def main():
    observer = Observer()
    watcher = ReloadWatcher()
    observer.schedule(watcher, '.', recursive=False)
    if Path('articles').exists():
        observer.schedule(watcher, 'articles', recursive=True)
    if Path('presentations').exists():
        observer.schedule(watcher, 'presentations', recursive=True)
    observer.start()

    httpd = ThreadingHTTPServer(('', PORT), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()


if __name__ == '__main__':
    main()
