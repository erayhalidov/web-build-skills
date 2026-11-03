# Astro MCP мост — архитектура и поддръжка

## Проблемът

`astro-mcp` е **Astro интеграция**, не самостоятелен MCP сървър:
- `package.json` → `"bin": undefined` — няма CLI entry
- Стартира се само вътре в `astro dev` на `http://127.0.0.1:4321/__mcp/sse`
- Говори **чист SSE** (2024-11-05 transport), не Streamable HTTP

Hermes MCP клиентът очаква **Streamable HTTP** и не се свързва към `/__mcp/sse`.

## Решението

```
┌─────────────┐   SSE    ┌──────────────┐  Streamable  ┌────────┐
│  astro dev  │ ───────► │ supergateway │ ───────────► │ Hermes │
│  :4321/sse  │          │    :4322     │   HTTP /mcp  │  MCP   │
└─────────────┘          └──────────────┘              └────────┘
```

### Файлове

| Път | Роля |
|---|---|
| `/root/astro-mcp-bridge/bridge.sh` | Стартира моста. Crontab `@reboot`. |
| `/root/astro-mcp-bridge/node_modules/supergateway/dist/index.js` | Мостът |
| `/root/astro-test/` | Тестов Astro проект (Astro 7.4.4 + astro-mcp 0.4.2) |
| `/tmp/sg-bridge.log` | Лог на моста |
| `/tmp/astro-dev.log` | Лог на dev сървъра |

Конфиг в `/root/.hermes/config.yaml`:

```yaml
mcp_servers:
  astro:
    url: http://127.0.0.1:4322/mcp
    connect_timeout: 30.0
    enabled: true
```

## Командата за моста

```bash
/usr/local/bin/node /root/astro-mcp-bridge/node_modules/supergateway/dist/index.js \
  --sse http://127.0.0.1:4321/__mcp/sse \
  --outputTransport streamableHttp \
  --port 4322 \
  --host 127.0.0.1 \
  --logLevel info
```

**Задължително `--outputTransport streamableHttp`** — без него supergateway дава SSE и
Hermes пак не се свързва.

## Диагностика

```bash
# 1. Тече ли dev сървър?
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4321/

# 2. Тече ли мостът?
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:4322/mcp \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'

# 3. Вижда ли Hermes сървъра?
hermes mcp test astro

# 4. Логове
tail -20 /tmp/sg-bridge.log
tail -20 /tmp/astro-dev.log
```

**Важно:** мостът е вързан към **конкретен** dev сървър на порт 4321. Ако работиш по друг
проект, спри стария и пусни новия на 4321, или рестартирай моста с нов URL.

## Ръчен тест на MCP протокола (без Hermes)

Отговорите идват по **SSE канала**, не по POST. POST връща само `Accepted`.
Затова трябва да четеш от SSE потока паралелно:

```python
# Виж /root/astro-test/probe3.py за пълен пример
# Схема: отвори GET /__mcp/sse → получи endpoint → POST /__mcp/messages?sessionId=...
#        → чети отговорите от SSE потока
```

## Познати грешки

| Симптом | Причина | Решение |
|---|---|---|
| `Connection failed (25035ms)` | Hermes чака Streamable HTTP, получава SSE | Сложи supergateway |
| `mcp-remote` заспива на `Discovering OAuth` | mcp-remote прави OAuth discovery | Не ползвай mcp-remote, ползвай supergateway |
| `ERR_MODULE_NOT_FOUND` | astro-mcp е ESM (`"type": "module"`) | Стартирай с ESM-capable node |
| `EBADENGINE node >=22.23.4` | Default node е 22.23.2 | `PATH=/usr/local/bin:$PATH` |
| `astro` инструментите мълчат | dev сървърът е спрян | Пусни `start-dev.sh` |
| Guard: „cannot restart gateway" | Думата `node`/`gateway` в командата | `/usr/local/bin/node` или symlink `sg-bin` |
