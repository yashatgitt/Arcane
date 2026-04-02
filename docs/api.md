<div align="center">

[![Back](https://img.shields.io/badge/%E2%86%90%20Back-README-C9513A?style=flat-square)](../README.md)
&nbsp;
[![Architecture](https://img.shields.io/badge/Also-Architecture-555?style=flat-square)](architecture.md)
&nbsp;
[![Setup](https://img.shields.io/badge/Also-Setup%20Guide-555?style=flat-square)](setup.md)

</div>

# API Reference


All endpoints are served from the Flask backend. Base URL in production: `https://arcane-ai.onrender.com`

---

## Authentication

Most endpoints accept an optional JWT token. Endpoints marked **Auth Required** will return `401` without a valid token.

Send the token in the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

Tokens are issued on `/register` and `/login`. They expire after 30 days.

---

## Endpoints

### POST `/register`

Create a new account.

**Request:**
```json
{
  "username": "ashok",
  "email": "ashok@gmail.com",
  "password": "yourpassword",
  "confirm_password": "yourpassword"
}
```

**Validation rules:**
- Username: 3–32 characters, case-insensitive unique
- Email: must be gmail.com, outlook.com, yahoo.com, icloud.com, or hotmail.com
- Password: minimum 6 characters

**Response `201`:**
```json
{
  "status": "ok",
  "token": "<jwt>",
  "user_id": "<uuid>",
  "username": "ashok",
  "email": "ashok@gmail.com"
}
```

**Errors:**
- `400` — missing fields, password mismatch, invalid email, email domain not allowed
- `409` — username already taken
- `500` — internal error

---

### POST `/login`

Authenticate an existing user.

**Request:**
```json
{
  "username": "ashok",
  "password": "yourpassword"
}
```

**Response `200`:**
```json
{
  "status": "ok",
  "token": "<jwt>",
  "user_id": "<uuid>",
  "username": "ashok",
  "email": "ashok@gmail.com"
}
```

**Errors:**
- `400` — missing fields
- `401` — wrong username or password

---

### POST `/chat`

Send a message to a character. This is the core endpoint.

**Rate limit:** 20 requests per minute per IP.

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <jwt>   (optional — guests can chat)
```

**Request:**
```json
{
  "character": "gojo_satoru",
  "message": "Tell me about your Infinity technique.",
  "history": [
    { "role": "user", "content": "Hey Gojo" },
    { "role": "assistant", "content": "Oh, someone actually daring enough to talk to me. Color me mildly interested." }
  ],
  "max_tokens": 120,
  "nickname_hint": "Call me Ash.",
  "lang_hint": "Respond in English.",
  "extra_context": "We are in the middle of a mission.",
  "image": "<base64_string_optional>",
  "custom_character": null
}
```

**`character` field:** must match an `id` from `/characters`, OR be a string starting with `custom_` when `custom_character` is provided.

**`max_tokens` field:**
- `< 150` → short response (1–2 sentences)
- `150–300` → medium
- `> 300` → detailed

**Custom character shape (when `custom_character` is present):**
```json
{
  "name": "Shadow",
  "universe": "Original",
  "description": "A figure who speaks only in half-truths.",
  "how_they_speak": "Quietly, with unsettling pauses",
  "core_trait": "calculating",
  "never_do": "show weakness or admit uncertainty",
  "catchphrase": "Silence is the loudest answer.",
  "language": "English"
}
```

All custom character fields are optional with safe fallback defaults. Field limits:
- `name`: 50 chars
- `description`: 500 chars
- `how_they_speak` / `never_do`: 200 chars each
- `catchphrase` / `core_trait`: 100 chars each
- `universe` / `language`: 50 chars each

**Response `200`:**
```json
{
  "response": "Infinity... yeah, I'll tell you about it. But only because you asked nicely.",
  "character": "gojo_satoru",
  "source": "groq"
}
```

`source` can be: `"ollama"` | `"groq"` | `"gemini"` | `"FAIL"`

**Errors:**
- `400` — empty or invalid body
- `404` — character not found

---

### GET `/characters`

Returns the full character roster.

No auth required.

**Response `200`:** array of character objects, each with:
```json
{
  "id": "gojo_satoru",
  "name": "Gojo Satoru",
  "anime": "Jujutsu Kaisen",
  "model_name": "gojo_modelfile",
  "personality": "...",
  "image": "assets/avtar/gojo.webp",
  "mal_id": 52819
}
```

---

### GET `/history/<character>`

Get the last 50 messages for the authenticated user and the given character.

**Auth Required.**

`<character>` is a character ID string (e.g. `gojo_satoru`).

**Response `200`:** array ordered oldest → newest:
```json
[
  { "role": "user", "content": "...", "created_at": "2026-04-01T12:00:00Z" },
  { "role": "assistant", "content": "...", "created_at": "2026-04-01T12:00:05Z" }
]
```

---

### POST `/history/<character>`

Save a message directly to history. Used internally by the frontend on history sync.

**Auth Optional.**

**Request:**
```json
{ "role": "assistant", "content": "..." }
```

**Response `200`:** `{ "status": "ok" }`

---

### DELETE `/history/<character>`

Delete message history. **Auth Required.**

`<character>` can be:

| Value | Effect |
|---|---|
| A character ID | Deletes only that character's messages |
| `all` | Deletes all messages for the user |
| `profile_wipe` | Deletes all messages AND the user account |

**Response `200`:** `{ "status": "ok", "deleted_character": "...", "user_id": "..." }`

**Errors:**
- `401` — unauthenticated or guest user tried to delete
- `500` — database error

---

### POST `/suggest`

Submit a feature suggestion. Rate-limited to 5 per minute.

**Request:**
```json
{ "suggestion": "Add voice acting for Levi" }
```

**Response `200`:** `{ "status": "ok" }`

---

## Error format

All errors return JSON:

```json
{ "error": "Human-readable description of what went wrong" }
```

[Back to README](../README.md)
