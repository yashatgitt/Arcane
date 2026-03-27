# A·R·C·A·N·E
## Advanced Roleplay Chat & Anime Network Engine

A premium, character-focused AI roleplay platform built for anime and fiction enthusiasts. Chat with pre-built anime characters or create fully custom original characters. Runs as a Progressive Web App (PWA) with offline support and a dark, immersive aesthetic.

**Created by Yash Gangurde** — Final year IT Engineering Student, Sinhgad College of Engineering, Pune

---

## 🌟 Core Features

- **🎭 Dual Interface** — Separate responsive layouts for Desktop (chat_pc.html) and Mobile (chat_mobile.html)
- **👥 Anime Character Roster** — Pre-loaded characters (Naruto, Gojo, Levi, etc.) with deep personality traits and custom system prompts
- **🎨 Custom Character Builder** — Create and inject your own original characters with isolated context
- **📏 Token Length Control** — User-facing toggle for response length — Short / Medium / Long
- **🔒 Incognito Mode** — Isolated session buffers preventing history bleeding across characters
- **📱 Offline Support** — Service Worker (sw.js) handles caching and network fallback gracefully
- **🔍 Web Search Integration** — Dynamically triggered Tavily searches inside Groq tool-call pipeline

---

## 🏗️ Backend Architecture

**Three-tier LLM Fallback Chain:**
1. **🏠 Local Ollama** — Primary inference, exposed via Ngrok tunnel
2. **⚡ Groq (Llama-3.3-70b)** — Fast cloud fallback with native tool-call support
3. **🛡️ Gemini (gemini-1.5-flash)** — Final reliability backup

**Security Layers:**
- Rate limiting: 20 requests/minute via Flask-Limiter
- Strict CORS policy (no wildcard origins)
- REGEX filters preventing terminal stdout leaking into responses

---

## 🌐 Tunnel Layer (LocalBridge)

**Problem Solved:** Local Ollama can't be directly accessed by cloud/external clients

**Solution:** `run.py` + `models.json` setup a secure Ngrok mesh tunnel exposing local Ollama endpoint to Flask backend. Handles JSON payload forwarding and local function trigger translation on the fly.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama (for local AI characters)
- API keys for Groq & Gemini (free tiers available)

### Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/yashatgitt/Arcane.git
   cd one-last-hope
   ```

2. **Install Dependencies**
   ```bash
   cd arcane
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start Ollama (Local AI)**
   ```bash
   ollama serve
   ```

5. **Setup Tunnel (New Terminal)**
   ```bash
   cd tunnel
   python run.py
   ```

6. **Run Main Application**
   ```bash
   cd arcane
   python app.py
   ```

7. **Open Browser**
   - Visit: http://localhost:5001
   - Install as PWA for offline support

---

## 🎮 Usage Examples

### Chat with Pre-built Character
```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Gojo",
    "message": "What are your thoughts on curses?",
    "token_length": "medium"
  }'
```

### Create Custom Character
```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "character": "custom_1",
    "message": "Tell me about yourself",
    "custom_character": {
      "name": "Shadow Hunter",
      "description": "A mysterious assassin from the underworld",
      "personality": "Cold, calculating, and deadly precise",
      "speaking_style": "Whispers with a hint of danger"
    }
  }'
```

### Enable Incognito Mode
```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Naruto",
    "message": "Secret conversation",
    "incognito": true
  }'
```

---

## 📁 Project Structure

`
one last hope/
├── arcane/                 # Main application
│   ├── app.py             # Flask backend with LLM orchestration
│   ├── characters.json    # Anime character definitions & prompts
│   ├── requirements.txt   # Python dependencies
│   ├── .env.example       # Environment variables template
│   └── static/            # Frontend PWA files
│       ├── intro.html     # Landing page
│       ├── chat_pc.html   # Desktop roleplay interface
│       ├── chat_mobile.html # Mobile roleplay interface
│       ├── sw.js          # Service worker for offline
│       ├── manifest.json  # PWA manifest
│       └── assets/        # Images, fonts, UI assets
│
└── tunnel/                # Ollama tunnel bridge
    ├── run.py            # Ngrok tunnel server
    ├── models.json       # Model mappings & configurations
    └── requirements.txt  # Tunnel dependencies
`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML, CSS, JS (PWA, Service Worker) |
| **Backend** | Python Flask |
| **Primary LLM** | Ollama (local, via Ngrok tunnel) |
| **Cloud LLM 1** | Groq — Llama-3.3-70b |
| **Cloud LLM 2** | Gemini 1.5 Flash |
| **Web Search** | Tavily API |
| **Tunneling** | Ngrok |
| **Character Config** | characters.json |

---

## 🎭 Character System

Characters are defined in characters.json with custom-tuned Ollama modelfiles:

**Custom Model Tuning:**
- Each character has a dedicated Ollama modelfile (e.g., `naruto_modelfile`, `gojo_modelfile`)
- Modelfiles are created using custom Ollama Modelfile format for enhanced roleplay depth
- Base model: llama3.1:8b with character-specific fine-tuning
- Model mappings defined in `tunnel/models.json`

**Personality Traits:**
- Deep psychological profiles with anime-specific lore
- Unique dialogue styles and catchphrases
- Custom system prompts per character
- Enhanced roleplay through model fine-tuning

**Pre-loaded Characters:**
- **Gojo Satoru** — The strongest sorcerer, cocky and powerful
- **Levi Ackerman** — Humanity's strongest soldier, stern and disciplined
- **Naruto Uzumaki** — Determined ninja with unwavering spirit
- **L Lawliet** — World's greatest detective, analytical and unsettling
- **Light Yagami** — Genius student turned Kira, charming yet ruthless
- **And more...** (expandable roster)

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Landing page |
| POST | `/chat` | AI roleplay chat (supports custom_character field) |
| GET | `/characters` | List available characters |
| GET | `/history/<char>` | Get character chat history |
| POST | `/register` | User registration |
| POST | `/login` | User authentication |

---

## 🎨 Design Philosophy

**Dark-mode first, immersive UI.** Built for roleplay depth — not just chatting, but *being in the world* of the character. Each character has a full personality pipeline, creating authentic, memorable interactions that feel like stepping into your favorite anime.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-character)
3. Add new characters to characters.json
4. Test roleplay interactions thoroughly
5. Submit a pull request

---

## 📄 License

Created for educational and entertainment purposes. Built with passion for anime and AI.

---

## 🙋‍♂️ About the Creator

**Yash Gangurde**
- Final year IT Engineering Student
- Sinhgad College of Engineering, Pune
- Passionate about AI, anime, and immersive storytelling

**Contact:** Open to collaborations and character suggestions!

---

## 🎯 Future Enhancements

- [ ] Voice acting integration for characters
- [ ] Multi-character group conversations
- [ ] Advanced personality customization UI
- [ ] Character memory persistence across sessions
- [ ] Mobile app versions (React Native)
- [ ] Custom model training for ultra-realistic roleplay

---

**"Step into the world of anime. Let the characters come alive."**
