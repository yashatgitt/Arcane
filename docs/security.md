<div align="center">

[![Back](https://img.shields.io/badge/%E2%86%90%20Back-README-C9513A?style=flat-square)](../README.md)
&nbsp;
[![Setup](https://img.shields.io/badge/Also-Setup%20Guide-555?style=flat-square)](setup.md)
&nbsp;
[![API](https://img.shields.io/badge/Also-API%20Reference-555?style=flat-square)](api.md)

</div>

# Security


How ARCANE handles authentication, data protection, and abuse prevention in production.

---

## Authentication

ARCANE uses stateless JWT authentication. No server-side sessions.

### Token lifecycle

1. User registers or logs in → server issues a JWT signed with `JWT_SECRET` (HS256)
2. Token is stored in `localStorage` in the browser
3. Sent on every protected request in `Authorization: Bearer <token>`
4. Token expires after 30 days
5. Server verifies signature and expiry on every request — no database lookup needed

### Token payload

```json
{
  "user_id": "<uuid>",
  "username": "ashok",
  "iat": 1712000000,
  "exp": 1714592000
}
```

### Password storage

Passwords are never stored. Only bcrypt hashes:

```python
bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
```

Each hash includes a unique salt — two users with the same password have different hashes.

### Guest users

Unauthenticated users can still chat. They are assigned the identity `'global'` and their messages are stored in Supabase under that ID. This is intentional — the barrier to try the app is zero.

Guest users cannot delete history or accounts. Those endpoints return `401`.

---

## Rate limiting

Implemented via Flask-Limiter with memory-backed storage.

| Endpoint | Limit |
|---|---|
| `/chat` | 20 requests per minute per IP |
| `/suggest` | 5 requests per minute per IP |
| Global default | 60 requests per minute per IP |

The memory backend means counters reset on process restart. On Render's free tier, this is acceptable. For stricter enforcement under high traffic, swap to a Redis backend:

```python
storage_uri="redis://your-redis-url"
```

---

## CORS

Configured via `Flask-CORS`. No wildcard origins in production.

Allowed origins are set via the `CORS_ORIGINS` environment variable as a comma-separated list:

```env
CORS_ORIGINS=https://arcane-ai.onrender.com,https://yourdomain.com
```

If `CORS_ORIGINS` is empty, defaults to `localhost:5000` and `127.0.0.1:5000` only.

Allowed methods: `GET`, `POST`, `DELETE`, `OPTIONS`
Allowed headers: `Content-Type`, `X-User-ID`, `Authorization`

---

## Input sanitization

All user-supplied strings go through `sanitize_input()` before touching any system prompt:

1. Empty/falsy → return empty string
2. Non-string → cast to string
3. Strip leading/trailing whitespace
4. Truncate to `max_len` (2000 chars for messages, 200 for extra context, 80 for hints)

This prevents prompt injection via oversized or malformed inputs, and keeps token budgets predictable.

---

## Output filtering

LLM responses — especially from local Ollama models — can sometimes leak internal processing artifacts into the text. The output is regex-cleaned before being returned to the client:

```python
# Strip leaked function/tool call XML tags
re.sub(r'<function=[^>]+>.*?</function>', '', reply, flags=re.DOTALL)
re.sub(r'<tool_call>.*?</tool_call>', '', reply, flags=re.DOTALL)

# Strip server log artifacts (IP addresses, access log lines)
re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*?HTTP/\d\.\d["\s]+\d+\s*-?', '', reply)

# Strip timestamp brackets from logs
re.sub(r'\[\d{2}/\w+/\d{4}[^\]]*\]', '', reply)

# Normalize whitespace
re.sub(r'\n{3,}', '\n\n', reply).strip()
```

---

## Tunnel authentication

The LocalBridge tunnel (`tunnel/run.py`) requires every request from Flask to include:

```
X-API-Key: <BRIDGE_SECRET>
ngrok-skip-browser-warning: true
```

If the key is missing or wrong, the tunnel server rejects the request. `BRIDGE_SECRET` is shared between Flask and the tunnel server via environment variables — it never appears in the codebase.

---

## Proxy configuration

ARCANE runs behind Render's reverse proxy in production. Without `ProxyFix`, rate limiting reads the *proxy IP* instead of the real client IP, making limits trivially bypassable.

```python
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
```

This tells Flask to trust exactly one hop of the `X-Forwarded-For` chain.

---

## What's not here

**No email verification** — registration accepts email for record-keeping only. Email domain is restricted to major providers (gmail, outlook, yahoo, icloud, hotmail) to prevent obviously fake addresses.

**No refresh tokens** — tokens are long-lived (30 days). Refresh token rotation was not implemented for this version.

**No 2FA** — out of scope for the current release.

[Back to README](../README.md)
