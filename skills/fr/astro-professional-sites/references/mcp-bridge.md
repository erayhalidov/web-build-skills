# Pont Astro MCP — architecture et maintenance

## Le problème

`astro-mcp` est une **intégration Astro**, pas un serveur MCP autonome :
- `package.json` → `"bin": undefined` — pas d'entrée CLI
- Il ne démarre qu'à l'intérieur de `astro dev` sur `http://127.0.0.1:4321/__mcp/sse`
- Il parle **SSE pur** (transport 2024-11-05), pas Streamable HTTP

Le client MCP de Hermes attend du **Streamable HTTP** et ne se connecte pas à `/__mcp/sse`.

## La solution

```
┌─────────────┐   SSE    ┌──────────────┐  Streamable  ┌────────┐
│  astro dev  │ ───────► │ supergateway │ ───────────► │ Hermes │
│  :4321/sse  │          │    :4322     │   HTTP /mcp  │  MCP   │
└─────────────┘          └──────────────┘              └────────┘
```

### Fichiers

| Chemin | Rôle |
|---|---|
| `/root/astro-mcp-bridge/bridge.sh` | Démarre le pont. Crontab `@reboot`. |
| `/root/astro-mcp-bridge/node_modules/supergateway/dist/index.js` | Le pont |
| `/root/astro-test/` | Projet Astro de test (Astro 7.4.4 + astro-mcp 0.4.2) |
| `/tmp/sg-bridge.log` | Log du pont |
| `/tmp/astro-dev.log` | Log du serveur dev |

Config dans `/root/.hermes/config.yaml` :

```yaml
mcp_servers:
  astro:
    url: http://127.0.0.1:4322/mcp
    connect_timeout: 30.0
    enabled: true
```

## La commande du pont

```bash
/usr/local/bin/node /root/astro-mcp-bridge/node_modules/supergateway/dist/index.js \
  --sse http://127.0.0.1:4321/__mcp/sse \
  --outputTransport streamableHttp \
  --port 4322 \
  --host 127.0.0.1 \
  --logLevel info
```

**`--outputTransport streamableHttp` est obligatoire** — sans lui supergateway renvoie du SSE et
Hermes ne se connecte toujours pas.

## Diagnostic

```bash
# 1. Le serveur dev tourne-t-il ?
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4321/

# 2. Le pont tourne-t-il ?
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:4322/mcp \
  -H "content-type: application/json" \
  -H "accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'

# 3. Hermes voit-il le serveur ?
hermes mcp test astro

# 4. Logs
tail -20 /tmp/sg-bridge.log
tail -20 /tmp/astro-dev.log
```

**Important :** le pont est lié à un serveur dev **précis** sur le port 4321. Si tu travailles sur un autre
projet, arrête l'ancien et lance le nouveau sur 4321, ou redémarre le pont avec la nouvelle URL.

## Test manuel du protocole MCP (sans Hermes)

Les réponses arrivent par le **canal SSE**, pas par POST. Le POST ne renvoie que `Accepted`.
Il faut donc lire depuis le flux SSE en parallèle :

```python
# Voir /root/astro-test/probe3.py pour un exemple complet
# Schéma : ouvre GET /__mcp/sse → reçois un endpoint → POST /__mcp/messages?sessionId=...
#          → lis les réponses depuis le flux SSE
```

## Erreurs connues

| Symptôme | Cause | Solution |
|---|---|---|
| `Connection failed (25035ms)` | Hermes attend du Streamable HTTP, reçoit du SSE | Mets supergateway |
| `mcp-remote` reste bloqué sur `Discovering OAuth` | mcp-remote fait une découverte OAuth | N'utilise pas mcp-remote, utilise supergateway |
| `ERR_MODULE_NOT_FOUND` | astro-mcp est ESM (`"type": "module"`) | Démarre avec un node compatible ESM |
| `EBADENGINE node >=22.23.4` | le node par défaut est 22.23.2 | `PATH=/usr/local/bin:$PATH` |
| Les outils `astro` sont muets | le serveur dev est arrêté | Lance `start-dev.sh` |
| Guard : « cannot restart gateway » | le mot `node`/`gateway` dans la commande | `/usr/local/bin/node` ou symlink `sg-bin` |
