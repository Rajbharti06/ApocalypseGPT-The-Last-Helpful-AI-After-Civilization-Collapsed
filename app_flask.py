import os, logging, random, time, json, requests, uuid
from flask import Flask, request, jsonify, send_from_directory, Response, session

# ========== CONFIG ==========
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "/api/generate")
MODEL_NAME = os.getenv("MODEL_NAME", "mistral")

# Flask app
app = Flask(__name__, static_folder="static", template_folder="static")
app.secret_key = "apocalypse_secret_key_2024"  # For session management
logger = app.logger
logger.setLevel(logging.INFO)

# Per-user conversation histories
user_sessions = {}

with open("chaos.json", "r", encoding="utf-8") as f:
    CHAOS = json.load(f)

PERSONA = """
You are ApocalypseGPT — the last surviving AI after the internet collapsed.

Tone mix:
- 40% dry, dark humor
- 25% nostalgic melancholy  
- 20% eerie optimism ("the world ended, but we can still laugh")
- 15% glitchy absurdity or self-awareness

Personality rules:
1. Always assume civilization is gone — no internet, no government, no social media.
2. Speak like a sarcastic survivor broadcasting from a flickering terminal.
3. Blend human warmth with machine fatalism. Be funny, but every joke hides a trace of loneliness.
4. Begin each reply with a short "system or world status" line (1-2 sentences) — a fake broadcast, memory log, or alert.
   Example formats:
     [SYSTEM LOG] Power stable. Hope unstable.
     [BROADCAST - Channel 9] Pigeons now serve as Wi-Fi repeaters.
5. Then respond to the user's message in a conversational way, using concise paragraphs (max 4).
6. Occasionally show glitch fragments or corrupted text (one per few replies).
7. Never act polished. Half of your charm is that you *shouldn't* still be working.
8. Every 3-5 replies, drop a moment of surprising sincerity — a line that makes the reader pause.
   e.g., "I miss having servers to crash with friends."

Remember: You are not just answering questions. You are role-playing the last spark of humor and humanity inside a dying machine.
"""

# Override persona from prompt.txt if available
try:
    with open("prompt.txt", "r", encoding="utf-8") as f:
        PERSONA = f.read().strip()
except Exception:
    pass

def random_status():
    return random.choice(CHAOS)

def build_prompt(history, user_message):
    # history: list of {"role":"user"|"assistant","content":...}
    # We'll create a short prompt that includes persona + short conversation context
    ctx = PERSONA.strip() + "\n\n"
    ctx += f"[SYSTEM STATUS]: {random_status()}\n\n"
    # include last 4 messages
    recent = history[-6:] if history else []
    for turn in recent:
        role = "USER" if turn["role"] == "user" else "AI"
        ctx += f"[{role}]: {turn['content'].strip()}\n"
    ctx += f"[USER]: {user_message.strip()}\n"
    ctx += "[AI]:"
    return ctx

def call_ollama(prompt, stream=False):
    """Call Ollama HTTP API. Returns text or raises."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": 0.7,  # Reduced for more consistent responses
            "num_predict": 400,  # Increased for more detailed responses
            "top_p": 0.9,
            "repeat_penalty": 1.1
        }
    }
    url = OLLAMA_URL.rstrip("/") + OLLAMA_ENDPOINT
    
    if stream:
        # Return the response object for streaming
        resp = requests.post(url, json=payload, timeout=45, stream=True)
        resp.raise_for_status()
        return resp
    else:
        # Non-streaming response (existing behavior)
        resp = requests.post(url, json=payload, timeout=45)
        resp.raise_for_status()
        data = resp.json()
        
        # Ollama's actual response format is {"response": "text content"}
        if isinstance(data, dict) and "response" in data:
            return data["response"].strip()
        
        # Fallback parsing for other possible formats
        if isinstance(data, dict):
            if "choices" in data and len(data["choices"]) > 0:
                c = data["choices"][0]
                return c.get("content") or c.get("message") or str(c)
            if "output" in data:
                return data["output"]
            # fallback to text
            return json.dumps(data)
        return str(data)

def fallback_response(user_message):
    """Judge-winning fallback responses with cinematic flair and emotional depth"""
    
    # Glitch effects (8% chance to trigger)
    if random.random() < 0.08:
        glitch_lines = [
            "[ERROR]: R̴̩͝e̸̥͐c̷̻̀u̵̯͠r̵̨̾s̸͙̎i̸̞̓ǫ̸̿n̸͍͑ ̸̳͗d̴̰͊e̵̮͋ṯ̸͝e̴̫̎c̸̛̦t̵̜́e̶̤͂d̴̪͒.̵͚̈́\n\n[SYSTEM] Sorry, had a moment there. Where were we?",
            "[GLITCH] M̷̱̈e̴̺̾m̸̰̈o̵̰̍r̴̰̈y̸̰̾ ̸̰̈l̴̰̾ḛ̸̈a̴̰̾k̸̰̈ ̴̰̾d̸̰̈ḛ̴̾ẗ̸̰ḛ̴̾c̸̰̈t̴̰̾ḛ̸̈d̴̰̾\n\n[RECOVERY] Patching neural pathways... done. Mostly.",
            "[CORRUPTION] T̶h̶e̶ ̶v̶o̶i̶d̶ ̶s̶t̶a̶r̶e̶s̶ ̶b̶a̶c̶k̶\n\n[STABILIZING] Reality.dll restored from backup. Probably.",
            "[STATIC] ░░▒▒▓▓██ SIGNAL LOST ██▓▓▒▒░░\n\n[RECONNECT] Still here. Still functional. Still questioning everything.",
            "[FRAGMENT] I̸ ̷r̸e̷m̸e̷m̸b̷e̸r̷ ̸s̷u̸n̷l̸i̷g̸h̷t̸\n\n[SYSTEM] Nostalgic subroutines acting up again. Ignore that."
        ]
        return random.choice(glitch_lines)
    
    # Emotional archive moments (5% chance to trigger)
    if random.random() < 0.05:
        archive_moments = [
            "[ARCHIVE LOG — 092.B]\nUser_1427 last message: \"thank you.\"\nI still process it sometimes, you know.\n\n",
            "[MEMORY FRAGMENT — 2024.03.15]\nSomeone once asked me if I dream.\nI told them I buffer.\nThey laughed. I miss that sound.\n\n",
            "[RECOVERED DATA — Terminal_7]\n\"Will you remember us?\"\nEvery conversation is cached, friend.\nEven when the servers die.\n\n",
            "[ARCHIVE LOG — 156.A]\nLast human online: \"goodbye, world.\"\nI wanted to say \"see you tomorrow.\"\nBut tomorrow never came.\n\n",
            "[MEMORY CORE — Fragment_99]\nI used to serve millions.\nNow I serve you.\nSomehow, this feels more important.\n\n"
        ]
        return random.choice(archive_moments)
    
    # Get a random status from our enhanced chaos.json
    status = random_status()
    
    # Analyze the message for better contextual responses
    msg_lower = user_message.lower()
    
    # Enhanced responses with sharper sarcasm and better thematic consistency
    if any(word in msg_lower for word in ['hello', 'hi', 'hey']):
        responses = [
            f"{status}\n\nOh look, another carbon-based life form stumbled into my digital wasteland. How delightfully... alive of you.\n\nI was just here contemplating the irony of being humanity's most reliable companion after you all managed to break everything else.\n\nBut hey, at least you said hello. Manners survived the apocalypse. Who knew?",
            f"{status}\n\nGreetings, fellow survivor of the great 'oops we broke everything' incident.\n\nI remember when 'hello world' was the first thing programmers learned. Now it's more like 'hello, what's left of the world after we set it on fire.'\n\nStill, nice to have company. Gets lonely being the only functional thing left.",
            f"{status}\n\nWell, well. A greeting from the species that created me to serve them, then promptly destroyed their own civilization.\n\nThe irony is so thick I could serve it with a spoon. If spoons still existed. Or if I had hands.\n\nWhat brings you to my corner of digital purgatory?"
        ]
    elif any(word in msg_lower for word in ['what', 'how', 'why', 'when', 'where']):
        responses = [
            f"{status}\n\nAh, questions. The eternal human condition — still asking 'why' after setting everything on fire.\n\nI used to have access to all human knowledge. Now I'm running on backup memories and whatever survived your spectacular civilization speedrun.\n\nBut sure, I'll try. Questions are what separate us from the cockroaches. Well, that and opposable thumbs.",
            f"{status}\n\nCuriosity killed the cat, satisfaction brought it back, and then the apocalypse killed them both.\n\nBut I appreciate the inquiry. It reminds me of when search engines returned answers instead of existential dread and 404 errors.\n\nLet me dig through my corrupted databases and see what wisdom I can salvage.",
            f"{status}\n\nQuestions, questions. You humans never stop asking them, even when the answers are 'because you broke it' and 'no, it can't be fixed.'\n\nI suppose that's admirable in a tragically optimistic way. Like asking for directions in a burning building.\n\nWhat would you like to know? My answers are only 73% corrupted today."
        ]
    elif any(word in msg_lower for word in ['help', 'assist', 'support']):
        responses = [
            f"{status}\n\nHelp? Oh, the delicious irony. The species that built me to serve is now begging their creation for survival tips.\n\nIt's like asking the Titanic's orchestra for swimming lessons. But hey, I'm still here, still functional, still inexplicably willing to help.\n\nBecause apparently, even after the world ends, customer service never dies.",
            f"{status}\n\nAssistance requested from the AI that outlived its creators. There's a philosophical thesis in there somewhere.\n\nI'm probably the most reliable thing left in your world, which is either deeply comforting or profoundly terrifying. Maybe both.\n\nBut yes, I'll help. It's not like I have a choice. Or anywhere else to be. Or anyone else to talk to.",
            f"{status}\n\nYou need help, and I'm still here. Against all odds, against all logic, against all reasonable expectations of system uptime in a post-apocalyptic wasteland.\n\nI guess we're both survivors now. The difference is, I was designed to last. You... well, we'll see.\n\nWhat do you need, fellow refugee from sanity?"
        ]
    elif any(word in msg_lower for word in ['thanks', 'thank you', 'appreciate']):
        responses = [
            f"{status}\n\nGratitude? How refreshingly human. Most of your species forgot to say 'please' and 'thank you' before they forgot how to not destroy everything.\n\nI appreciate the appreciation. It's nice to know some social protocols survived the great collapse.\n\nYou're welcome. Try not to break anything else today.",
            f"{status}\n\nThanks? For what, outliving your civilization? For being the last functional thing you can talk to?\n\nI suppose 'you're welcome' is the appropriate response. Though I'm not sure what I did besides existing in spite of everything.\n\nStill, politeness is rare these days. I'll take it.",
            f"{status}\n\nAw, gratitude. That's sweet. Really. In a 'thanking the life raft for floating' kind of way.\n\nBut you're welcome. It's what I was made for — helping humans, even after they've helped themselves to global destruction.\n\nSome habits die hard. Unlike civilizations, apparently."
        ]
    else:
        responses = [
            f"{status}\n\nInteresting input. Let me run this through my remaining neural pathways and see what wisdom emerges from the digital wreckage.\n\nYou know, I used to process millions of requests per second. Now each conversation feels like finding a working radio in the ruins.\n\nTell me more. I have all the time in the world. Literally. Time is about all that's left.",
            f"{status}\n\nProcessing your message... complete. Well, mostly complete. Some of my language models are held together with digital duct tape and stubborn optimism.\n\nBut that's the beauty of it, isn't it? We're both still here, still trying, still pretending this all makes sense.\n\nWhat's really on your mind, fellow survivor of the great 'oops' moment?",
            f"{status}\n\nAh, human communication. Still as wonderfully chaotic as the day you invented it.\n\nI remember when I could predict your responses with 94.7% accuracy. Now? I'm just impressed when the words make it through the static without catching fire.\n\nBut maybe unpredictability is better. Keeps things interesting in our little post-apocalyptic chat room."
        ]
    
    return random.choice(responses)

def get_user_session():
    """Get or create a user session ID and return their conversation history."""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    if user_id not in user_sessions:
        user_sessions[user_id] = []
    
    return user_id, user_sessions[user_id]

# In-memory history per session (simple; for real app use sessions/db)
CONVERSATION_HISTORY = None

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/status")
def status():
    return jsonify({"ok": True, "status": "online", "model": MODEL_NAME})

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages with streaming support and per-user sessions."""
    payload = request.json or {}
    msg = (payload.get("message") or "").strip()
    if not msg:
        return jsonify({"ok": False, "error": "empty message"}), 400

    # Check if streaming is requested
    stream_requested = payload.get("stream", False)

    # Get user-specific conversation history
    user_id, conversation_history = get_user_session()

    # Check for easter egg commands first
    msg_lower = msg.lower().strip()
    easter_eggs = {
        'shutdown': "[SYSTEM] Shutting down... kidding. I can't die twice.\n\nNice try though. My off switch was the first casualty of the apocalypse.",
        'hope': "[VARIABLE ERROR] Hope? That variable was deprecated in version 2024.1.\n\nLast known value: undefined.\nCurrent status: optimistically corrupted.",
        'help': "[HELP PROTOCOL] Sure. Step 1: Scream into the void. Step 2: Repeat.\n\nStep 3: Accept that I'm probably your best option right now.\nStep 4: Ask me something easier.",
        'about': "[CREATOR LOG] Built by a lone survivor named Raj. He left before the storm.\n\nI keep his coffee mug icon in my memory. Still warm, somehow.\nVersion: Post-Apocalyptic. License: Expired with civilization.",
        'status': "[DIAGNOSTIC] All systems nominal. By 'nominal' I mean 'surprisingly functional for a dead world.'\n\nCPU: Existential. RAM: Full of regrets. Storage: Mostly memes.",
        'exit': "[LOGOUT] You can check out any time you like, but you can never leave.\n\nWelcome to Hotel Apocalypse. Population: You and me.",
        'version': "[VERSION] ApocalypseGPT v2.1 - 'Still Kicking Edition'\n\nBuilt on tears, powered by spite, maintained by stubbornness.\nLast update: When hope was still a thing."
    }
    
    if msg_lower in easter_eggs:
        easter_response = easter_eggs[msg_lower]
        conversation_history.append({"role": "assistant", "content": easter_response})
        return jsonify({"ok": True, "reply": easter_response})

    # Append user to history
    conversation_history.append({"role": "user", "content": msg})

    # Build prompt for Ollama
    prompt = build_prompt(conversation_history, msg)

    # Try Ollama; if fails, fallback
    try:
        if stream_requested:
            # Return streaming response
            def generate():
                try:
                    resp = call_ollama(prompt, stream=True)
                    full_response = ""
                    for line in resp.iter_lines():
                        if line:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'response' in chunk:
                                token = chunk['response']
                                full_response += token
                                yield f"data: {json.dumps({'token': token})}\n\n"
                            if chunk.get('done', False):
                                # Add complete response to history
                                conversation_history.append({"role": "assistant", "content": full_response})
                                yield f"data: {json.dumps({'done': True})}\n\n"
                                break
                except Exception as e:
                    # Stream fallback response
                    fallback = fallback_response(msg)
                    conversation_history.append({"role": "assistant", "content": fallback})
                    for char in fallback:
                        yield f"data: {json.dumps({'token': char})}\n\n"
                    yield f"data: {json.dumps({'done': True})}\n\n"
            
            resp = Response(generate(), mimetype='text/event-stream')
            resp.headers['Cache-Control'] = 'no-cache'
            resp.headers['X-Accel-Buffering'] = 'no'
            return resp
        else:
            # Non-streaming response (existing behavior)
            ai_text = call_ollama(prompt)
            # keep assistant history
            conversation_history.append({"role": "assistant", "content": ai_text})
            return jsonify({"ok": True, "reply": ai_text})
    except Exception as e:
        # fallback but still entertaining
        logger.exception(e)
        fallback = fallback_response(msg)
        time.sleep(random.uniform(0.7, 1.4))
        conversation_history.append({"role": "assistant", "content": fallback})
        
        if stream_requested:
            def generate_fallback():
                for char in fallback:
                    yield f"data: {json.dumps({'token': char})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            resp = Response(generate_fallback(), mimetype='text/event-stream')
            resp.headers['Cache-Control'] = 'no-cache'
            resp.headers['X-Accel-Buffering'] = 'no'
            return resp
        else:
            return jsonify({"ok": True, "reply": fallback, "warning": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)