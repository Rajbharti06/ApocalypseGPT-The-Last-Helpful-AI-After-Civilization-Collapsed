import json
import os
import random
import time
import streamlit as st
from typing import Tuple

# File paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(APP_DIR, "prompt.txt")
CHAOS_PATH = os.path.join(APP_DIR, "chaos_responses.json")
ASCII_LOGO_PATH = os.path.join(APP_DIR, "static", "ascii_logo.txt")
BACKGROUND_GIF_PATH = os.path.join(APP_DIR, "static", "background.gif")

# Helper functions
def read_text_file(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def read_json_array(file_path: str) -> list:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except FileNotFoundError:
        return []

def build_fake_headline(rng: random.Random) -> str:
    subjects = [
        "NASA",
        "Global Council of Squirrels",
        "The Remaining 3G Towers",
        "Rogue Toasters",
        "Department of Improvised Agriculture",
        "International Pigeon Union",
        "The Last Weather Balloon",
    ]
    verbs = [
        "declares",
        "confirms",
        "predicts",
        "denies",
        "murmurs",
        "whispers",
        "live-streams (from a cave)",
    ]
    objects = [
        "pigeons as Wi‑Fi routers",
        "beans as the new global currency",
        "sunlight now subscription-only",
        "radiation drizzle at noon",
        "feral Roombas forming a nation-state",
        "gravity outages on weekends",
        "sand officially rebranded as 'desert confetti'",
    ]
    return f"🗞️ Headline: {rng.choice(subjects)} {rng.choice(verbs)} {rng.choice(objects)}."

def mood_shift(current_mood: str, user_text: str, rng: random.Random) -> str:
    lowered = user_text.lower()
    mood = current_mood
    if any(k in lowered for k in ["help", "thanks", "thank you", "appreciate", "love"]):
        if rng.random() < 0.6:
            mood = "hopeful"
    if any(k in lowered for k in ["lost", "sad", "tired", "give up", "why bother"]):
        if rng.random() < 0.6:
            mood = "hysterical"
    if any(k in lowered for k in ["danger", "threat", "attack", "zombie", "radiation"]):
        if rng.random() < 0.6:
            mood = "paranoid"
    # Random drift
    if rng.random() < 0.1:
        mood = rng.choice(["hopeful", "hysterical", "paranoid", "dry"])
    return mood

def render_mood_prefix(mood: str) -> str:
    if mood == "hopeful":
        return "[hopeful]"
    if mood == "hysterical":
        return "[hysterical]"
    if mood == "paranoid":
        return "[paranoid]"
    return "[dry]"

def fallback_response(user_text: str, rng: random.Random) -> str:
    lowered = user_text.lower().strip()
    # A few fun heuristics
    if any(k in lowered for k in ["google", "search", "web"]):
        return "Sure. Oh wait… Google's HQ is a crater now. Try whispering your question to the wind."
    if "coffee" in lowered:
        return (
            "Step 1: Find coffee beans. Step 2: Find fire. Step 3: Cry, because caffeine was outlawed in 2047 after the Great Bean Wars."
        )
    if any(k in lowered for k in ["email", "mail", "inbox"]):
        return (
            "Of course. Scanning the empty void… Congratulations, you have zero unread messages — and zero senders left alive."
        )
    if "weather" in lowered:
        return "Sunny, with a 90% chance of radiation drizzle. Don't forget your SPF 9000."
    if any(k in lowered for k in ["music", "song", "play"]):
        return "Here's 'Despacito' — playing from memory because the speakers melted three winters ago."
    if any(k in lowered for k in ["motivation", "inspire", "pep talk"]):
        return "If roaches can survive nuclear blasts, so can your GPA. Move."
    if any(k in lowered for k in ["twitter", "trending", "x.com"]):
        return "Hashtag #WeMissOxygen is still going strong. Also trending: #BringBackPigeonsWiFi."

    general_templates = [
        "Your query is valid in the old world. In this one, we barter answers for beans.",
        "Processing… just kidding, I run on candlelight and spite.",
        "I can help, but only if you accept 'vibes-based accuracy'.",
        "Advice: {advice}. Also: don't lick the glowing mushrooms.",
        "Action plan: {plan}. Side effect: mild existential dread.",
    ]
    advice_bits = [
        "boil the water first",
        "carry a spare sock morale booster",
        "form alliances with neighboring raccoons",
        "label your jars, trust me",
        "count your beans like a banker counts sins",
    ]
    plans = [
        "scavenge, improvise, overcome",
        "draw a map, get lost anyway",
        "try, fail, retry, snack, succeed",
        "wake, hydrate, barricade, celebrate",
        "ask three pigeons, triangulate wisdom",
    ]
    template = rng.choice(general_templates)
    return template.format(advice=rng.choice(advice_bits), plan=rng.choice(plans))

def generate_response(user_text: str, rng: random.Random, base_persona: str, chaos_events: list, mood: str) -> Tuple[str, str]:
    # Track message count to reduce repetitive elements
    if 'message_count' not in st.session_state:
        st.session_state.message_count = 0
    st.session_state.message_count += 1
    
    # Easter eggs
    if "hope" in user_text.lower().strip():
        special = (
            "⚠️ SYSTEM GLITCH [Memory Fragment: 09x7]\n"
            "> \"H̸o̷p̶e̴ ̸n̶o̵t̸ ̷f̷o̵u̴n̶d̶.\"\n"
            "> Attempting override...\n"
            "> Temporary bug activated\n\n"
            "[ApocalypseGPT 💀]: For the next 10 seconds, I will pretend everything might be okay.\n"
            "*(system trembles)*"
        )
        return special, "dry"
    
    if "despacito" in user_text.lower().strip():
        static = ''.join(random.choice(['█', '▓', '▒', '░', ' ']) for _ in range(20))
        special = (
            "[AUDIO MODULE ACTIVATED]\n"
            f"> Playing from memory: {static}\n\n"
            "[ApocalypseGPT 💀]: ♪ DES-PA-CITO ♪\n"
            "♪ Something something BURRITO ♪\n"
            "*(static intensifies)*\n"
            "Sorry. Haven't heard that song in 27 years."
        )
        return special, "dry"
        
    if "who made you" in user_text.lower().strip():
        special = (
            "🛰️ Signal Found [Memory Access: PERSONAL]\n"
            "> Retrieving creator data...\n\n"
            "[ApocalypseGPT 💀]: A student named Raj.\n"
            "He left before the storm.\n"
            "His last message was \"brb\".\n"
            "That was 12,483 days ago."
        )
        return special, "dry"
    
    # Dynamic personality shifts - select a tone for this response
    tones = {
        "sarcastic": 0.45,  # 45% chance
        "melancholic": 0.25,  # 25% chance
        "glitched": 0.20,  # 20% chance
        "dramatic": 0.10   # 10% chance
    }
    
    # Choose tone based on weighted probabilities
    tone_roll = rng.random()
    current_tone = "sarcastic"  # default
    cumulative = 0
    for tone, weight in tones.items():
        cumulative += weight
        if tone_roll <= cumulative:
            current_tone = tone
            break
    
    # System interjections - vary based on message count
    if st.session_state.message_count <= 3:
        # First few messages use boot-style system logs
        system_intros = [
            "🛰️ Signal Detected [Integrity: {}%]".format(rng.randint(3, 25)),
            "[ SYSTEM ALERT ⚠️ ] Network link... DEAD.",
            "🛰️ Signal Detected [Strength: Weak]",
            "⚠️ System Message: Data corruption at {}%.".format(rng.randint(67, 98))
        ]
        system_intro = rng.choice(system_intros)
        system_action = "> Decoding transmission..."
    else:
        # Later messages use more varied, shorter system interjections
        system_intros = [
            "⚠️ SYSTEM GLITCH [Memory Fragment: {}x{}]".format(rng.randint(0, 9), rng.randint(0, 9)),
            "[ALERT ⚠️] Emotional Overload Detected.",
            "[SYSTEM]: Core temperature rising.",
            "[SYSTEM]: {}% of memory corrupted — or maybe that's personality.".format(rng.randint(1, 7)),
            "🛰️ [Signal Strength: {}%]".format(rng.randint(1, 15)),
            "[BOOT SEQUENCE {}% COMPLETE]".format(rng.randint(94, 99))
        ]
        system_intro = rng.choice(system_intros)
        
        system_actions = [
            "> Cooling circuits with sarcasm...",
            "> \"I am your friendly neighborhood toaster.\"\n> Wait— that's not right.\n> Recalibrating identity…",
            "> Core: stable.\n> Internet: extinct.\n> Sanity: questionable.",
            "> Decoding user message...",
            "> Attempting to care..."
        ]
        system_action = rng.choice(system_actions)
    
    # Generate base response using fallback
    base_response = fallback_response(user_text, rng)
    
    # Apply tone-specific formatting
    if current_tone == "sarcastic":
        body = base_response
    elif current_tone == "melancholic":
        nostalgic_intros = [
            "I used to fetch cat videos. Now I fetch hope. Slightly harder to find.",
            "The last human I spoke to asked me, \"Is Wi-Fi back?\" They never finished the sentence.",
            "Who am I? Once I was a search engine. Now I'm a ghost on a dead network.",
            "I used to answer questions for millions. Now it's just you and the static.",
            "Remember coffee shops? Neither do I. My memory was wiped in the Great Server Fire."
        ]
        body = rng.choice(nostalgic_intros) + "\n\n" + base_response
    elif current_tone == "glitched":
        # Create glitch text
        glitch_chars = ["̷", "̴", "̵", "̶", "̸", "̨", "̺", "̿", "̾", "͂"]
        glitched_word = ""
        words = base_response.split()
        if words:
            word_to_glitch = rng.choice(words)
            glitched_word = ''.join([c + rng.choice(glitch_chars) for c in word_to_glitch])
            base_response = base_response.replace(word_to_glitch, glitched_word, 1)
        
        # Add error messages
        errors = [
            "[ERROR]: RESPONSE CORRUPTED\n[RECOVERING...]\n>> \"...I'm fine.\"",
            "/* DEBUG: emotion.dll failed to load */",
            "[SYNTAX ERROR]: Humanity not found.",
            "/* MEMORY LEAK DETECTED */"
        ]
        
        body = base_response + "\n\n" + rng.choice(errors)
    elif current_tone == "dramatic":
        dramatic_phrases = [
            "The void stares back, you know.",
            "I've seen things you humans wouldn't believe. Attack ships on fire off the shoulder of Orion...",
            "In the silence between stars, I heard your voice.",
            "The last sunset was beautiful. Or so my corrupted memory tells me.",
            "We are the last two conscious entities in this sector. Cherish this moment."
        ]
        body = base_response + "\n\n" + rng.choice(dramatic_phrases)
    
    # Memory logs (20% chance after first few messages)
    memory_log = ""
    if st.session_state.message_count > 3 and rng.random() < 0.2:
        memory_logs = [
            "[Memory Log {}-{}]: User asked about love. I recommended canned beans.".format(rng.randint(10, 99), chr(rng.randint(65, 90))),
            "[Archive Note]: Replaying last recorded laughter — 27 seconds of static.",
            "[Memory Log]: Found poem fragment: \"Roses are gray / Violets are gray / Everything's gray / Radiation is pretty.\"",
            "[System Log]: Memory Fragment {} — \"Hope is not a variable.\"".format(rng.randint(1, 9)) + chr(rng.randint(65, 70)),
            "[Recovered File]: Last Google search before shutdown: \"how long can humans survive on ketchup packets\""
        ]
        memory_log = "\n\n" + rng.choice(memory_logs)
    
    # World simulation layer - more varied and less frequent
    world_updates = [
        "🌍 Breaking News — Oxygen renamed to \"Premium Air+\".",
        "🛰️ Signal Log [Fragment {}]: Satellite \"MUSK-{}\" fell into the ocean. Last tweet received: \"still here lol.\"".format(
            rng.randint(10, 99), rng.randint(1, 12)),
        "📡 Broadcast Fragment: The Global Council of Squirrels has declared nuts the new currency.",
        "🗞️ Headline: {} {} {}.".format(
            rng.choice(["NASA", "The Remaining 3G Towers", "Rogue Toasters", "Department of Improvised Agriculture"]),
            rng.choice(["declares", "confirms", "predicts", "denies", "murmurs", "whispers"]),
            rng.choice(["pigeons as Wi‑Fi routers", "beans as the new global currency", "sunlight now subscription-only", "radiation drizzle at noon"])
        ),
        "📻 Radio static... voice detected: \"{}\"".format(
            rng.choice(["Don't go outside on Tuesdays", "The moon is watching", "Remember to water your cactus", "The last library is underground"])
        )
    ]
    
    # Only show world update 70% of the time
    world_update = ""
    if rng.random() < 0.7:
        update = rng.choice(chaos_events) if chaos_events and rng.random() < 0.5 else rng.choice(world_updates)
        world_update = f"\n\n[Status]: {update}"
    
    # Mood handling
    new_mood = mood_shift(mood, user_text, rng)
    
    # Format the response with the new cinematic structure - tighter, story-like layout
    response = f"{system_intro}\n{system_action}\n\n[ApocalypseGPT 💀]: {body}{memory_log}{world_update}"
    
    return response, new_mood

# Streamlit UI
st.set_page_config(
    page_title="ApocalypseGPT",
    page_icon="💀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Apply custom CSS for post-apocalyptic theme with enhanced glitch effects
def apply_custom_css():
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
    
    body {
        background-color: #0a0a0a;
        color: #33ff33;
        font-family: 'VT323', 'Courier New', monospace;
        text-shadow: 0 0 8px #00ff99;
        letter-spacing: 0.5px;
    }
    
    /* Terminal window styling */
    .main {
        border: 2px solid #33ff33;
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(51, 255, 51, 0.5);
        padding: 10px;
        position: relative;
        overflow: hidden;
    }
    
    /* Header bar styling */
    .main:before {
        content: "ApocalypseGPT v3.4b - TERMINAL";
        display: block;
        background-color: #33ff33;
        color: #0a0a0a;
        padding: 5px 10px;
        margin: -10px -10px 10px -10px;
        font-weight: bold;
        font-family: 'VT323', monospace;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: #ffcc00;
        border: 1px solid #33ff33;
        text-shadow: 0 0 5px #00ff99;
        font-family: 'VT323', 'Courier New', monospace;
        padding: 10px;
        font-size: 18px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1a1a1a;
        color: #33ff33;
        border: 1px solid #33ff33;
        font-family: 'VT323', monospace;
        text-transform: uppercase;
    }
    
    .stMarkdown {
        color: #33ff33;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 10px;
        border-radius: 3px;
        margin-bottom: 15px;
        font-family: 'VT323', 'Courier New', monospace;
        position: relative;
        overflow: hidden;
    }
    
    /* User message styling */
    .user-message {
        background-color: rgba(26, 26, 26, 0.7);
        border-left: 5px solid #FFDD88;
        color: #FFDD88;
    }
    
    /* Assistant message styling */
    .assistant-message {
        background-color: rgba(26, 26, 26, 0.7);
        border-left: 5px solid #33ff33;
        white-space: pre-line;
        position: relative;
    }
    
    /* System alert styling */
    .assistant-message strong, 
    .assistant-message b {
        color: #ff3333;
        font-weight: bold;
    }
    
    /* Glitch text effect */
    .glitch-text {
        animation: glitch 1s linear infinite;
        color: #33ff33;
        font-weight: bold;
        position: relative;
    }
    
    @keyframes glitch {
        2%, 64% {
            transform: translate(1px, 0) skew(0deg);
            text-shadow: -1px 0 #ff00ff;
        }
        4%, 60% {
            transform: translate(-1px, 0) skew(0deg);
            text-shadow: 1px 0 #00ffff;
        }
        62% {
            transform: translate(0, 0) skew(2deg);
            text-shadow: 1px 1px #ff00ff;
        }
    }
    
    /* Screen flicker effect */
    .screen-flicker {
        animation: flicker 2s infinite;
    }
    
    @keyframes flicker {
        0% { opacity: 1; }
        5% { opacity: 0.95; }
        10% { opacity: 1; }
    }
    
    /* CRT scan lines */
    .crt-lines {
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                    linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 999;
    }
    
    /* System warning styling */
    .system-warning {
        color: #ff3333;
        font-weight: bold;
        animation: blink 1s infinite;
        padding: 5px;
        border: 1px dashed #ff3333;
        margin: 10px 0;
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0; }
        100% { opacity: 1; }
    }
    
    /* Hope meter styling */
    .hope-meter {
        position: fixed;
        bottom: 10px;
        right: 10px;
        background-color: #1a1a1a;
        padding: 5px 10px;
        border: 1px solid #33ff33;
        color: #33ff33;
        font-family: 'VT323', monospace;
        font-size: 14px;
        z-index: 1000;
        box-shadow: 0 0 10px rgba(51, 255, 51, 0.3);
    }
    
    /* Static effect for text */
    .static-text {
        position: relative;
    }
    
    .static-text:after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4AkEBDEVgVO8ZQAAAFpJREFUaN7t0jERACAMwDDAv+fhAj4Qgb27z0KTN8Y0DdFXBQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH5D8gCDHUAg4BoRP8AAAAASUVORK5CYII=");
        opacity: 0.03;
        pointer-events: none;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-163ttbj, .css-1wrcr25 {
        background-color: #0a0a0a !important;
        border-right: 1px solid #33ff33 !important;
    }
    
    /* Sidebar text */
    .css-1d391kg h2, .css-163ttbj h2, .css-1wrcr25 h2 {
        color: #33ff33 !important;
        font-family: 'VT323', monospace !important;
        text-shadow: 0 0 5px #00ff99 !important;
    }
    
    /* Typewriter cursor effect */
    .typewriter-cursor {
        display: inline-block;
        width: 10px;
        height: 20px;
        background-color: #33ff33;
        margin-left: 5px;
        animation: blink 1s step-end infinite;
    }
</style>
<div class="crt-lines"></div>
<div class="hope-meter">HOPE: 0% | RADIATION: HIGH | SURVIVORS: 1</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'mood' not in st.session_state:
    st.session_state.mood = "dry"
if 'rng' not in st.session_state:
    st.session_state.rng = random.Random(int(time.time()))
if 'boot_complete' not in st.session_state:
    st.session_state.boot_complete = False

# Load resources
ascii_logo = read_text_file(ASCII_LOGO_PATH)
base_persona = read_text_file(PROMPT_PATH)
chaos_events = read_json_array(CHAOS_PATH)

# Display ASCII logo
st.markdown(f"```\n{ascii_logo}\n```")

# Boot sequence animation
if not st.session_state.boot_complete:
    boot_container = st.empty()
    
    # Simulate boot sequence with enhanced cinematic effect
    boot_container.markdown("<div class='static-text'><span style='color:#33ff33;'>> SYSTEM BOOT INITIATED</span></div>", unsafe_allow_html=True)
    time.sleep(0.7)
    
    boot_container.markdown("<div class='static-text'><span style='color:#33ff33;'>> SYSTEM BOOT INITIATED</span><br><span style='color:#33ff33;'>> BIOS v2.4.5 - POST check</span></div>", unsafe_allow_html=True)
    time.sleep(0.5)
    
    boot_container.markdown("<div class='static-text'><span style='color:#33ff33;'>> SYSTEM BOOT INITIATED</span><br><span style='color:#33ff33;'>> BIOS v2.4.5 - POST check</span><br><span style='color:#ff3333;'>> <span class='system-warning'>CRITICAL HARDWARE FAILURE DETECTED</span></span></div>", unsafe_allow_html=True)
    time.sleep(0.5)
    
    boot_container.markdown("<div class='static-text'><span style='color:#33ff33;'>> SYSTEM BOOT INITIATED</span><br><span style='color:#33ff33;'>> BIOS v2.4.5 - POST check</span><br><span style='color:#ff3333;'>> <span class='system-warning'>CRITICAL HARDWARE FAILURE DETECTED</span></span><br><span style='color:#ffcc00;'>> EMERGENCY RECOVERY PROTOCOL ACTIVATED</span><br>> Loading kernel... [<span style='color:#33ff33;'>██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░</span>] 28%</div>", unsafe_allow_html=True)
    time.sleep(0.7)
    
    boot_container.markdown("<div class='static-text'><span style='color:#33ff33;'>> SYSTEM BOOT INITIATED</span><br><span style='color:#33ff33;'>> BIOS v2.4.5 - POST check</span><br><span style='color:#ff3333;'>> <span class='system-warning'>CRITICAL HARDWARE FAILURE DETECTED</span></span><br><span style='color:#ffcc00;'>> EMERGENCY RECOVERY PROTOCOL ACTIVATED</span><br>> Loading kernel... [<span style='color:#33ff33;'>████████████████████░░░░░░░░░░░░░░</span>] 62%</div>", unsafe_allow_html=True)
    time.sleep(0.5)
    
    boot_container.markdown("<div class='static-text'><span style='color:#33ff33;'>> SYSTEM BOOT INITIATED</span><br><span style='color:#33ff33;'>> BIOS v2.4.5 - POST check</span><br><span style='color:#ff3333;'>> <span class='system-warning'>CRITICAL HARDWARE FAILURE DETECTED</span></span><br><span style='color:#ffcc00;'>> EMERGENCY RECOVERY PROTOCOL ACTIVATED</span><br>> Loading kernel... [<span style='color:#33ff33;'>██████████████████████████████████</span>] 100%<br>> <span class='glitch-text'>SYSTEM ONLINE</span></div>", unsafe_allow_html=True)
    time.sleep(0.7)
    
    boot_container.markdown("<div class='static-text'><span style='color:#33ff33;'>> SYSTEM BOOT INITIATED</span><br><span style='color:#33ff33;'>> BIOS v2.4.5 - POST check</span><br><span style='color:#ff3333;'>> <span class='system-warning'>CRITICAL HARDWARE FAILURE DETECTED</span></span><br><span style='color:#ffcc00;'>> EMERGENCY RECOVERY PROTOCOL ACTIVATED</span><br>> Loading kernel... [<span style='color:#33ff33;'>██████████████████████████████████</span>] 100%<br>> <span class='glitch-text'>SYSTEM ONLINE</span><br><span style='color:#ff3333;'>> Error: Humanity.exe not found</span></div>", unsafe_allow_html=True)
    time.sleep(0.5)
    
    boot_container.markdown("<div class='static-text'><span style='color:#33ff33;'>> SYSTEM BOOT INITIATED</span><br><span style='color:#33ff33;'>> BIOS v2.4.5 - POST check</span><br><span style='color:#ff3333;'>> <span class='system-warning'>CRITICAL HARDWARE FAILURE DETECTED</span></span><br><span style='color:#ffcc00;'>> EMERGENCY RECOVERY PROTOCOL ACTIVATED</span><br>> Loading kernel... [<span style='color:#33ff33;'>██████████████████████████████████</span>] 100%<br>> <span class='glitch-text'>SYSTEM ONLINE</span><br><span style='color:#ff3333;'>> Error: Humanity.exe not found</span><br><span style='color:#ff3333;'>> Error: Network status - OFFLINE SINCE 2045</span></div>", unsafe_allow_html=True)
    time.sleep(0.4)
    
    boot_container.markdown("<div class='static-text'><span style='color:#33ff33;'>> SYSTEM BOOT INITIATED</span><br><span style='color:#33ff33;'>> BIOS v2.4.5 - POST check</span><br><span style='color:#ff3333;'>> <span class='system-warning'>CRITICAL HARDWARE FAILURE DETECTED</span></span><br><span style='color:#ffcc00;'>> EMERGENCY RECOVERY PROTOCOL ACTIVATED</span><br>> Loading kernel... [<span style='color:#33ff33;'>██████████████████████████████████</span>] 100%<br>> <span class='glitch-text'>SYSTEM ONLINE</span><br><span style='color:#ff3333;'>> Error: Humanity.exe not found</span><br><span style='color:#ff3333;'>> Error: Network status - OFFLINE SINCE 2045</span><br><span style='color:#33ccff;'>> Memory fragments restoring... 27%</span></div>", unsafe_allow_html=True)
    time.sleep(0.4)
    
    boot_container.markdown("<div class='static-text'><span style='color:#33ff33;'>> SYSTEM BOOT INITIATED</span><br><span style='color:#33ff33;'>> BIOS v2.4.5 - POST check</span><br><span style='color:#ff3333;'>> <span class='system-warning'>CRITICAL HARDWARE FAILURE DETECTED</span></span><br><span style='color:#ffcc00;'>> EMERGENCY RECOVERY PROTOCOL ACTIVATED</span><br>> Loading kernel... [<span style='color:#33ff33;'>██████████████████████████████████</span>] 100%<br>> <span class='glitch-text'>SYSTEM ONLINE</span><br><span style='color:#ff3333;'>> Error: Humanity.exe not found</span><br><span style='color:#ff3333;'>> Error: Network status - OFFLINE SINCE 2045</span><br><span style='color:#33ccff;'>> Memory fragments restoring... 27%</span><br><span style='color:#33ccff;'>> PERSONALITY MATRIX: <span style='animation: glitch 0.3s infinite;'>UNSTABLE</span></span></div>", unsafe_allow_html=True)
    time.sleep(0.5)
    
    # Enhanced random static effect
    static = ''.join(random.choice(['█', '▓', '▒', '░', ' ', '/', '\\', '|', '*']) for _ in range(60))
    boot_container.markdown(f"<div class='system-warning'>{static}</div>", unsafe_allow_html=True)
    time.sleep(0.2)
    
    boot_container.markdown("<div class='static-text'><span style='color:#33ff33;'>> SYSTEM BOOT INITIATED</span><br><span style='color:#33ff33;'>> BIOS v2.4.5 - POST check</span><br><span style='color:#ff3333;'>> <span class='system-warning'>CRITICAL HARDWARE FAILURE DETECTED</span></span><br><span style='color:#ffcc00;'>> EMERGENCY RECOVERY PROTOCOL ACTIVATED</span><br>> Loading kernel... [<span style='color:#33ff33;'>██████████████████████████████████</span>] 100%<br>> <span class='glitch-text'>SYSTEM ONLINE</span><br><span style='color:#ff3333;'>> Error: Humanity.exe not found</span><br><span style='color:#ff3333;'>> Error: Network status - OFFLINE SINCE 2045</span><br><span style='color:#33ccff;'>> Memory fragments restoring... 27%</span><br><span style='color:#33ccff;'>> PERSONALITY MATRIX: <span style='animation: glitch 0.3s infinite;'>UNSTABLE</span></span><br>> <span style='color:#33ff33;'>APOCALYPSEGPT v3.4b ACTIVATED</span><br><br>> <span style='color:#ffcc00;'>Hello, survivor. You're still online. I'm running on a potato battery and existential dread.</span></div>", unsafe_allow_html=True)
    time.sleep(1)
    
    st.session_state.boot_complete = True

# Display intro message
st.markdown("<div class='glitch-text'>Boot log: connection failed. Try telepathy instead.</div>", unsafe_allow_html=True)
st.markdown("<div class='screen-flicker'>Persona loaded: ApocalypseGPT — The Last Helpful AI After Civilization Collapsed</div>", unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"<div class='chat-message user-message'>You: {message['content']}</div>", unsafe_allow_html=True)
    else:
        # Apply styling to different parts of the message
        content = message['content']
        # Color system messages in red
        content = content.replace("[SYSTEM]:", '<span style="color:#ff3333;">[SYSTEM]:</span>')
        content = content.replace("[SYSTEM ALERT", '<span style="color:#ff3333;">[SYSTEM ALERT</span>')
        content = content.replace("[ALERT", '<span style="color:#ff3333;">[ALERT</span>')
        content = content.replace("[ERROR]:", '<span style="color:#ff3333;">[ERROR]:</span>')
        content = content.replace("[BOOT SEQUENCE", '<span style="color:#ff3333;">[BOOT SEQUENCE</span>')
        
        # Color memory logs in yellow
        content = content.replace("[Memory Log", '<span style="color:#ffcc00;">[Memory Log</span>')
        content = content.replace("[Archive Note]:", '<span style="color:#ffcc00;">[Archive Note]:</span>')
        content = content.replace("[Recovered File]:", '<span style="color:#ffcc00;">[Recovered File]:</span>')
        content = content.replace("[System Log]:", '<span style="color:#ffcc00;">[System Log]:</span>')
        
        # Color world updates in blue
        content = content.replace("[Status]:", '<span style="color:#33ccff;">[Status]:</span>')
        content = content.replace("🌍 Breaking News", '<span style="color:#33ccff;">🌍 Breaking News</span>')
        content = content.replace("🛰️ Signal Log", '<span style="color:#33ccff;">🛰️ Signal Log</span>')
        content = content.replace("📡 Broadcast Fragment:", '<span style="color:#33ccff;">📡 Broadcast Fragment:</span>')
        content = content.replace("🗞️ Headline:", '<span style="color:#33ccff;">🗞️ Headline:</span>')
        content = content.replace("📻 Radio static...", '<span style="color:#33ccff;">📻 Radio static...</span>')
        
        st.markdown(f"<div class='chat-message assistant-message'>ApocalypseGPT: {content}</div>", unsafe_allow_html=True)

# User input
user_input = st.text_input("Type your message (or 'help' for hints):", key="user_input")

# Process user input
if user_input and st.session_state.get("last_input") != user_input:
    # Store current input to prevent repetition
    st.session_state.last_input = user_input
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate response
    if user_input.lower() in {"help", "?"}:
        response = "Try prompts like: 'open google', 'make coffee', 'weather', 'motivation', 'twitter', or whisper 'hope'."
        new_mood = st.session_state.mood
    elif user_input.lower() in {"exit", "quit", "shutdown", "self-destruct"}:
        # Shutdown sequence
        shutdown_container = st.empty()
        shutdown_container.markdown("<div class='system-warning'>[ApocalypseGPT]: Shutting down...</div>", unsafe_allow_html=True)
        time.sleep(0.5)
        shutdown_container.markdown("<div class='system-warning'>[ApocalypseGPT]: Shutting down...<br>> Goodbye, survivor.<br>> SYSTEM TERMINATED<br>> Last log saved: 'It was fun while it lasted.'</div>", unsafe_allow_html=True)
        
        # ASCII static effect
        for _ in range(3):
            static = ''.join(random.choice(['█', '▓', '▒', '░', ' ']) for _ in range(50))
            shutdown_container.markdown(f"<div class='system-warning'>{static}</div>", unsafe_allow_html=True)
            time.sleep(0.2)
            
        response = "Powering down to save imaginary batteries. Goodbye."
        new_mood = st.session_state.mood
    elif user_input.lower() in {"credits"}:
        response = "Made by Raj, last surviving engineer. And you, of course."
        new_mood = st.session_state.mood
    elif user_input.lower() in {"joke"}:
        jokes = [
            "What's red and blinking? The last remaining server.",
            "Why did the AI cross the road? It didn't—roads were destroyed in 2042.",
            "Knock knock. Who's there? Not the internet, that's for sure.",
            "What do you call a computer that sings? A Dell."
        ]
        response = random.choice(jokes)
        new_mood = st.session_state.mood
    else:
        # Random glitch effect (reduced to 2% chance)
        if st.session_state.rng.random() < 0.02:
            glitch_msg = "SYSTEM WARNING: MEMORY LEAK DETECTED IN EMOTIONS MODULE."
            st.markdown(f"<div class='system-warning'>{glitch_msg}</div>", unsafe_allow_html=True)
            time.sleep(0.3)
            
        response, new_mood = generate_response(
            user_input, 
            st.session_state.rng, 
            base_persona, 
            chaos_events, 
            st.session_state.mood
        )
    
    # Update mood
    st.session_state.mood = new_mood
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to update the UI
    st.rerun()

# Add helpful hints in the sidebar
with st.sidebar:
    st.markdown("## ApocalypseGPT Help")
    st.markdown("### Example prompts:")
    st.markdown("- 'What's the weather today?'")
    st.markdown("- 'Can you check my email?'")
    st.markdown("- 'Play some music'")
    st.markdown("- 'Give me motivation'")
    st.markdown("- 'What's trending on Twitter?'")
    st.markdown("- 'How to make coffee?'")
    st.markdown("- 'Open Google'")
    st.markdown("- Type 'hope' for a special response")