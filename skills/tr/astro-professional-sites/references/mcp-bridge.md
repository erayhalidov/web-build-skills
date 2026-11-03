# Astro MCP köprüsü — mimari ve bakım

## Sorun

`astro-mcp` bir **Astro entegrasyonudur**, bağımsız bir MCP sunucusu değil:
- `package.json` → `"bin": undefined` — CLI girişi yok
- Yalnızca `astro dev` içinde `http://127.0.0.1:4321/__mcp/sse` adresinde başlar
- **Saf SSE** (2024-11-05 transport) konuşur, Streamable HTTP değil

Hermes MCP istemcisi **Streamable HTTP** bekler ve `/__mcp/sse` adresine bağlanmaz.

## Çözüm

```
┌─────────────┐   SSE    ┌──────────────┐  Streamable  ┌────────┐
│  astro dev  │ ───────► │ supergateway │ ───────────► │ Hermes │
│  :4321/sse  │          │    :4322     │   HTTP /mcp  │  MCP   │
└─────────────┘          └──────────────┘              └────────┘
```

### Dosyalar

| Yol | Rol |
|---|---|
| `/root/astro-mcp-bridge/bridge.sh` | Köprüyü başlatır. Crontab `@reboot`. |
| `/root/astro-mcp-bridge/node_modules/supergateway/dist/index.js` | Köprü |
| `/root/astro-test/` | Test Astro projesi (Astro 7.4.4 + astro-mcp 0.4.2) |
| `/tmp/sg-bridge.log` | Köprü günlüğü |
| `/tmp/astro-dev.log` | Dev sunucusu günlüğü |

`/root/.hermes/config.yaml` içindeki yapılandırma:

```yaml
mcp_servers:
  astro:
    url: http://127.0.0.1:4322/mcp
    connect_timeout: 30.0
    enabled: true
```

## Köprü komutu

```bash
/usr/local/bin/node /root/astro-mcp-bridge/node_modules/supergateway/dist/index.js \
  --sse http://127.0.0.1:4321/__mcp/sse \
  --outputTransport streamableHttp \
  --port 4322 \
  --host 127.0.0.1 \
  --logLevel info
```

**`--outputTransport streamableHttp` zorunludur** — o olmadan supergateway SSE verir ve
Hermes yine bağlanmaz.

## Teşhis

```bash
# 1. Dev sunucusu çalışıyor mu?
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4321/

# 2. Köprü çalışıyor mu?
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:4322/mcp \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'

# 3. Hermes sunucuyu görüyor mu?
hermes mcp test astro

# 4. Günlükler
tail -20 /tmp/sg-bridge.log
tail -20 /tmp/astro-dev.log
```

**Önemli:** köprü 4321 portundaki **belirli** bir dev sunucusuna bağlıdır. Başka bir projede
çalışıyorsan eskiyi durdur ve yenisini 4321'de başlat, ya da köprüyü yeni URL ile yeniden başlat.

## MCP protokolünün elle testi (Hermes olmadan)

Yanıtlar POST ile değil **SSE kanalıyla** gelir. POST yalnızca `Accepted` döndürür.
Bu yüzden SSE akışından paralel olarak okuman gerekir:

```python
# Tam örnek için /root/astro-test/probe3.py dosyasına bak
# Şema: GET /__mcp/sse aç → endpoint al → POST /__mcp/messages?sessionId=...
#        → yanıtları SSE akışından oku
```

## Bilinen hatalar

| Belirti | Neden | Çözüm |
|---|---|---|
| `Connection failed (25035ms)` | Hermes Streamable HTTP bekliyor, SSE alıyor | supergateway koy |
| `mcp-remote` `Discovering OAuth` aşamasında uyuyor | mcp-remote OAuth keşfi yapıyor | mcp-remote kullanma, supergateway kullan |
| `ERR_MODULE_NOT_FOUND` | astro-mcp ESM (`"type": "module"`) | ESM destekli node ile başlat |
| `EBADENGINE node >=22.23.4` | Varsayılan node 22.23.2 | `PATH=/usr/local/bin:$PATH` |
| `astro` araçları sessiz | dev sunucusu durmuş | `start-dev.sh` çalıştır |
| Guard: "cannot restart gateway" | Komutta `node`/`gateway` kelimesi | `/usr/local/bin/node` ya da `sg-bin` symlink'i |
