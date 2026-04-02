<div align="center">

[![Back](https://img.shields.io/badge/%E2%86%90%20Back-README-C9513A?style=flat-square)](../README.md)
&nbsp;
[![API](https://img.shields.io/badge/Next-API%20Reference-555?style=flat-square)](api.md)

</div>

# Architecture


How ARCANE is put together end to end.

---

## High-level overview

```
Browser (PWA)
    |
    |  HTTPS
    v
┌──────────────────────────────────┐
│   Flask + Gunicorn  (Render)     │
│                                  │
│  ┌─────────────────────────────┐ │
│  │  ProxyFix + CORS + Limiter  │ │
│  └────────────┬────────────────┘ │
│               │                  │
│  ┌────────────▼────────────────┐ │
│  │       /chat  endpoint       │ │
│  │                             │ │
│  │  1. JWT / guest resolution  │ │
│  │  2. Prompt construction     │ │
│  │  3. LLM fallback chain      │ │
│  │  4. Output regex filtering  │ │
│  │  5. Supabase write          │ │
│  └────────────┬────────────────┘ │
└───────────────┼──────────────────┘
                │
     ┌──────────┼──────────────────┐
     │          │                  │
     ▼          ▼                  ▼
  Ollama      Groq             Gemini
 (local)   (Llama 3.3)      (1.5 Flash)
 via Ngrok   + Llama 4       tool calls
             (vision)
                │
                ▼
            Tavily
          Web Search
```

---

## LLM fallback chain

The `/chat` handler tries models in this exact order. **First non-null response wins.**

### Tier 1 — Ollama (local via Ngrok)

- Performs an HTTP GET to `{NGROK_URL}/health` with a 10s timeout before every call
- If health check fails for any reason (timeout, connection refused, non-200), Ollama is silently skipped
- Custom characters (`char_id.startswith('custom_')`) skip Ollama entirely — they have no modelfile
- On success, POSTs to `{NGROK_URL}/chat` with the full message history, toolspec, and optional base64 image
- The tunnel server maps `char_id` → Ollama model name via `tunnel/models.json`
- Auth on the tunnel: `X-API-Key: {BRIDGE_SECRET}` + `ngrok-skip-browser-warning: true`

### Tier 2 — Groq

- Default model: `llama-3.3-70b-versatile`
- If request contains an image: switches to `meta-llama/llama-4-scout-17b-16e-instruct`
- Tool calling is enabled by default (Tavily web search)
- If Groq's tool call validation fails, retries **without tools** and appends a note to the system prompt
- Full multi-tool loop: collects all `tool_calls`, runs each, appends `role: "tool"` messages, requests a second completion

### Tier 3 — Gemini

- Model: `gemini-1.5-flash`
- Uses `FunctionDeclaration` format for tool calling (different schema from OpenAI-compatible)
- If safety filters block the response, returns a graceful string instead of raising
- Vision: injects base64 image as `mime_type` + `data` inline in the last user message

### Failure state

If all three return `None`:

```python
reply = 'Signal lost. All models failed.'
source = "FAIL"
```

The frontend renders this as a character dialogue line, so even total failure feels in-universe.

---

## Prompt construction

Built dynamically on every request. Components in order:

1. **Character base** — personality string from `characters.json` (200–400 words)
2. **Length hint** — derived from `max_tokens`:
   - `< 150` → "Keep your response extremely brief (1-2 sentences max)"
   - `< 300` → "Provide a medium-length response"
   - `>= 300` → "Provide a detailed response"
3. **Time context** — injected only when user message contains time/date keywords AND is under 60 chars. Tools are disabled for that turn. Current time/date is formatted and embedded directly.
4. **Nickname hint** — user's display name preference, e.g. "Call me Ash"
5. **Language hint** — "Respond only in Hindi" style preference
6. **Extra context** — user-supplied free text, max 200 chars, appended raw

For custom characters, all fields come from the request body rather than `characters.json`.

---

## Request lifecycle (full)

```
POST /chat
  |
  ├── get_json(force=True)
  ├── JWT resolution  →  user_id (or 'global' for guests)
  ├── sanitize_input(message, max_len=2000)
  ├── Check char_id in CHAR_MAP  (or custom_character present)
  ├── Build messages[] from history + new message
  ├── Detect time query  →  disable tools if true
  ├── Build system_prompt
  |
  ├── try_ollama()        → reply or None
  ├── if None: chat_groq()  → reply or None
  ├── if None: chat_gemini()  → reply or None
  |
  ├── Regex output filter (function tags, IP logs, brackets)
  ├── Supabase insert (user message + assistant reply)
  └── return jsonify({ response, character, source })
```

---

## Database writes

Two Supabase inserts happen per chat turn:

1. The user message is written **before** LLM inference (so it's already logged even if inference fails)
2. The assistant reply is written **after** successful inference

History retrieval queries the last 50 rows ordered by `id DESC`, then reverses them for chronological display.

---

## Caching strategy (Service Worker)

| Request type | Strategy | Reason |
|---|---|---|
| HTML / navigation | Network-First | Users always get fresh code; cache is fallback |
| Static assets (images, fonts) | Stale-While-Revalidate | Instant load from cache; updates in background |
| API endpoints (`/chat`, `/history`) | Network-Only | Never cache dynamic data |
| Localhost requests | Bypass entirely | No interference in development |

Cache key: `arcane-cache-v6` — bump this string to force all user caches to refresh.

[Back to README](../README.md)
