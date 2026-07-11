# fantastic-journey

A voice-activated AI assistant named Jarvis that uses OpenAI or Google Gemini APIs.

## Features

- Voice input/output using speech recognition and text-to-speech
- Integration with OpenAI GPT-3.5-turbo or Google Gemini APIs
- Conversation history management
- Simple command-line interface

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Create a `.env` file or export these variables:
   ```
   OPENAI_API_KEY=your_openai_key_here
   GEMINI_API_KEY=your_gemini_key_here
   ```

3. **Set microphone device index:**
   Update `MIC_DEVICE_INDEX` in `config.py` if using a non-default microphone.

## Running

```bash
python main.py
```

## Exit commands

Say any of: "exit", "quit", "goodbye", or "stop" to end the conversation.

## Files

- `main.py` - Entry point
- `ai.py` - AI agent implementation (fixed: updated OpenAI client initialization and Gemini model)
- `voice.py` - Speech recognition and text-to-speech (fixed: improved error handling and timeouts)
- `config.py` - Configuration settings (fixed: default values for environment variables)
- `requirements.txt` - Python dependencies (fixed: added missing edge-tts and updated versions)

## Bugs Fixed

1. **ai.py**: Updated deprecated OpenAI API usage (`openai.ChatCompletion.create()` → `OpenAI().chat.completions.create()`)
2. **ai.py**: Changed Gemini model from `gemini-2.5-flash` to `gemini-1.5-flash` (correct available model)
3. **config.py**: Fixed environment variable defaults (empty string instead of `None`)
4. **voice.py**: Added proper exception handling for `RequestError` and `UnknownValueError`
5. **voice.py**: Added timeout parameters to `listen()` to prevent hanging
6. **requirements.txt**: Added missing `edge-tts` package and `google-generativeai` for Gemini API
