<div align="center">

<br/>

<a href="https://arcane-m7pi.onrender.com" target="_blank">
  <img src="arcane/static/assets/github%20images/intro_page.png" alt="ARCANE" width="900" style="border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);"/>
</a>

<br/><br/>

<h1>A · R · C · A · N · E</h1>
<p><b>Advanced Roleplay Chat & Anime Network Engine</b></p>
<p><i>The bridge between static lore and meaningful interaction.</i></p>

<p>
<a href="https://arcane-m7pi.onrender.com" target="_blank"><img src="https://img.shields.io/badge/%F0%9F%9A%80%20Live%20App-Visit%20ARCANE-C9513A?style=for-the-badge" alt="Live"/></a>
</p>

<p>
<img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask">
<img src="https://img.shields.io/badge/Gunicorn-Production-499848?style=flat-square&logo=gunicorn&logoColor=white" alt="Gunicorn">
<img src="https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat-square&logo=supabase&logoColor=white" alt="Supabase">
<img src="https://img.shields.io/badge/PWA-Installable-5A0FC8?style=flat-square&logo=pwa&logoColor=white" alt="PWA">
<img src="https://img.shields.io/badge/Render-Deployed-46E3B7?style=flat-square&logo=render&logoColor=white" alt="Render">
</p>

<p>
<img src="https://img.shields.io/badge/Groq-Llama%203.3%2070b-F55036?style=flat-square&logo=meta&logoColor=white" alt="Groq">
<img src="https://img.shields.io/badge/Gemini-1.5%20Flash-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini">
<img src="https://img.shields.io/badge/Ollama-Local%20LLM-grey?style=flat-square" alt="Ollama">
<img src="https://img.shields.io/badge/Tavily-Web%20Search-FF6B35?style=flat-square" alt="Tavily">
<img src="https://img.shields.io/badge/JWT-Auth-000000?style=flat-square&logo=jsonwebtokens&logoColor=white" alt="JWT">
<img src="https://img.shields.io/badge/Status-Production-brightgreen?style=flat-square" alt="Status">
</p>

</div>

---

## 🚀 Core User Experience

ARCANE is an AI roleplay platform built for anime fans who want more than generic responses. Each character has a handcrafted 200–400 word persona that includes deep lore, specific speech patterns, and "Lore Triggers" — keywords that prompt the AI to recall specific canon events truthfully.

<div align="center">
<table>
<tr>
<td align="center"><b>Welcome Screen</b></td>
<td align="center"><b>Chat & Visual Novels</b></td>
<td align="center"><b>Interactive Roster</b></td>
</tr>
<tr>
<td><img src="arcane/static/assets/github%20images/intro_page.png" width="300"/></td>
<td><img src="arcane/static/assets/github%20images/chat_ui_with_vn_overlay.png" width="300"/></td>
<td><img src="arcane/static/assets/github%20images/char_grid_page.png" width="300"/></td>
</tr>
</table>
</div>

---

## 🧠 Intelligence & Architecture

The backend implements a highly resilient three-tier model fallback chain. If a local model or a specific cloud provider is rate-limited or down, the next tier picks up the request instantly.

```text
Message Flow
    |
    ├── TIER 1: Ollama (Local)           [Lowest Latency]
    │           Health Check -> Request -> Tool Loop
    │
    ├── TIER 2: Groq (Llama 3.3 70B)     [Highest Speed Cloud]
    │           Multi-tool Fallback -> Manual Generation Parsing
    │
    └── TIER 3: Gemini 1.5 Flash         [Maximum Reliability]
                Vision Support -> Web Search Integration
```

### Advanced Capabilities

<div align="center">
<table>
<tr>
<td align="center"><b>Web Search Capability</b></td>
<td align="center"><b>Visual Recognition</b></td>
<td align="center"><b>Adaptive Themes</b></td>
</tr>
<tr>
<td><img src="arcane/static/assets/github%20images/web_search_ablity.png" width="300"/></td>
<td><img src="arcane/static/assets/github%20images/image_and_doc_recognition.png" width="300"/></td>
<td><img src="arcane/static/assets/github%20images/light_theme_ui.png" width="300"/></td>
</tr>
</table>
</div>

- **Real-Time Context**: Integrates Tavily Web Search with "Advanced Depth" for the most accurate and up-to-date information.
- **Visual Intelligence**: Full support for image and document upload/recognition via Llama 4 Vision and Gemini 1.5.
- **Roleplay Engine**: Custom-built JS Visual Novel mode for a more immersive storytelling experience.

---

## 🔐 Security & Identity

Every interaction is secured through industry-standard practices, ensuring your chats and profile remain private.

<div align="center">
<table>
<tr>
<td align="center"><b>Portal Entrance</b></td>
<td align="center"><b>Sign In Experience</b></td>
<td align="center"><b>Profile Onboarding</b></td>
</tr>
<tr>
<td><img src="arcane/static/assets/github%20images/login_page.png" width="300"/></td>
<td><img src="arcane/static/assets/github%20images/sign_in_page%201.png" width="300"/></td>
<td><img src="arcane/static/assets/github%20images/setup_page%201.png" width="300"/></td>
</tr>
</table>
</div>

- **Stateless Auth**: JWT-based authentication with 30-day token rotation.
- **Data Protection**: All sensitive user information is hashed using bcrypt before being stored.
- **Stateless History**: Hybrid localStorage + Supabase persistence for maximum performance and cross-device sync.

---

## 🛠️ Tech Stack

<div align="center">
<table>
<tr>
<td><b>Frontend</b></td>
<td>
<img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white" alt="HTML5">
<img src="https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white" alt="CSS3">
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black" alt="JS">
<img src="https://img.shields.io/badge/PWA-5A0FC8?style=flat-square&logo=pwa&logoColor=white" alt="PWA">
</td>
</tr>
<tr>
<td><b>Backend</b></td>
<td>
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask">
<img src="https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white" alt="Gunicorn">
</td>
</tr>
<tr>
<td><b>AI / LLM</b></td>
<td>
<img src="https://img.shields.io/badge/Groq-F55036?style=flat-square&logo=meta&logoColor=white" alt="Groq">
<img src="https://img.shields.io/badge/Gemini-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini">
<img src="https://img.shields.io/badge/Ollama-Local%20LLM-grey?style=flat-square" alt="Ollama">
<img src="https://img.shields.io/badge/Tavily-Web%20Search-FF6B35?style=flat-square" alt="Tavily">
</td>
</tr>
<tr>
<td><b>Data</b></td>
<td>
<img src="https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white" alt="Supabase">
<img src="https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white" alt="JWT">
<img src="https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=white" alt="Render">
</td>
</tr>
</table>
</div>

---

## ⚡ Quick Start

```bash
# Clone and enter directory
git clone https://github.com/yashatgitt/Arcane.git
cd Arcane/arcane

# Install core dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Fill in your GROQ_API_KEY, GEMINI_API_KEY, and SUPABASE credentials

# Run the engine
python app.py
```

### 🛠️ App Setup Journey

As you set up ARCANE for the first time, take advantage of the integrated onboarding flow to customize your experience.

<div align="center">
<table>
<tr>
<td align="center"><b>Step 1: Configuration</b></td>
<td align="center"><b>Step 2: Customization</b></td>
<td align="center"><b>Step 3: Verification</b></td>
</tr>
<tr>
<td><img src="arcane/static/assets/github%20images/setup_page%201.png" width="300"/></td>
<td><img src="arcane/static/assets/github%20images/setup_page%202.png" width="300"/></td>
<td><img src="arcane/static/assets/github%20images/setup_page%203.png" width="300"/></td>
</tr>
</table>
</div>

---

## 📚 Technical Documentation

Explore the project deeply through our modular technical guides:

| Component | Technical Depth |
|---|---|
| [**Architecture**](docs/architecture.md) | Fallback orchestration, prompt engineering, and request lifecycle. |
| [**API Reference**](docs/api.md) | Comprehensive endpoint documentation and authentication schemas. |
| [**Setup Guide**](docs/setup.md) | Environment configuration, Supabase setup, and production deployment. |
| [**Character System**](docs/characters.md) | Persona design philosophy, lore triggers, and prompt construction. |
| [**Security**](docs/security.md) | Auth rotation, rate limiting, and output sanitization protocols. |
| [**Frontend**](docs/frontend.md) | PWA logic, keyboard handling, and Visual Novel engine mechanics. |

---

## 👤 About the Engineer

**Yash Gangurde** — Final Year IT Engineering student at Sinhgad College of Engineering, Pune. Focused on high-scale AI orchestration and immersive digital experiences.

<p align="center">
<a href="https://github.com/yashatgitt" target="_blank"><img src="https://img.shields.io/badge/GitHub-yashatgitt-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/></a>
&nbsp;&nbsp;
<a href="https://www.linkedin.com/in/yash-gangurde-95557328b/" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/></a>
</p>

---

<div align="center">
  <sub>Built with Lore-Accuracy in Pune, India 🇮🇳</sub>
</div>
