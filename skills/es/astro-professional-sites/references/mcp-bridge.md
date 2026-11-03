# Puente Astro MCP — arquitectura y mantenimiento

## El problema

`astro-mcp` es una **integración de Astro**, no un servidor MCP independiente:
- `package.json` → `"bin": undefined` — no hay entrada CLI
- Solo arranca dentro de `astro dev` en `http://127.0.0.1:4321/__mcp/sse`
- Habla **SSE puro** (transporte 2024-11-05), no Streamable HTTP

El cliente MCP de Hermes espera **Streamable HTTP** y no se conecta a `/__mcp/sse`.

## La solución

```
┌─────────────┐   SSE    ┌──────────────┐  Streamable  ┌────────┐
│  astro dev  │ ───────► │ supergateway │ ───────────► │ Hermes │
│  :4321/sse  │          │    :4322     │   HTTP /mcp  │  MCP   │
└─────────────┘          └──────────────┘              └────────┘
```

### Archivos

| Ruta | Rol |
|---|---|
| `/root/astro-mcp-bridge/bridge.sh` | Arranca el puente. Crontab `@reboot`. |
| `/root/astro-mcp-bridge/node_modules/supergateway/dist/index.js` | El puente |
| `/root/astro-test/` | Proyecto Astro de prueba (Astro 7.4.4 + astro-mcp 0.4.2) |
| `/tmp/sg-bridge.log` | Log del puente |
| `/tmp/astro-dev.log` | Log del servidor dev |

Config en `/root/.hermes/config.yaml`:

```yaml
mcp_servers:
  astro:
    url: http://127.0.0.1:4322/mcp
    connect_timeout: 30.0
    enabled: true
```

## El comando del puente

```bash
/usr/local/bin/node /root/astro-mcp-bridge/node_modules/supergateway/dist/index.js \
  --sse http://127.0.0.1:4321/__mcp/sse \
  --outputTransport streamableHttp \
  --port 4322 \
  --host 127.0.0.1 \
  --logLevel info
```

**Obligatorio `--outputTransport streamableHttp`** — sin ello supergateway sirve SSE y
Hermes tampoco se conecta.

## Diagnóstico

```bash
# 1. ¿Está corriendo el servidor dev?
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4321/

# 2. ¿Está corriendo el puente?
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:4322/mcp \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'

# 3. ¿Ve Hermes el servidor?
hermes mcp test astro

# 4. Logs
tail -20 /tmp/sg-bridge.log
tail -20 /tmp/astro-dev.log
```

**Importante:** el puente está atado a **un** servidor dev concreto en el puerto 4321. Si trabajas en otro
proyecto, para el antiguo y lanza el nuevo en 4321, o reinicia el puente con la nueva URL.

## Prueba manual del protocolo MCP (sin Hermes)

Las respuestas llegan por el **canal SSE**, no por POST. El POST solo devuelve `Accepted`.
Por eso hay que leer del stream SSE en paralelo:

```python
# Ver /root/astro-test/probe3.py para un ejemplo completo
# Esquema: abre GET /__mcp/sse → recibe endpoint → POST /__mcp/messages?sessionId=...
#          → lee las respuestas del stream SSE
```

## Errores conocidos

| Síntoma | Causa | Solución |
|---|---|---|
| `Connection failed (25035ms)` | Hermes espera Streamable HTTP, recibe SSE | Pon supergateway |
| `mcp-remote` se queda en `Discovering OAuth` | mcp-remote hace OAuth discovery | No uses mcp-remote, usa supergateway |
| `ERR_MODULE_NOT_FOUND` | astro-mcp es ESM (`"type": "module"`) | Arranca con un node compatible con ESM |
| `EBADENGINE node >=22.23.4` | El node por defecto es 22.23.2 | `PATH=/usr/local/bin:$PATH` |
| Las herramientas `astro` están mudas | El servidor dev está parado | Lanza `start-dev.sh` |
| Guard: "cannot restart gateway" | La palabra `node`/`gateway` en el comando | `/usr/local/bin/node` o un symlink `sg-bin` |
