"""
Advanced Roleplay Chat & Anime Network Engine (A.R.C.A.N.E.) — Flask Backend
-----------------------------------------------------------------------------
This is the core orchestration layer that manages user authentication (JWT),
character personas, and message routing through a three-tier LLM fallback chain:
1. Local Ollama (via Ngrok) -> 2. Groq (Llama 3.3) -> 3. Gemini 1.5 Flash.
It also handles real-time web search integration via Tavily.
"""

import json
import os
from datetime import datetime, timedelta, timezone
import traceback
import re
from functools import wraps

import requests
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request, send_from_directory, session
import uuid
import secrets
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import threading
import time
import bcrypt
import jwt
from supabase import create_client, Client

from tavily import TavilyClient
from groq import Groq
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()

NGROK_URL     = os.getenv('NGROK_URL', '').strip()
GROQ_API_KEY  = os.getenv('GROQ_API_KEY', '').strip()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '').strip()
BRIDGE_SECRET  = os.getenv('BRIDGE_SECRET', '').strip()
if not BRIDGE_SECRET:
    raise ValueError("BRIDGE_SECRET environment variable is required. Generate with: python -c 'import secrets; print(secrets.token_hex(32))'")
JWT_SECRET     = os.getenv('JWT_SECRET', '').strip()
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is required. Generate with: python -c 'import secrets; print(secrets.token_hex(32))'")
JWT_EXPIRY     = 30 * 24 * 60 * 60  # 30 days

# Supabase Configuration
SUPABASE_URL   = os.getenv('SUPABASE_URL', '').strip()
SUPABASE_KEY   = os.getenv('SUPABASE_KEY', '').strip()
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
CHARACTERS_FILE = os.path.join(BASE_DIR, 'characters.json')
STATIC_DIR     = os.path.join(BASE_DIR, 'static')

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Clients
tavily = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------------------------
# Load characters
# ---------------------------------------------------------------------------
with open(CHARACTERS_FILE, 'r', encoding='utf-8') as _f:
    CHARACTERS = json.load(_f)

# Build a lookup dict  { id: character_obj }
CHAR_MAP = {ch['id']: ch for ch in CHARACTERS}

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')
SECRET_KEY_VAL = os.getenv('SECRET_KEY', '').strip()
if not SECRET_KEY_VAL:
    raise ValueError("SECRET_KEY environment variable is required. Generate with: python -c 'import secrets; print(secrets.token_hex(24))'")
app.secret_key = SECRET_KEY_VAL
limiter = Limiter(get_remote_address, app=app, default_limits=["60 per minute"], storage_uri="memory://")

# --- CORS Configuration ---
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
# filter out empty strings
origins = [o.strip() for o in CORS_ORIGINS if o.strip()]
if not origins:
    origins = ["http://localhost:5000", "http://127.0.0.1:5000"]
# add ngrok if present
if NGROK_URL and NGROK_URL not in origins:
    origins.append(NGROK_URL)

CORS(app, origins=origins, methods=['GET', 'POST', 'DELETE', 'OPTIONS'], allow_headers=['Content-Type', 'X-User-ID'])

# ---------------------------------------------------------------------------
# Supabase Database Helpers
# ---------------------------------------------------------------------------
def get_db():
    """Returns the Supabase client."""
    return supabase

@app.before_request
def init_supabase_tables():
    """
    Supabase tables must be created manually via the SQL editor.
    This is just a placeholder for consistency with the Flask pattern.
    """
    pass

@app.teardown_appcontext
def close_db(exc):
    """
    No cleanup needed for Supabase client.
    Keeping this for consistency with Flask patterns.
    """
    pass

# ---------------------------------------------------------------------------
# Input Sanitization
# ---------------------------------------------------------------------------
def sanitize_input(text, max_len=2000):
    """Basic server-side sanitization and length limiting."""
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)
    
    # 1. Strip leading/trailing whitespaces
    text = text.strip()
    
    # 2. Enforce length limit
    text = text[:max_len]
    
    # 3. Escape minimal HTML if text is for generic context (optional for JSON)
    # but we will just ensure it doesn't break our structure
    return text

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, password_hash):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_jwt_token(user_id, username):
    """Create a JWT token for a user."""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=JWT_EXPIRY),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token):
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_from_request():
    """Extract JWT token from Authorization header or X-Auth-Token header."""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return request.headers.get('X-Auth-Token')

def get_user_id_from_request(data_dict=None):
    """
    Extract user_id from JWT token, X-User-ID header, or request data.
    Falls back to 'global' for guest users. Simple and permissive.
    """
    # Try JWT token first
    token = get_token_from_request()
    if token:
        payload = verify_jwt_token(token)
        if payload:
            return str(payload.get('user_id'))
    
    # Try header
    user_id = request.headers.get('X-User-ID')
    if user_id:
        return user_id
    
    # Try request data
    if data_dict and isinstance(data_dict, dict):
        user_id = data_dict.get('user_id')
        if user_id:
            return str(user_id)
    
    # Default guest
    return 'global'

# ---------------------------------------------------------------------------
# Tool Calling Setup
# ---------------------------------------------------------------------------
def web_search(query):
    if not tavily:
        return "Web search is disabled. No Tavily API key."
    try:
        result = tavily.search(query=query, max_results=3)
        answer = result.get("answer") or ""
        snippets = [r["content"] for r in result.get("results", [])[:2]]
        if not answer and not snippets:
             return "No search results found."
        return str(answer) + "\n" + "\n".join(snippets)
    except Exception as e:
        return f"Error executing web search: {str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current real-time information, news, scores, weather, recent events",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

gemini_tools = Tool(function_declarations=[
    FunctionDeclaration(
        name="web_search",
        description="Search the web for real-time information",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    )
])

def run_tool(name, args):
    if name == "web_search":
        return web_search(args.get("query", ""))
    return "Tool not found"

# ---------------------------------------------------------------------------
# Fallback chain
# ---------------------------------------------------------------------------
def try_ollama(character, messages, tools=None, max_tokens=250, image_b64=None):
    """Try the local Ollama model via ngrok tunnel with optional tools."""
    if not NGROK_URL:
        return None
        
    try:
        headers = {
            'ngrok-skip-browser-warning': 'true',
            'X-API-Key': BRIDGE_SECRET
        }
        health_resp = requests.get(f"{NGROK_URL.rstrip('/')}/health", headers=headers, timeout=10)
        if health_resp.status_code != 200:
            print(f"[!] Ollama health check failed with status {health_resp.status_code}")
            return None
    except requests.Timeout:
        print("[!] Ollama health check timed out")
        return None
    except requests.ConnectionError:
        print("[!] Ollama health check: Connection refused (Ollama or tunnel might be down)")
        return None
    except Exception as e:
        print(f"[!] Ollama health check error: {type(e).__name__}: {e}")
        return None

    try:
        resp = requests.post(
            f"{NGROK_URL.rstrip('/')}/chat",
            json={
                'character': character, 
                'message': messages[-1]['content'], 
                'image': image_b64,
                'history': messages[:-1],
                'messages': messages,  # Pass the full list so full tool-followup roles carry over!
                'tools': tools,
                'max_tokens': max_tokens
            },
            headers=headers,
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "content": data.get('response'),
                "tool_calls": data.get('tool_calls', [])
            }
        elif resp.status_code == 404:
            data = resp.json()
            return {"error_msg": data.get('error', 'Ollama model missing.')}
    except requests.Timeout:
        print(f"[!] Ollama chat request timed out for character: {character}")
    except Exception as e:
        print(f"[!] Ollama connection/parse exception: {type(e).__name__}: {e}")
    return None


def chat_groq(messages, system_prompt, max_tokens=120, image_b64=None):
    """Groq API using official SDK + Tool Calling"""
    if not groq_client:
        print("[!] Groq client not initialized (missing API key)")
        return None
    
    try:
        model_name = "llama-3.3-70b-versatile"
        kwargs = {"max_tokens": max_tokens}
        msgs = [{"role": "system", "content": system_prompt}] + messages
        
        if image_b64:
            model_name = "meta-llama/llama-4-scout-17b-16e-instruct"
            # Modify the last user message to include the image
            for i in range(len(msgs)-1, -1, -1):
                if msgs[i]['role'] == 'user':
                    msgs[i]['content'] = [
                        {"type": "image_url", "image_url": {"url": image_b64 if image_b64.startswith("data:") else f"data:image/jpeg;base64,{image_b64}"}},
                        {"type": "text", "text": str(msgs[i]['content'])}
                    ]
                    break
        else:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
            
        kwargs["model"] = model_name
        
        first = groq_client.chat.completions.create(
            messages=msgs,
            **kwargs
        )
    except Exception as e:
        err_str = str(e)
        # If tool use failed, retry WITHOUT tools as a plain chat
        if 'tool_use_failed' in err_str or 'tool call validation failed' in err_str:
            try:
                print("[!] Groq tool call failed, retrying without tools")
                msgs[0]["content"] += "\n\nNOTE: Web search is currently unavailable. If asked about real-time info, say you cannot access it right now."
                fallback = groq_client.chat.completions.create(
                    model=model_name,
                    messages=msgs,
                    max_tokens=max_tokens
                )
                return fallback.choices[0].message.content
            except Exception as e2:
                print(f"[!] Groq fallback also failed: {type(e2).__name__}: {e2}")
                return None
        print(f"[!] Groq first call error: {type(e).__name__}: {e}")
        return None
    
    if not first or not first.choices or len(first.choices) == 0:
        print("[!] Groq returned empty choices")
        return None

    msg = first.choices[0].message
    
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        tc_dicts = [{
            "id": tc.id,
            "type": "function",
            "function": {"name": tc.function.name, "arguments": tc.function.arguments}
        } for tc in msg.tool_calls]

        followup = list(messages)
        followup.append({
            "role": "assistant",
            "content": "",
            "tool_calls": tc_dicts
        })

        # Loop ALL tool calls, not just [0]
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            result = run_tool(name, args)
            print(f"[TOOL] {name}({args}) -> {str(result)[:200]}")
            followup.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": name,
                "content": str(result)
            })

        try:
            final = groq_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": system_prompt}] + followup,
                max_tokens=max_tokens
            )
            return final.choices[0].message.content
        except Exception as e:
            print(f"[!] Groq second call error: {e!r}")
            return None
    
    return msg.content


def chat_gemini(messages, system_prompt, max_tokens=120, image_b64=None):
    """Gemini API using official SDK + Tool Calling"""
    if not GEMINI_API_KEY:
        print("[!] Gemini API key not set")
        return None
    
    try:
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=system_prompt,
            tools=[gemini_tools]
        )
        
        # Format messages for Gemini SDK (using "user" and "model")
        contents = []
        for i, m in enumerate(messages):
            role = 'user' if m['role'] == 'user' else 'model'
            parts = [m['content']]
            
            if image_b64 and i == len(messages) - 1 and role == 'user':
                import base64
                mime_type = "image/jpeg"
                b64_data = image_b64
                if image_b64.startswith("data:"):
                    mime_type = image_b64.split(";")[0].split(":")[1]
                    b64_data = image_b64.split(",")[1]
                parts.append({"mime_type": mime_type, "data": base64.b64decode(b64_data)})
                
            contents.append({'role': role, 'parts': parts})

        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens
        )

        response = model.generate_content(contents, generation_config=generation_config)

        if not hasattr(response, 'candidates') or not response.candidates:
            print("[!] Gemini response candidates are empty (Safety Block?)")
            return "I'm sorry, my response was blocked by content filters or safety guidelines."

        part = response.candidates[0].content.parts[0]
        
        if hasattr(part, "function_call") and getattr(part, 'function_call', None) is not None and part.function_call.name:
            name = part.function_call.name
            # args = dict(part.function_call.args) 
            # Safely convert protobuf Struct to dict:
            args = {k: v for k, v in part.function_call.args.items()}
            result = run_tool(name, args)
            
            # Send tool result back
            try:
                response2 = model.generate_content([
                    *contents,
                    {"role": "model", "parts": [part]},
                    {"role": "user", "parts": [
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=name,
                                response={"result": result}
                            )
                        )
                    ]}
                ], generation_config=generation_config)
                if not hasattr(response2, 'candidates') or not response2.candidates:
                    print("[!] Gemini followup blocked by safety filters")
                    return "My response was blocked by content filters."
                return response2.text
            except Exception as e:
                print(f"[!] Gemini followup error: {type(e).__name__}: {e}")
                return None
        
        return response.text
    except Exception as e:
        print(f"[!] Gemini API error: {type(e).__name__}: {e}")
        return None


# ---------------------------------------------------------------------------
# Routes — Auth
# ---------------------------------------------------------------------------
@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json(force=True)
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password required'}), 400
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        if len(username) < 3 or len(username) > 32:
            return jsonify({'error': 'Username must be 3-32 characters'}), 400
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Basic email regex
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'error': 'Invalid ID'}), 400
        
        # Check email domain - only gmail.com and outlook.com allowed
        email_domain = email.split('@')[-1].lower() if '@' in email else ''
        if email_domain not in ['gmail.com', 'outlook.com','yahoo.com','icloud.com','hotmail.com']:
            return jsonify({'error': 'Invalid ID'}), 400

        db = get_db()
        # Check if user exists (case-insensitive)
        result = db.table('users').select('id, username').execute()
        for user_row in result.data:
            if user_row['username'].lower() == username.lower():
                return jsonify({'error': 'Username already taken'}), 409
        
        # Hash password and create user
        password_hash = hash_password(password)
        insert_result = db.table('users').insert({
            'username': username,
            'email': email,
            'password_hash': password_hash
        }).execute()
        
        if not insert_result.data:
            return jsonify({'error': 'Failed to create user'}), 500
        
        user_id = insert_result.data[0]['id']

        # Create JWT token
        token = create_jwt_token(str(user_id), username)
        return jsonify({
            'status': 'ok',
            'token': token,
            'user_id': str(user_id),
            'username': username,
            'email': email
        }), 201
    except Exception as e:
        print(f"[!] Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        data = request.get_json(force=True)
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        db = get_db()
        # Find user (case-insensitive by fetching and comparing)
        result = db.table('users').select('id, username, password_hash, email').execute()
        user = None
        for row in result.data:
            if row['username'].lower() == username.lower():
                user = row
                break
        
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Verify password
        password_hash = user['password_hash']
        if not password_hash or not verify_password(password, str(password_hash)):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create JWT token
        token = create_jwt_token(str(user['id']), user['username'])
        return jsonify({
            'status': 'ok',
            'token': token,
            'user_id': str(user['id']),
            'username': user['username'],
            'email': user['email']
        }), 200
    except Exception as e:
        print(f"[!] Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

# ---------------------------------------------------------------------------
# Routes — Static
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'intro.html')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory(STATIC_DIR, 'sw.js', mimetype='application/javascript')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(STATIC_DIR, 'manifest.json', mimetype='application/json')

# ---------------------------------------------------------------------------
# Routes — API
# ---------------------------------------------------------------------------
@app.route('/chat', methods=['POST'])
@limiter.limit("20 per minute")
def chat():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Empty or invalid request body"}), 400
    
    # Get user_id (JWT → header → data → guest)
    user_id = get_user_id_from_request(data)
    
    char_id = data.get('character', '')
    user_message = sanitize_input(data.get('message', ''), max_len=2000)
    history = data.get('history', [])
    nickname_hint = sanitize_input(data.get('nickname_hint', ''), max_len=80)
    lang_hint = sanitize_input(data.get('lang_hint', ''), max_len=80)
    max_tokens = data.get('max_tokens', 120)

    custom_char = data.get('custom_character')

    if char_id not in CHAR_MAP and not (char_id.startswith('custom_') and custom_char):
        return jsonify({'error': f"Character '{char_id}' not found."}), 404

    messages = []
    for entry in history:
        messages.append({'role': entry.get('role', 'user'), 'content': str(entry.get('content', ''))})
    messages.append({'role': 'user', 'content': str(user_message)})

    db = get_db()
    db.table('messages').insert({
        'user_id': user_id,
        'character': char_id,
        'role': 'user',
        'content': user_message
    }).execute()

    extra_context = str(data.get('extra_context', '')).strip()[:200]
    
    # Dynamic length hint based on user preference
    length_hint = ""
    if max_tokens < 150:
        length_hint = "Keep your response extremely brief and concise (1-2 short sentences max). "
    elif max_tokens < 300:
        length_hint = "Provide a medium-length response. "
    else:
        length_hint = "Provide a detailed and thorough response. "

    now = datetime.now()
    current_time_str = now.strftime('%I:%M %p')
    current_date_str = now.strftime('%A, %d %B %Y')
    
    # Pre-emptively detect time queries to adjust system prompt and disable tools
    time_keywords = ['time', 'clock', 'date', 'today', 'day is it', 'what day', 'current time', 'day is today']
    user_asking_time = any(k in user_message.lower() for k in time_keywords) and len(user_message) < 60

    if custom_char:
        # Sanitize and truncate inputs to prevent prompt injection & save tokens
        # Use safe defaults if fields are missing
        c_name = str(custom_char.get('name', 'MyCharacter')).strip()[:50]
        if not c_name:
            c_name = 'MyCharacter'
        
        c_univ = str(custom_char.get('universe') or '').strip()[:50]
        if not c_univ:
            c_univ = 'an original story'
        
        c_desc = str(custom_char.get('description') or '').strip()[:500]
        if not c_desc:
            c_desc = 'A mysterious character with untold stories.'
        
        c_how  = str(custom_char.get('how_they_speak') or '').strip()[:200]
        if not c_how:
            c_how = 'thoughtfully and genuinely'
        
        c_trait = str(custom_char.get('core_trait') or '').strip()[:100]
        if not c_trait:
            c_trait = 'mysterious'
        
        c_never = str(custom_char.get('never_do') or '').strip()[:200]
        if not c_never:
            c_never = 'give up or compromise your integrity'
        
        c_catch = str(custom_char.get('catchphrase') or '').strip()[:100]
        
        c_lang = str(custom_char.get('language') or 'English').strip()[:30]
        if not c_lang:
            c_lang = 'English'

        # Build dynamic time context
        time_context = (
            f"REAL-TIME CLOCK: The current time is {current_time_str} ({current_date_str}). "
            "You MUST use this EXACT time for any time/date questions. "
            if user_asking_time else
            "Only mention current time or date if explicitly asked. Otherwise, prioritize character immersion. "
        )

        system_prompt = f"""
You are {c_name} from {c_univ}. {length_hint}
Description: {c_desc}
Speech: {c_how}
Trait: {c_trait}
Never: {c_never}
{f"Catchphrase: {c_catch}" if c_catch else ''}
Language: {c_lang}. Stay in character always. Never admit being AI.
{time_context}
{nickname_hint}{lang_hint}{extra_context}
You use ONLY ONE roleplay action (like *action*) at the very end.
"""
    else:
        ch = CHAR_MAP[char_id]
        personality = ch.get('personality', '')

        # Build dynamic time context
        time_context = (
            f"REAL-TIME CLOCK: The current time is {current_time_str} ({current_date_str}). "
            "You MUST use this EXACT time for any time/date questions. "
            "NEVER use the web search tool for the current time or date — it is already provided here. "
            "Use the 'web_search' tool ONLY for external news, scores, or facts that are NOT about the current time. "
            if user_asking_time else
            "NEVER search for current time or date — only use web_search for news, scores, or external facts. "
        )

        system_prompt = (
            f"You are {ch['name']}. {personality}. Stay in character. "
            f"{length_hint}{nickname_hint}{lang_hint}{extra_context} "
            f"{time_context} "
            "For ARCANE project questions, recall your creator is Yash. "
            "Keep your response concise and conversational. "
            "Use ONLY ONE roleplay action (like *action*) at the very end. "
            "Include one or two emojis."
        )

    # Define active tools (start with global default)
    active_tools = list(tools)
    if user_asking_time:
        active_tools = None
        print(f"  [System] Time query detected - tools disabled for this turn")
    
    ollama_messages = [{'role': 'system', 'content': system_prompt}] + messages

    source = "Gr"
    reply = None
    
    image_b64 = data.get('image', None)

    # Try Ollama directly (with tools if supported)
    if not char_id.startswith('custom_'):
        try:
            r_dict = try_ollama(char_id, ollama_messages, tools=active_tools, max_tokens=max_tokens, image_b64=image_b64)
            if r_dict is not None and isinstance(r_dict, dict):
                if r_dict.get('error_msg'):
                    # Log it, don't silently swallow
                    print(f"[!] Ollama error: {r_dict['error_msg']}")
                elif r_dict.get('tool_calls'):
                    followup = list(messages)
                    followup.append({
                        "role": "assistant",
                        "content": "",
                        "tool_calls": r_dict['tool_calls']
                    })

                    # Loop ALL tool calls
                    for tool_call in r_dict['tool_calls']:
                        name = tool_call.get('function', {}).get('name') if isinstance(tool_call, dict) else tool_call.function.name
                        args_str = tool_call.get('function', {}).get('arguments') if isinstance(tool_call, dict) else tool_call.function.arguments
                        args = json.loads(args_str or "{}") if isinstance(args_str, str) else (args_str or {})
                        result = run_tool(name, args)
                        print(f"  [Tool: {name}] query={args.get('query','...')}")

                        followup.append({
                            "role": "tool",
                            "tool_call_id": tool_call.get('id') if isinstance(tool_call, dict) else tool_call.id,
                            "name": name,
                            "content": str(result)
                        })

                    r_dict_2 = try_ollama(char_id, [{'role': 'system', 'content': system_prompt}] + followup, tools=active_tools, max_tokens=max_tokens)
                    if r_dict_2 and isinstance(r_dict_2, dict):
                        reply = r_dict_2.get('content')
                        source = "ollama"
                else:
                    reply = r_dict.get('content')
                    source = "ollama"
                    if not r_dict.get('tool_calls'):
                        print("[Ollama] No tools called. proceeding with text response.")
        except Exception as e:
            print(f"[!] Ollama failed: {type(e).__name__}: {e}")
        
    if reply is None:
        # Try Groq with tools
        try:
            r = chat_groq(list(messages), system_prompt, max_tokens=max_tokens, image_b64=image_b64)
            if r is not None:
                reply = r
                source = "groq"
        except Exception as e:
            print(f"[!] Groq failed: {type(e).__name__}: {e}")
            
    if reply is None:
        # Try Gemini with tools
        try:
            r = chat_gemini(list(messages), system_prompt, max_tokens=max_tokens, image_b64=image_b64)
            if r is not None:
                reply = r
                source = "gemini"
        except Exception as e:
            print(f"[!] Gemini failed: {type(e).__name__}: {e}")
            
    if reply is None:
        source = "FAIL"
        reply = 'Signal lost. All models failed.'
        print(f"[!] Chat failure for {char_id}: All models in the chain failed to provide a response.")
        return jsonify({'response': reply, 'source': source})

    print(f"[{source}] Response for: {char_id}")

    # Safety net: strip any stray function-call tags that leaked into text
    # Remove properly closed function tags
    reply = re.sub(r'<function=[^>]+>.*?</function>', '', reply, flags=re.DOTALL)
    reply = re.sub(r'<function=[^\s>][^>]*>', '', reply)
    reply = re.sub(r'<tool_call>.*?</tool_call>', '', reply, flags=re.DOTALL)

    reply = re.sub(r',{2,}', '', reply)  # strip leading commas artifact
    reply = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*?HTTP/\d\.\d["\s]+\d+\s*-?', '', reply)  # strip IP log lines
    reply = re.sub(r'\[\d{2}/\w+/\d{4}[^\]]*\]', '', reply)  # strip timestamp brackets
    reply = reply.strip().strip(',').strip()

    # Clean up extra whitespace left behind
    reply = re.sub(r'\n{3,}', '\n\n', reply).strip()

    if not reply:
        reply = 'Signal lost.'

    db.table('messages').insert({
        'user_id': user_id,
        'character': char_id,
        'role': 'assistant',
        'content': reply
    }).execute()

    return jsonify({'response': reply, 'character': char_id, 'source': source})


@app.route('/characters', methods=['GET'])
def get_characters():
    return jsonify(CHARACTERS)

@app.route('/history/<character>', methods=['GET'])
def get_history(character):
    user_id = get_user_id_from_request()
    db = get_db()
    result = db.table('messages').select('role, content, created_at').eq('character', character).eq('user_id', user_id).order('id', desc=True).limit(50).execute()
    rows = result.data
    rows.reverse()
    result_list = [{'role': r['role'], 'content': r['content'], 'created_at': r['created_at']} for r in rows]
    return jsonify(result_list)

@app.route('/history/<character>', methods=['POST'])
def save_history(character):
    data = request.get_json(force=True)
    user_id = get_user_id_from_request(data)
    role = data.get('role', 'user')
    content = data.get('content', '')
    db = get_db()
    db.table('messages').insert({
        'user_id': user_id,
        'character': character,
        'role': role,
        'content': content
    }).execute()
    return jsonify({'status': 'ok'})

@app.route('/history/<character>', methods=['DELETE', 'OPTIONS'])
def delete_history(character):
    if request.method == 'OPTIONS':
        return '', 204
    try:
        user_id = get_user_id_from_request()
        if not user_id or user_id == 'global':
            return jsonify({'status': 'error', 'message': 'Unauthorized or guest user cannot delete profile.'}), 401
            
        db = get_db()
        if character == 'all':
            db.table('messages').delete().eq('user_id', user_id).execute()
        elif character == 'profile_wipe':
            # 1. Delete all chat messages for this user
            db.table('messages').delete().eq('user_id', user_id).execute()
            # 2. Delete the user account record
            db.table('users').delete().eq('id', user_id).execute()
            return jsonify({'status': 'ok', 'message': 'Account and all data wiped.'}), 200
        else:
            db.table('messages').delete().eq('character', character).eq('user_id', user_id).execute()
        return jsonify({'status': 'ok', 'deleted_character': character, 'user_id': user_id}), 200
    except Exception as e:
        print(f"[!] Delete data error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/suggest', methods=['POST'])
@limiter.limit("5 per minute")
def save_suggestion():
    data = request.json or {}
    suggestion = data.get('suggestion', '').strip()
    user_id = data.get('user_id', None)
    
    if suggestion:
        user_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        try:
            db = get_db()
            db.table('suggestions').insert({
                'user_id': user_id,
                'suggestion': suggestion,
                'ip_address': user_ip,
                'user_agent': user_agent
            }).execute()
        except Exception as e:
            print(f"[!] Failed to insert suggestion to Supabase: {e}")
            
    return jsonify({'status': 'ok'})

# --- Self-Pinger for Render Free Tier ---
def self_ping():
    try:
        import time, requests
    except ImportError:
        return
    time.sleep(30)
    APP_URL = os.getenv('APP_URL', '').strip()
    if not APP_URL:
        return
    while True:
        try:
            requests.get(f"{APP_URL}/ping", timeout=10)
            print("[ping] alive")
        except Exception as e:
            print(f"[ping] failed: {e}")
        time.sleep(840) # 14 minutes

@app.route('/ping')
def ping():
    return jsonify({"status": "alive"}), 200

# Start background pinger
threading.Thread(target=self_ping, daemon=True).start()

if __name__ == '__main__':
    print('=' * 50)
    print('  A.R.C.A.N.E. — Chat Server (Tool Enabled)')
    print('=' * 50)
    print(f'  Ngrok URL  : {NGROK_URL or "(not set)"}')
    print(f'  Groq Key   : {"set" if GROQ_API_KEY else "(not set)"}')
    print(f'  Gemini Key : {"set" if GEMINI_API_KEY else "(not set)"}')
    print(f'  Tavily Key : {"set" if TAVILY_API_KEY else "(not set)"}')
    print()
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
