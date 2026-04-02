<div align="center">

[![Back](https://img.shields.io/badge/%E2%86%90%20Back-README-C9513A?style=flat-square)](../README.md)
&nbsp;
[![API](https://img.shields.io/badge/Also-API%20Reference-555?style=flat-square)](api.md)
&nbsp;
[![Security](https://img.shields.io/badge/Also-Security-555?style=flat-square)](security.md)

</div>

# Setup Guide


Everything you need to run ARCANE locally or deploy it yourself.

---

## What you need (minimum)

- Python 3.9+
- At least one of: `GROQ_API_KEY` or `GEMINI_API_KEY`
- A Supabase project (free tier works fine)

## What you need (for local AI / full stack)

- [Ollama](https://ollama.ai) installed and running
- An [Ngrok](https://ngrok.com) account (free)

---

## Step 1 — Clone

```bash
git clone https://github.com/yashatgitt/Arcane.git
cd Arcane
```

---

## Step 2 — Install dependencies

```bash
cd arcane
pip install -r requirements.txt
```

If you want to isolate it in a virtual environment first:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

---

## Step 3 — Create your .env

```bash
cp .env.example .env
```

Open `.env` and fill in your values. Here's what each one is and where to get it:

```env
# AI APIs — get free keys from the links below
GROQ_API_KEY=        # console.groq.com
GEMINI_API_KEY=      # aistudio.google.com
TAVILY_API_KEY=      # app.tavily.com

# Supabase — create a project at supabase.com
SUPABASE_URL=        # Project Settings > API > Project URL
SUPABASE_KEY=        # Project Settings > API > anon/public key

# Security — generate these, do not share them, do not commit them
BRIDGE_SECRET=       # 64-char hex
JWT_SECRET=          # 64-char hex
SECRET_KEY=          # 48-char hex

# Local Ollama (optional)
NGROK_URL=           # filled in after Step 5, leave blank for now
```

**Generate the secrets:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Run that three times and paste the outputs into `BRIDGE_SECRET`, `JWT_SECRET`, and `SECRET_KEY`.

---

## Step 4 — Set up Supabase tables

Go to your Supabase project → SQL Editor → New query, and run:

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT UNIQUE NOT NULL,
  email TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE messages (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  character TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE suggestions (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT,
  suggestion TEXT,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## Step 5 — Run the app

```bash
cd arcane
python app.py
```

Visit `http://localhost:5001`

That's it. If you have Groq or Gemini keys set, characters will work immediately.

---

## Step 6 (optional) — Local Ollama with tunnel

This lets characters use your own local model instead of the cloud APIs. Much faster responses and no API costs.

**Pull a model in Ollama:**
```bash
ollama pull llama3.1:8b
ollama serve
```

**Start the tunnel:**
```bash
cd tunnel
python run.py
```

Copy the Ngrok URL it prints and paste it into `NGROK_URL` in your `.env`. Restart `app.py`.

---

## Deploying to Render

ARCANE ships with a `Procfile` ready for Render:

```
web: gunicorn app:app
```

1. Push your repo to GitHub
2. Connect to Render → New Web Service
3. Set Root Directory: `arcane`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`
6. Add all environment variables in Render's **Environment** tab
7. Deploy

Render auto-sets the `PORT` variable. The app reads it with `os.getenv('PORT', 5001)`.

**Do not set `NGROK_URL` on Render** unless you have a persistent tunnel running elsewhere. The app handles `NGROK_URL` being empty by simply skipping Ollama.

---

## Troubleshooting

**App crashes on startup:**
Check the error message — it usually says which env variable is missing. The app explicitly raises `ValueError` if `BRIDGE_SECRET`, `JWT_SECRET`, `SECRET_KEY`, `SUPABASE_URL`, or `SUPABASE_KEY` are not set.

**Characters return "Signal lost. All models failed.":**
At least one LLM API key needs to be valid. Check your Groq or Gemini key in `.env`.

**Voice input doesn't work:**
Voice input requires HTTPS or localhost. It won't work on HTTP in production. Render provides HTTPS automatically.

**Mobile back button closes the app:**
This is handled by the two-state `history.pushState` guard in the mobile interface. If it's not working, try reinstalling the PWA from your browser's install prompt.

[Back to README](../README.md)
