# Astro MCP bridge — architecture and maintenance

## The problem

`astro-mcp` is an **Astro integration**, not a standalone MCP server:
- `package.json` → `"bin": undefined` — no CLI entry
- It only starts inside `astro dev` at `http://127.0.0.1:4321/__mcp/sse`
- It speaks **plain SSE** (2024-11-05 transport), not Streamable HTTP

The Hermes MCP client expects **Streamable HTTP** and does not connect to `/__mcp/sse`.

## The solution

```
┌─────────────┐   SSE    ┌──────────────┐  Streamable  ┌────────┐
│  astro dev  │ ───────► │ supergateway │ ───────────► │ Hermes │
│  :4321/sse  │          │    :4322     │   HTTP /mcp  │  MCP   │
└─────────────┘          └──────────────┘              └────────┘
```

### Files

| Path | Role |
|---|---|
| `/root/astro-mcp-bridge/bridge.sh` | Starts the bridge. Crontab `@reboot`. |
| `/root/astro-mcp-bridge/node_modules/supergateway/dist/index.js` | The bridge |
| `/root/astro-test/` | Test Astro project (Astro 7.4.4 + astro-mcp 0.4.2) |
| `/tmp/sg-bridge.log` | Bridge log |
| `/tmp/astro-dev.log` | Dev server log |

Config in `/root/.hermes/config.yaml`:

```yaml
mcp_servers:
  astro:
    url: http://127.0.0.1:4322/mcp
    connect_timeout: 30.0
    enabled: true
```

## The bridge command

```bash
/usr/local/bin/node /root/astro-mcp-bridge/node_modules/supergateway/dist/index.js \
  --sse http://127.0.0.1:4321/__mcp/sse \
  --outputTransport streamableHttp \
  --port 4322 \
  --host 127.0.0.1 \
  --logLevel info
```

**`--outputTransport streamableHttp` is mandatory** — without it supergateway serves SSE and
Hermes still will not connect.

## Diagnostics

```bash
# 1. Is the dev server running?
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4321/

# 2. Is the bridge running?
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:4322/mcp \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'

# 3. Does Hermes see the server?
hermes mcp test astro

# 4. Logs
tail -20 /tmp/sg-bridge.log
tail -20 /tmp/astro-dev.log
```

**Important:** the bridge is tied to a **specific** dev server on port 4321. If you work on another
project, stop the old one and start the new one on 4321, or restart the bridge with the new URL.

## Manual test of the MCP protocol (without Hermes)

Responses come over the **SSE channel**, not over POST. The POST only returns `Accepted`.
That is why you have to read from the SSE stream in parallel:

```python
# See /root/astro-test/probe3.py for a complete example
# Scheme: open GET /__mcp/sse → get endpoint → POST /__mcp/messages?sessionId=...
#         → read the responses from the SSE stream
```

## Known errors

| Symptom | Cause | Fix |
|---|---|---|
| `Connection failed (25035ms)` | Hermes waits for Streamable HTTP, gets SSE | Install supergateway |
| `mcp-remote` hangs on `Discovering OAuth` | mcp-remote does OAuth discovery | Don't use mcp-remote, use supergateway |
| `ERR_MODULE_NOT_FOUND` | astro-mcp is ESM (`"type": "module"`) | Start with an ESM-capable node |
| `EBADENGINE node >=22.23.4` | Default node is 22.23.2 | `PATH=/usr/local/bin:$PATH` |
| The `astro` tools are silent | The dev server is stopped | Run `start-dev.sh` |
| Guard: "cannot restart gateway" | The word `node`/`gateway` in the command | `/usr/local/bin/node` or the symlink `sg-bin` |
