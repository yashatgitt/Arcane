"""
LocalBridge — Advanced Roleplay Chat & Anime Network Engine (A.R.C.A.N.E.)
--------------------------------------------------------------------------
This utility acts as a secure proxy between your local computer and the cloud.
It automates the following processes:
1. Starts the Ollama service locally if not already running.
2. Establishes a secure ngrok tunnel on port 5000.
3. Syncs the live tunnel URL to the main application's environment configuration.
4. Forwards JSON payloads with X-API-Key security validation.
"""

import json
import os
import signal
import subprocess
import sys
import time
import uuid

import re
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from pyngrok import ngrok
from dotenv import load_dotenv

# Load common .env from the root or local
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'arcane', '.env'))
load_dotenv() # Load local too if any

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OLLAMA_HOST = "http://localhost:11434"
FLASK_PORT = 5000
MODELS_FILE = os.path.join(os.path.dirname(__file__), "models.json")
TUNNEL_URL_FILE = os.path.join(os.path.dirname(__file__), "tunnel_url.txt")
# Security Secret - MUST be set via environment variable
BRIDGE_SECRET = os.getenv('BRIDGE_SECRET', '').strip()
if not BRIDGE_SECRET:
    raise ValueError("BRIDGE_SECRET environment variable is required. Generate with: python -c 'import secrets; print(secrets.token_hex(32))'")

# ---------------------------------------------------------------------------
# Load models.json
# ---------------------------------------------------------------------------
def load_models():
    if not os.path.exists(MODELS_FILE):
        print(f"[!] FATAL: models.json not found at {MODELS_FILE}")
        sys.exit(1)
    try:
        with open(MODELS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[!] FATAL: models.json is invalid JSON — {e}")
        sys.exit(1)

MODELS = load_models()

# ---------------------------------------------------------------------------
# Ollama helpers
# ---------------------------------------------------------------------------
ollama_process = None

def ollama_is_running():
    """Check if Ollama is responding on its default port."""
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        return r.status_code == 200
    except requests.Timeout:
        print("[!] Ollama health check timed out")
        return False
    except Exception as e:
        print(f"[!] Ollama health check error: {type(e).__name__}: {e}")
        return False

def start_ollama():
    """Start ollama serve as a background subprocess."""
    global ollama_process
    if ollama_is_running():
        print("[+] Ollama is already running.")
        return
    print("[*] Starting Ollama …")
    ollama_process = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Wait up to 15 s for it to become ready
    for _ in range(30):
        if ollama_is_running():
            print("[+] Ollama is ready.")
            return
        time.sleep(0.5)
    print("[!] Ollama did not start in time — continuing anyway.")

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)
# No CORS needed for internal bridge called via requests (server-to-server)
# CORS(app) 

@app.route("/chat", methods=["POST"])
def chat():
    # Security Check
    api_key = request.headers.get('X-API-Key')
    if api_key != BRIDGE_SECRET:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Empty or invalid request body"}), 400
    character = data.get("character", "")
    user_message = data.get("message", "")
    history = data.get("history", [])

    MODELS = load_models()
    if character not in MODELS:
        return jsonify({"error": f"Character '{character}' not found in models.json"}), 404

    model_name = MODELS[character]["model_name"]

    # Build messages list for Ollama
    if "messages" in data:
        messages = data["messages"]
    else:
        messages = []
        for entry in history:
            m_entry = {"role": entry.get("role", "user"), "content": entry.get("content", "") or ""}
            if "tool_calls" in entry:
                m_entry["tool_calls"] = entry["tool_calls"]
            if "tool_call_id" in entry:
                m_entry["tool_call_id"] = entry["tool_call_id"]
            messages.append(m_entry)
        messages.append({"role": "user", "content": user_message})

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": model_name, 
                "messages": messages, 
                "stream": False,
                "options": {"num_predict": data.get("max_tokens", 250), "temperature": 0.1},
                "tools": data.get("tools")
            },
            timeout=120,
        )
        if resp.status_code == 404:
            return jsonify({"error": f"Model '{model_name}' for character '{character}' not found in Ollama. Please pull it first."}), 404
            
        resp.raise_for_status()
        result = resp.json()
        msg = result.get("message", {})
        content = str(msg.get("content") or "")
        tool_calls = msg.get("tool_calls", [])

        # Robustness: some models include tool calls as text if they fail native tool use
        if data.get("tools") and not tool_calls and "{" in content and "}" in content:
            try:
                # Find JSON-like blocks
                json_blocks = re.findall(r'\{[^{}]+\}', content)
                for block in json_blocks:
                    if '"name":' in block and ('"parameters":' in block or '"arguments":' in block):
                        try:
                            t_data = json.loads(block)
                            t_name = t_data.get("name")
                            t_args = t_data.get("parameters") or t_data.get("arguments")
                            if t_name and t_args:
                                tool_calls.append({
                                    "id": f"call_{uuid.uuid4().hex[:8]}",
                                    "type": "function",
                                    "function": {"name": t_name, "arguments": t_args if isinstance(t_args, (str, dict)) else str(t_args)}
                                })
                                content = content.replace(block, "").strip()
                        except: continue
            except: pass

        for tc in tool_calls:
            if isinstance(tc, dict) and "id" not in tc:
                tc["id"] = f"call_{uuid.uuid4().hex[:8]}"

        return jsonify({
            "response": content,
            "tool_calls": tool_calls,
            "character": character,
        })
    except requests.ConnectionError:
        return jsonify({"error": "Ollama is not reachable."}), 502
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

@app.route("/models", methods=["GET"])
def get_models():
    """Return the list of available characters with metadata."""
    return jsonify(MODELS)

@app.route("/health", methods=["GET"])
def health():
    """Return Ollama status + current ngrok tunnel URL."""
    tunnel_url = ""
    if os.path.exists(TUNNEL_URL_FILE):
        with open(TUNNEL_URL_FILE, "r", encoding="utf-8") as f:
            tunnel_url = f.read().strip()
    return jsonify({
        "ollama": ollama_is_running(),
        "tunnel_url": tunnel_url,
    })

# ---------------------------------------------------------------------------
# Ngrok tunnel
# ---------------------------------------------------------------------------
public_url = None

def update_env_file(url):
    """Update NGROK_URL in the shared .env file if it exists."""
    env_path = os.path.join(os.path.dirname(__file__), '..', 'arcane', '.env')
    if not os.path.exists(env_path):
        return
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        found = False
        with open(env_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.startswith('NGROK_URL='):
                    f.write(f'NGROK_URL={url}\n')
                    found = True
                else:
                    f.write(line)
            if not found:
                f.write(f'\nNGROK_URL={url}\n')
        print(f"[+] Synced tunnel URL to {env_path}")
    except Exception as e:
        print(f"[!] Error updating .env: {e}")

def start_tunnel():
    """Open an ngrok tunnel on FLASK_PORT, save URL to tunnel_url.txt."""
    global public_url
    try:
        existing = ngrok.get_tunnels()
        if existing:
            public_url = existing[0].public_url
            print(f"[+] Reusing existing tunnel: {public_url}")
        else:
            tunnel = ngrok.connect(FLASK_PORT)
            public_url = tunnel.public_url
    except Exception as e:
        print(f"[!] ngrok tunnel error: {type(e).__name__}: {e}")
        public_url = ""
        return

    with open(TUNNEL_URL_FILE, "w", encoding="utf-8") as f:
        f.write(public_url)
    
    update_env_file(public_url)

    border = "+" + "-" * (len(public_url) + 18) + "+"
    print()
    print(border)
    print(f"|  TUNNEL URL:  {public_url}  |")
    print(border)
    print()

# ---------------------------------------------------------------------------
# Graceful shutdown
# ---------------------------------------------------------------------------
def shutdown(sig, frame):
    print("\n[*] Shutting down …")
    ngrok.kill()
    if ollama_process:
        ollama_process.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("  Advanced Roleplay Chat & Anime Network Engine (A.R.C.A.N.E.)")
    print("=" * 50)

    start_ollama()
    start_tunnel()

    print(f"[*] Flask server starting on port {FLASK_PORT} …")
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=False, threaded=True)
