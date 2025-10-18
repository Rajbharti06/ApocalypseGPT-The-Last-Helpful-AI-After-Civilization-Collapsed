# ApocalypseGPT - Flask Web UI

A chaotic, broken, and emotionally funny AI chatbot that survived the apocalypse. Features a retro CRT-style interface with Ollama AI integration.

## 🚀 Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-username/ApocalypseGPT.git
cd ApocalypseGPT
```

### 2. Install Ollama (Recommended)
**Download and install Ollama first for smart AI responses:**

**Windows:**
- Download from https://ollama.ai/
- Run the installer
- Open Command Prompt or PowerShell

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 3. Download AI Model
**Choose your preferred model:**
```bash
# Recommended: Balanced performance
ollama pull mistral

# Alternatives:
ollama pull llama3.2        # More capable, larger
ollama pull phi3           # Faster, smaller
ollama pull codellama      # Best for code questions
```

### 4. Start Ollama Server
```bash
ollama serve
```
*Keep this running in a separate terminal*

### 5. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 6. Run ApocalypseGPT
```bash
python app_flask.py
```

### 7. Open Browser
Navigate to **http://localhost:5000** and start chatting!

## ✨ Features

- **Smart AI Responses**: Uses Ollama for intelligent, context-aware replies
- **Fallback System**: Rule-based responses when Ollama is unavailable
- **CRT-Style UI**: Retro terminal aesthetic with glitch effects
- **Input Clearing**: Message input clears automatically after sending
- **Typing Indicators**: Shows when AI is "thinking"
- **Conversation History**: Maintains context across messages
- **Glitch Effects**: Random screen flickers and visual distortions
- **Color-Coded Messages**: Different colors for user, AI, and system messages

## ⚙️ Configuration

Edit these settings in `app_flask.py`:

```python
# Ollama Configuration
OLLAMA_URL = "http://localhost:11434"   # Change if different host/port
MODEL_NAME = "mistral"                  # Your preferred model

# Flask Configuration  
app.run(debug=True, host="0.0.0.0", port=5000)  # Change port if needed
```

## 🔧 Troubleshooting

**Ollama Connection Issues:**
- Ensure `ollama serve` is running
- Check available models: `ollama list`
- Verify URL in `app_flask.py` matches your Ollama server

**Port Conflicts:**
- Change port in `app_flask.py`: `port=5001`
- Kill existing process: `netstat -ano | findstr :5000` (Windows)

**Model Not Found:**
- Download model: `ollama pull mistral`
- Update `MODEL_NAME` in `app_flask.py`

## 🎯 Fallback Mode

If Ollama is not available, ApocalypseGPT automatically falls back to entertaining rule-based responses, ensuring the app never appears broken or empty.

## 📁 Files Structure

- `app_flask.py` - Flask backend with Ollama integration
- `static/index.html` - CRT-style web interface  
- `chaos.json` - Random apocalypse status messages
- `requirements.txt` - Python dependencies

## 🎮 Usage Tips

- Try different conversation topics to see personality shifts
- Type "help" for built-in commands
- Watch for random glitch effects and status updates
- The AI remembers conversation context within the session

---

**Enjoy the chaos! 🔥🤖**

*"In a world where the internet died, at least the sarcasm survived."*

- `app_flask.py` - Flask backend with Ollama integration
- `static/index.html` - CRT-style web interface
- `chaos.json` - Random apocalypse status messages
- `requirements.txt` - Python dependencies

Enjoy the chaos! 🔥🤖