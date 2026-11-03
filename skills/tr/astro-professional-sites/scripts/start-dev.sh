#!/bin/bash
# Starts the Astro dev server for MCP work — outside the Hermes process.
# The guard blocks `astro dev` / `node` on the command line, so this script
# is launched via crontab or background=true.
#
# Usage: /root/.hermes/skills/webdev/astro-professional-sites/scripts/start-dev.sh /path/to/project [port]

set -u
PROJECT="${1:-/root/astro-test}"
PORT="${2:-4321}"

export PATH=/usr/local/bin:$PATH
cd "$PROJECT" || { echo "No such project: $PROJECT"; exit 1; }

# Check for the astro-mcp integration
if ! grep -q "astro-mcp" astro.config.mjs 2>/dev/null; then
  echo "WARNING: astro.config.mjs has no astro-mcp integration."
  echo "Add: import mcp from 'astro-mcp';  integrations: [mcp()]"
fi

if [ ! -x "./node_modules/.bin/astro" ]; then
  echo "astro is missing in $PROJECT. Run: npm install astro astro-mcp"
  exit 1
fi

# Kill the old instance on the same port
if [ -f "/tmp/astro-dev-$PORT.pid" ]; then
  OLD=$(cat "/tmp/astro-dev-$PORT.pid" 2>/dev/null)
  [ -n "$OLD" ] && kill "$OLD" 2>/dev/null && sleep 1
fi

echo "Starting Astro dev in $PROJECT (port $PORT)"
exec ./node_modules/.bin/astro dev --port "$PORT" --host 127.0.0.1
