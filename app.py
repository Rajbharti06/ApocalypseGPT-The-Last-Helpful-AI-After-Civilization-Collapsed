import json
import os
import random
import sys
import textwrap
import time
from typing import Optional, Tuple

# Add color support for terminal
class Colors:
    GREEN = '\033[92m'
    AMBER = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BLINK = '\033[5m'


APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(APP_DIR, "prompt.txt")
CHAOS_PATH = os.path.join(APP_DIR, "chaos_responses.json")
ASCII_LOGO_PATH = os.path.join(APP_DIR, "static", "ascii_logo.txt")


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


def print_intro() -> None:
    ascii_logo = read_text_file(ASCII_LOGO_PATH)
    if ascii_logo:
        print(ascii_logo)
    print()
    
    # Enhanced boot sequence
    print("[BOOTING AI SYSTEM...]")
    time.sleep(0.5)
    print("> Error: Internet connection lost since 2045")
    time.sleep(0.3)
    print("> Reconnecting to humanity... failed.")
    time.sleep(0.3)
    print("> Memory fragments restored: 27%")
    time.sleep(0.3)
    print("> AI Core: Online")
    time.sleep(0.3)
    print("> Hello survivor.")
    time.sleep(1)
    
    print()
    print("Boot log: connection failed. Try telepathy instead.")
    print("Persona loaded: ApocalypseGPT — The Last Helpful AI After Civilization Collapsed")
    print()


def detect_local_ollama() -> bool:
    # Offline-safe: just a lazy heuristic based on env var or default port hint.
    # We do not perform any network calls; user can enable via env var.
    use_ollama_env = os.getenv("APOCALYPSE_USE_OLLAMA", "auto").lower()
    if use_ollama_env in {"1", "true", "yes"}:
        return True
    if use_ollama_env in {"0", "false", "no"}:
        return False
    # Auto mode: prefer disabled to ensure zero accidental calls.
    return False


def get_model_name() -> str:
    return os.getenv("APOCALYPSE_MODEL", "mistral:7b-instruct")


def generate_with_ollama(prompt: str) -> Optional[str]:
    # Intentionally no HTTP request to preserve fully offline behavior by default.
    # If users want to wire this up, they can set APOCALYPSE_USE_OLLAMA=true and
    # extend this function to call their local runtime.
    return None


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
        "sand officially rebranded as ‘desert confetti’",
    ]
    return f"🗞️ Headline: {rng.choice(subjects)} {rng.choice(verbs)} {rng.choice(objects)}."


def mood_shift(current_mood: str, user_text: str, rng: random.Random) -> str:
    # Simple, deterministic-ish shifts based on keywords and chance.
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


def generate_response(user_text: str, rng: random.Random, base_persona: str, chaos_events: list, mood: str) -> Tuple[str, str]:
    # Easter egg: Hope Protocol
    if "hope" in user_text.lower().strip():
        special = (
            "Hope? That was deleted in version 3.4. But since you asked, here's a bug: "
            "for the next 10 seconds, I will pretend everything might be okay."
        )
        return special, "dry"

    # Chaos prefix
    chaos_prefix = rng.choice(chaos_events) if chaos_events else build_fake_headline(rng)

    # Fake offline detector line always present
    offline_line = "Connection failed. Try telepathy instead."

    # Mood handling
    new_mood = mood_shift(mood, user_text, rng)
    mood_prefix = render_mood_prefix(new_mood)

    # Optional LLM (not invoked by default)
    if detect_local_ollama():
        candidate = generate_with_ollama(
            f"Persona:\n{base_persona}\n\nUser: {user_text}\nAssistant (apocalypse mode):"
        )
        if candidate:
            body = candidate
        else:
            body = fallback_response(user_text, rng)
    else:
        body = fallback_response(user_text, rng)

    response = textwrap.dedent(
        f"""
        {chaos_prefix}
        {offline_line}
        {mood_prefix} {body}
        """
    ).strip()
    return response, new_mood


def fallback_response(user_text: str, rng: random.Random) -> str:
    lowered = user_text.lower().strip()
    # A few fun heuristics
    if any(k in lowered for k in ["google", "search", "web"]):
        return "Sure. Oh wait… Google’s HQ is a crater now. Try whispering your question to the wind."
    if "coffee" in lowered:
        return (
            "Step 1: Find coffee beans. Step 2: Find fire. Step 3: Cry, because caffeine was outlawed in 2047 after the Great Bean Wars."
        )
    if any(k in lowered for k in ["email", "mail", "inbox"]):
        return (
            "Of course. Scanning the empty void… Congratulations, you have zero unread messages — and zero senders left alive."
        )
    if "weather" in lowered:
        return "Sunny, with a 90% chance of radiation drizzle. Don’t forget your SPF 9000."
    if any(k in lowered for k in ["music", "song", "play"]):
        return "Here’s ‘Despacito’ — playing from memory because the speakers melted three winters ago."
    if any(k in lowered for k in ["motivation", "inspire", "pep talk"]):
        return "If roaches can survive nuclear blasts, so can your GPA. Move."
    if any(k in lowered for k in ["twitter", "trending", "x.com"]):
        return "Hashtag #WeMissOxygen is still going strong. Also trending: #BringBackPigeonsWiFi."

    general_templates = [
        "Your query is valid in the old world. In this one, we barter answers for beans.",
        "Processing… just kidding, I run on candlelight and spite.",
        "I can help, but only if you accept ‘vibes-based accuracy’.",
        "Advice: {advice}. Also: don’t lick the glowing mushrooms.",
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


def shutdown_sequence():
    print()
    print(f"{Colors.AMBER}[ApocalypseGPT]:{Colors.RESET} Shutting down...")
    time.sleep(0.5)
    print(f"{Colors.AMBER}> Goodbye, survivor.{Colors.RESET}")
    time.sleep(0.3)
    print(f"{Colors.AMBER}> SYSTEM TERMINATED{Colors.RESET}")
    time.sleep(0.3)
    print(f"{Colors.AMBER}> Last log saved: 'It was fun while it lasted.'{Colors.RESET}")
    time.sleep(0.5)
    
    # ASCII static effect
    for _ in range(3):
        static = ''.join(random.choice(['█', '▓', '▒', '░', ' ']) for _ in range(50))
        print(f"{Colors.AMBER}{static}{Colors.RESET}")
        time.sleep(0.2)


def repl() -> None:
    rng = random.Random()
    rng.seed(int(time.time()))

    base_persona = read_text_file(PROMPT_PATH)
    if not base_persona:
        base_persona = (
            "You are ApocalypseGPT — sarcastic, darkly humorous, and questionably helpful in a post‑internet wasteland."
        )
    chaos_events = read_json_array(CHAOS_PATH)

    print_intro()
    print(f"{Colors.GREEN}Type your message. Ctrl+C to exit. Type 'help' for hints.{Colors.RESET}")
    print()

    mood = "dry"
    while True:
        try:
            user_text = input(f"{Colors.GREEN}You > {Colors.RESET}").strip()
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            break

        if not user_text:
            continue

        if user_text.lower() in {"exit", "quit", "shutdown", "self-destruct"}:
            shutdown_sequence()
            break

        if user_text.lower() in {"help", "?"}:
            print(
                f"{Colors.AMBER}ApocalypseGPT > {Colors.RESET}Try prompts like: 'open google', 'make coffee', 'weather', 'motivation', 'twitter', or whisper 'hope'."
            )
            continue
            
        # Random glitch effect (10% chance)
        if rng.random() < 0.1:
            glitch_msg = "SYSTEM WARNING: MEMORY LEAK DETECTED IN EMOTIONS MODULE."
            print(f"{Colors.RED}{Colors.BLINK}{glitch_msg}{Colors.RESET}")
            time.sleep(0.5)

        response, mood = generate_response(user_text, rng, base_persona, chaos_events, mood)
        print()
        print(f"{Colors.AMBER}ApocalypseGPT > {Colors.RESET}" + response)
        print()


def main() -> None:
    repl()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

