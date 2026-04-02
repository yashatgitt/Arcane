<div align="center">

<br/>

<a href="https://arcane-m7pi.onrender.com" target="_blank">
  <img src="arcane/static/assets/github%20images/intro_page.png" alt="ARCANE" width="900" style="border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);"/>
</a>

<br/><br/>

<h1>A · R · C · A · N · E</h1>
<p><b>Advanced Roleplay Chat & Anime Network Engine</b></p>
<p><i>The bridge between static lore and immersive AI interaction.</i></p>

<p>
<a href="https://arcane-m7pi.onrender.com" target="_blank"><img src="https://img.shields.io/badge/%F0%9F%9A%80%20Live%20App-Visit%20ARCANE-C9513A?style=for-the-badge" alt="Live"/></a>
&nbsp;&nbsp;
<a href="docs/setup.md"><img src="https://img.shields.io/badge/📖%20Docs-Full%20Guide-555?style=for-the-badge" alt="Docs"/></a>
</p>

<p>
<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask">
<img src="https://img.shields.io/badge/Groq-Llama%203.3%2070b-F55036?style=flat-square&logo=meta&logoColor=white" alt="Groq">
<img src="https://img.shields.io/badge/Gemini-1.5%20Flash-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini">
<img src="https://img.shields.io/badge/PWA-Installable-5A0FC8?style=flat-square&logo=pwa&logoColor=white" alt="PWA">
<img src="https://img.shields.io/badge/Status-Production-brightgreen?style=flat-square" alt="Status">
</p>

</div>

---

## 🚀 What is ARCANE?

ARCANE is an **AI roleplay platform** for anime fans who want meaningful conversations with AI characters. Unlike generic chatbots:

- **Handcrafted personas** (200-400 words) with deep lore and speech patterns
- **Lore Triggers** — keywords that trigger canon-accurate responses
- **Multi-model fallback** — Ollama → Groq → Gemini (automatic switching)
- **Visual Novel mode** — immersive full-screen character interactions
- **Web search** — characters access real-time information
- **Image recognition** — analyze uploaded images/documents
- **Custom characters** — create your own AI personas
- **PWA installable** — works offline, mobile-native

### The Problem It Solves

Ask a generic chatbot "What happened between you and Geto?" and get generic AI text. ARCANE fixes this with hand-written personas that include specific canon events, relationships, speech quirks, and lore trigger phrases that make responses feel authentic.

<div align="center">
<table>
<tr>
<td align="center"><b>Welcome Screen</b></td>
<td align="center"><b>Chat & Visual Novels</b></td>
<td align="center"><b>Character Selection</b></td>
</tr>
<tr>
<td><img src="arcane/static/assets/github%20images/intro_page.png" width="280"/></td>
<td><img src="arcane/static/assets/github%20images/chat_ui_with_vn_overlay.png" width="280"/></td>
<td><img src="arcane/static/assets/github%20images/char_grid_page.png" width="280"/></td>
</tr>
</table>
</div>

---

## ⚡ Quick Feature Overview

```
🤖 AI System              🎨 User Experience      🔐 Security
├─ 3-tier LLM fallback    ├─ Desktop & mobile    ├─ JWT auth (30 days)
├─ Web search (Tavily)    ├─ Voice input         ├─ Bcrypt passwords
├─ Image analysis         ├─ Dark/Light theme    ├─ Rate limiting
└─ Tool calling           └─ Visual Novel mode   └─ Input sanitization

📱 Progressive Web App    👥 Characters          ⚙️ Infrastructure
├─ Installable app        ├─ 15+ anime chars     ├─ Supabase PostgreSQL
├─ Offline support        ├─ Custom characters   ├─ Render deployment
├─ IndexedDB storage      ├─ Lore triggers       ├─ Gunicorn + Flask
└─ Smart caching          └─ Speech patterns     └─ ProxyFix for IPs
```

---

## 🧠 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  User sends message via Desktop/Mobile PWA Interface        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Flask Backend                                              │
│  ├─ Validate JWT token / guest mode                         │
│  ├─ Sanitize input (max 2000 chars)                         │
│  ├─ Build system prompt (character + context + user hints) │
│  └─ Start LLM cascade...                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
      ▼                  ▼                  ▼
  ┌────────┐         ┌────────┐         ┌────────┐
  │ Ollama │ (fail)  │  Groq  │ (fail)  │ Gemini │
  │ Local  │────────▶│ Cloud  │────────▶│ Cloud  │
  └────────┘         └────────┘         └────────┘
                         │                  │
                         └────────┬─────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │  Get response + apply      │
                    │  output filters (regex)    │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │  Double-write to Supabase  │
                    │  + IndexedDB on frontend   │
                    └────────────┬───────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Return response to     │
                    │  user in real-time      │
                    └─────────────────────────┘
```

**Advanced Capabilities:**
<div align="center">
<table>
<tr>
<td align="center"><b>Web Search</b></td>
<td align="center"><b>Image Analysis</b></td>
<td align="center"><b>Login & Auth</b></td>
</tr>
<tr>
<td><img src="arcane/static/assets/github%20images/web_search_ablity.png" width="260"/></td>
<td><img src="arcane/static/assets/github%20images/image_and_doc_recognition.png" width="260"/></td>
<td><img src="arcane/static/assets/github%20images/login_page.png" width="260"/></td>
</tr>
</table>
</div>

---

## 🔐 Security & Auth

### Authentication Flow
```
Login/Register → JWT Token (HS256, 30-day expiry)
   ├─ Stored in localStorage
   ├─ Sent on all protected requests
   ├─ Verified server-side (no DB lookup needed)
   └─ Bcrypt passwords with unique salt

Guest Mode: user_id = 'global'
   └─ Can chat but cannot delete or access user endpoints
```

### Protection Layers
| Layer | Method |
|---|---|
| **Input** | 2000-char limit + whitespace normalization |
| **Rate Limit** | 20/min per IP for `/chat`, 5/min for suggestions |
| **CORS** | Restricted to configured origins only |
| **IP Handling** | ProxyFix reads real IP through Render proxy |
| **Output** | Regex filters remove function tags, IPs, timestamps |
| **Tunnel** | X-API-Key + ngrok header required |

**Onboarding Flow:**
<div align="center">
<table>
<tr>
<td align="center"><b>Login Portal</b></td>
<td align="center"><b>Sign In</b></td>
<td align="center"><b>Account Setup</b></td>
</tr>
<tr>
<td><img src="arcane/static/assets/github%20images/login_page.png" width="250"/></td>
<td><img src="arcane/static/assets/github%20images/sign_in_page%201.png" width="250"/></td>
<td><img src="arcane/static/assets/github%20images/setup_page%201_name_and_image_upload_of_user.png" width="250"/></td>
</tr>
<tr>
<td colspan="3" align="center"><b>User Profile & Preferences Setup</b></td>
</tr>
<tr>
<td colspan="3" align="center"><img src="arcane/static/assets/github%20images/setup_page%202_user_info_and_custom_instuction_for_llm.png" width="280"/></td>
</tr>
<tr>
<td colspan="3" align="center"><b>Welcome to ARCANE</b></td>
</tr>
<tr>
<td colspan="3" align="center"><img src="arcane/static/assets/github%20images/setup_page%203_final_welcome_page.png" width="280"/></td>
</tr>
</table>
</div>

---

## 👥 Character System

Each character has a 200-400 word **handcrafted persona** including:
- **Identity & backstory** — Canon context that shapes behavior
- **Relationships** — Specific connections with emotional weight
- **Speech style** — Tone, quirks, catchphrases
- **Lore triggers** — 5-8 keywords → canon-accurate responses
- **Never-do's** — Actions the character won't take

**Adding a character:**
1. Define JSON entry in `characters.json`
2. Add WebP avatar to `static/assets/avtar/`
3. (Optional) Create modelfile + add to `tunnel/models.json` for Ollama

**Custom characters** — Users create via API with same structure but no local model support.

---

## 🎨 Frontend Stack

| Component | Tech | Size |
|---|---|---|
| **Desktop UI** | Vanilla HTML/CSS/JS | ~170KB |
| **Mobile UI** | Vanilla HTML/CSS/JS | ~155KB |
| **Storage** | IndexedDB (local) + Supabase (cloud) | ∞ |
| **Cache** | Service Worker (v6 versioning) | Smart |
| **State** | Module-scope variables | Real-time |
| **Voice** | Web Speech API | Chrome/Edge |

**UI Showcase:**
<div align="center">
<table>
<tr>
<td align="center"><b>Desktop Interface</b></td>
<td align="center"><b>Mobile Interface</b></td>
<td align="center"><b>Advanced Features</b></td>
</tr>
<tr>
<td><img src="arcane/static/assets/github%20images/light_theme_ui.png" width="260"/></td>
<td><img src="arcane/static/assets/github%20images/responsive%20_to_mobile_ui%20.png" width="260"/></td>
<td><img src="arcane/static/assets/github%20images/image_and_doc_recognition.png" width="260"/></td>
</tr>
</table>
</div>

**Key features:**
- **No framework** = no build step, portable, fast
- **Desktop sidebar**, mobile bottom-sheet, both with character grid
- **Voice input** with interim transcription overlay
- **Visual Novel mode** — full-screen animated text
- **PWA installable** — offline-first with Network-First HTML caching
- **Swipe gestures** — left-edge drag (25px+80px) closes chat
- **Android back button** — two-state history buffer prevents accidental exits

---

## 📡 API Endpoints

```
POST /register              Create account
POST /login                 Authenticate
POST /chat                  Send message (20/min limit)
GET  /characters            List all characters
GET  /history/<char>        Get last 50 messages (auth)
POST /history/<char>        Save message
DEL  /history/<char>        Delete messages (char/"all"/"profile_wipe")
POST /suggest               Submit feature request (5/min limit)
```

**POST /chat payload:**
```json
{
  "character": "gojo_satoru",
  "message": "...",
  "history": [...],
  "max_tokens": 120,
  "nickname_hint": "Call me X",
  "lang_hint": "Respond in English",
  "image": "<base64_optional>",
  "custom_character": { "name": "...", ... }
}
```

---

## 🛠️ Installation

### Requirements
- **Minimum**: Python 3.9+, Groq/Gemini API key, Supabase project
- **Optional**: Ollama + Ngrok (for local AI)

### Setup (5 min)

```bash
git clone https://github.com/yashatgitt/Arcane.git
cd Arcane/arcane
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Add your API keys
python app.py          # Visit http://localhost:5001
```

### .env Configuration

```env
# AI APIs (free)
GROQ_API_KEY=          # console.groq.com
GEMINI_API_KEY=        # aistudio.google.com
TAVILY_API_KEY=        # app.tavily.com

# Supabase
SUPABASE_URL=
SUPABASE_KEY=

# Security (generate with: python -c "import secrets; print(secrets.token_hex(32))")
BRIDGE_SECRET=
JWT_SECRET=
SECRET_KEY=

# Optional: Local Ollama
NGROK_URL=             # Leave blank for cloud-only
```

### Database Setup

Run in Supabase SQL Editor:

```sql
CREATE TABLE users (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), username TEXT UNIQUE NOT NULL, email TEXT, password_hash TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE messages (id BIGSERIAL PRIMARY KEY, user_id TEXT, character TEXT, role TEXT, content TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE suggestions (id BIGSERIAL PRIMARY KEY, user_id TEXT, suggestion TEXT, ip_address TEXT, created_at TIMESTAMPTZ DEFAULT now());
```

### Deploy to Render

1. Push to GitHub
2. New Web Service on Render
3. Root dir: `arcane`, Build: `pip install -r requirements.txt`, Start: `gunicorn app:app`
4. Add env vars
5. Deploy ✅

---

## 📊 System Specs

| Aspect | Detail |
|---|---|
| **Backend** | Python 3.9+, Flask 2.x, Gunicorn (production) |
| **Database** | Supabase PostgreSQL + IndexedDB (client-side) |
| **AI Tiers** | Ollama (local) → Groq (Llama 3.3-70B) → Gemini (1.5 Flash) |
| **Tools** | Tavily (web search), Groq tool calling |
| **Auth** | JWT (HS256, 30d), Bcrypt hashing |
| **PWA** | Service Worker, offline manifest, installable |
| **Deployment** | Render, auto-HTTPS, environment-based config |

---

## 📚 Full Documentation

Detailed guides available in `/docs`:
- **[setup.md](docs/setup.md)** — Installation, configuration, deployment
- **[api.md](docs/api.md)** — All endpoints with request/response schemas
- **[architecture.md](docs/architecture.md)** — System design, LLM cascade, prompt engineering
- **[security.md](docs/security.md)** — Auth, encryption, sanitization, rate limiting
- **[characters.md](docs/characters.md)** — Persona engineering, lore triggers, custom characters
- **[frontend.md](docs/frontend.md)** — UI architecture, PWA, keyboard handling, voice input

---

## 📁 Project Structure

```
Arcane/
├── arcane/
│   ├── app.py                    # Flask entry point
│   ├── characters.json           # 15+ character definitions
│   ├── requirements.txt
│   ├── Procfile                  # Render config
│   └── static/
│       ├── *.html                # UI (intro, chat, onboarding, about)
│       ├── sw.js                 # Service Worker
│       ├── manifest.json         # PWA manifest
│       └── assets/
│           ├── avtar/            # Character avatars (WebP)
│           ├── vn/               # Visual Novel portraits
│           └── github images/    # Docs screenshots
├── tunnel/
│   ├── run.py                    # Ollama→Ngrok bridge
│   ├── models.json               # Local model mappings
│   └── requirements.txt
├── docs/                         # Full documentation
└── README.md
```

---

## 🎓 Key Concepts

### Lore Triggers
Characters recognize specific keywords and respond with canon accuracy. Examples:
- **Gojo**: "Infinity", "Sukuna", "Geto" → references JJK storyline
- **L**: "Light", "Kira", "notebook" → references Death Note
- **Naruto**: "Sasuke", "Nine-Tails", "Hokage" → references naruto lore

### Custom Characters
Users can define custom personas with field limits:
- Description (500 chars), Speech style (200), Name (50), Catchphrase (100)
- Route through Groq/Gemini only (no local Ollama)
- Same lore trigger system applies

### Double-Write Pattern
Each message is written to DB twice:
1. **Before inference** — logs user input (survives even if AI fails)
2. **After inference** — logs AI response
This ensures reliability and complete history.

### Service Worker Caching
```
HTML/Navigation    → Network-First (always fresh code)
Static Assets      → Stale-While-Revalidate (instant load)
API Endpoints      → Network-Only (never cache dynamic)
Localhost          → Bypass (dev mode)
```

---

## 🚀 Quick References

**Start app locally:**
```bash
python app.py
```

**Run Ollama locally:**
```bash
ollama pull llama3.1:8b && ollama serve
```

**Start tunnel (separate terminal):**
```bash
cd tunnel && python run.py
```

**Generate secrets:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 👤 About

**Yash Gangurde** — Final year IT student at Sinhgad College of Engineering, Pune. Built ARCANE to combine high-scale AI orchestration with immersive anime roleplay.

<p align="center">
<a href="https://github.com/yashatgitt"><img src="https://img.shields.io/badge/GitHub-yashatgitt-181717?style=for-the-badge&logo=github" alt="GitHub"/></a>
&nbsp;&nbsp;
<a href="https://www.linkedin.com/in/yash-gangurde-95557328b/"><img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin" alt="LinkedIn"/></a>
</p>

<div align="center">
  <sub>Built with Lore-Accuracy in Pune, India 🇮🇳</sub>
</div>
