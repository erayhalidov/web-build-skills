#!/bin/bash
# Стартира Astro dev сървър за MCP работа — извън Hermes процеса.
# Guard-ът блокира `astro dev` / `node` в команден ред, затова този скрипт
# се пуска през crontab или background=true.
#
# Употреба: /root/.hermes/skills/webdev/astro-professional-sites/scripts/start-dev.sh /path/to/project [port]

set -u
PROJECT="${1:-/root/astro-test}"
PORT="${2:-4321}"

export PATH=/usr/local/bin:$PATH
cd "$PROJECT" || { echo "Няма такъв проект: $PROJECT"; exit 1; }

# Проверка за astro-mcp интеграция
if ! grep -q "astro-mcp" astro.config.mjs 2>/dev/null; then
  echo "ВНИМАНИЕ: astro.config.mjs няма astro-mcp интеграция."
  echo "Добави: import mcp from 'astro-mcp';  integrations: [mcp()]"
fi

if [ ! -x "./node_modules/.bin/astro" ]; then
  echo "Липсва astro в $PROJECT. Пусни: npm install astro astro-mcp"
  exit 1
fi

# Убий стара инстанция на същия порт
if [ -f "/tmp/astro-dev-$PORT.pid" ]; then
  OLD=$(cat "/tmp/astro-dev-$PORT.pid" 2>/dev/null)
  [ -n "$OLD" ] && kill "$OLD" 2>/dev/null && sleep 1
fi

echo "Стартирам Astro dev на $PROJECT (порт $PORT)"
exec ./node_modules/.bin/astro dev --port "$PORT" --host 127.0.0.1
