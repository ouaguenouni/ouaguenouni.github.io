#!/usr/bin/env bash
#
# Local development server for the whole website.
#
#   ./dev.sh          # serve on http://localhost:8000
#   ./dev.sh 9000     # serve on a different port
#
# It does two things:
#   1. Watches articles/ AND presentations/ and rebuilds the HTML when you
#      edit a Markdown file (article.md / slides.md)            (background)
#   2. Serves the site over HTTP so you can just edit + refresh the browser
#
# Workflow: edit a .md  ->  it rebuilds automatically  ->  refresh the browser.
#
# Press Ctrl+C to stop everything.

set -e
cd "$(dirname "$0")"
PORT="${1:-8000}"

if [ ! -x "venv/bin/python" ]; then
  echo "No virtualenv found. Creating one and installing dependencies..."
  python3 -m venv venv
  ./venv/bin/pip install --quiet --upgrade pip
  ./venv/bin/pip install --quiet -r requirements.txt
fi

# Rebuild articles on change (runs in the background).
./venv/bin/python generate.py --watch &
WATCH_PID=$!
trap "kill $WATCH_PID 2>/dev/null" EXIT

echo ""
echo "  ───────────────────────────────────────────────"
echo "   Site            http://localhost:$PORT/"
echo "   Presentations   http://localhost:$PORT/presentations/"
echo "   Live reload ON  — save a file, the browser refreshes itself"
echo "   (Ctrl+C to stop)"
echo "  ───────────────────────────────────────────────"
echo ""

./venv/bin/python serve.py "$PORT"
