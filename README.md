# JARVIS Pro - Advanced AI Assistant

## Overview

JARVIS Pro is a production-ready AI assistant built with Python 3.12, featuring:

- **Multi-Model AI**: Gemini (primary) + OpenAI (backup) + Ollama (offline)
- **Advanced Memory**: SQLite-based with conversation history, tasks, knowledge base
- **Smart Search**: Web search, news, weather, Wikipedia integration
- **Voice Assistant**: Speech recognition, TTS, wake word detection
- **Computer Automation**: Apps, files, clipboard, system control
- **Vision System**: Screenshot, OCR, face detection, object detection
- **Modern GUI**: Dark-themed interface with chat, settings, memory viewer
- **Plugin System**: Extensible architecture for custom plugins
- **Offline Mode**: Works without internet using Ollama

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/alinawazgujjar77-ship-it/jarvis.git
cd jarvis
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 5. Run JARVIS Pro
```bash
python main.py              # GUI mode
python main.py --cli        # CLI mode
python main.py --voice      # Voice mode
python main.py --debug      # Debug mode
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# API Keys
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
SEARCH_API_KEY=your_key_here

# Voice
WAKE_WORD=jarvis
VOICE_NAME=en-US-GuyNeural

# Memory
MEMORY_DB_PATH=data/jarvis.db
MEMORY_MAX_ITEMS=100
MEMORY_TTL_DAYS=30

# Application
ASSISTANT_NAME=Jarvis
USER_NAME=User
DEBUG_MODE=0
```

## Features

### AI System
- Primary: Google Gemini (free tier available)
- Backup: OpenAI GPT-3.5
- Offline: Ollama (Mistral, Llama2, etc.)
- Automatic provider switching
- Context-aware responses

### Memory Management
- **Conversations**: Full chat history
- **Tasks**: Create, manage, complete tasks
- **Knowledge Base**: Store and search information
- **Key-Value Store**: Custom data storage
- **User Preferences**: Personalization

### Search Integration
- Google Web Search (via SerpAPI)
- News Search
- Weather Forecasts
- Wikipedia Summaries
- Smart query routing

### Voice Features
- Wake word detection ("Jarvis")
- Automatic microphone selection
- Edge TTS for natural speech
- Noise reduction
- Wake word customization

### Computer Automation
- Open/close applications
- File management
- Screenshot capture
- Clipboard operations
- Volume control
- Brightness adjustment
- System shutdown/restart/sleep/lock
- CPU, memory, disk monitoring
- Wi-Fi status

### Vision Capabilities
- Screenshot capture
- Camera frame capture
- OCR (Optical Character Recognition)
- Face detection
- Object detection
- Image analysis

### GUI Interface
- Modern dark theme
- Chat interface
- Memory viewer
- Settings panel
- System monitor
- Responsive design

### Plugin System
- Dynamic plugin loading
- Enable/disable plugins
- Plugin management
- Extensible architecture

## Project Structure

```
jarvis/
├── core/                    # Core systems
│   ├── config_manager.py   # Configuration
│   ├── logger.py           # Logging
│   ├── memory_manager.py   # SQLite memory
│   ├── ai_brain.py         # Multi-model AI
│   ├── voice_assistant.py  # Voice I/O
│   ├── search_engine.py    # Web search
│   └── command_handler.py  # System commands
├── gui/                     # GUI components
│   ├── gui.py              # Main interface
├── vision/                  # Vision system
│   └── vision_system.py     # Camera, OCR
├── automation/              # System automation
│   └── system_automation.py # System control
├── plugins/                 # Plugin system
│   └── plugin_manager.py    # Plugin loader
├── utils/                   # Utilities
│   ├── text_utils.py        # Text processing
│   └── file_utils.py        # File operations
├── tests/                   # Unit tests
│   └── test_jarvis.py       # Test suite
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── .env.example             # Configuration template
└── README.md                # This file
```

## Development

### Run Tests
```bash
pytest                      # Run all tests
pytest --cov               # With coverage report
pytest -v                  # Verbose output
```

### Code Quality
```bash
black .                    # Format code
flake8 .                   # Lint code
mypy .                     # Type checking
```

### Create Virtual Env and Install Dev Tools
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install black flake8 mypy pytest pytest-cov
```

## API Integration

### Google Gemini
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API key
3. Add to `.env`: `GEMINI_API_KEY=your_key`

### OpenAI
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create API key
3. Add to `.env`: `OPENAI_API_KEY=your_key`

### SerpAPI (Search)
1. Go to [SerpAPI](https://serpapi.com)
2. Create account and get API key
3. Add to `.env`: `SEARCH_API_KEY=your_key`

### Ollama (Offline)
1. Download from [ollama.ai](https://ollama.ai)
2. Install and run: `ollama run mistral`
3. Ensure `OLLAMA_URL=http://localhost:11434`

## Troubleshooting

### No microphone detected
1. Run: `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`
2. Update `MIC_DEVICE_INDEX` in `.env` with correct index

### AI model not responding
1. Check API keys in `.env`
2. Verify internet connection (or use Ollama offline)
3. Check logs in `logs/` directory

### GUI not starting
1. Try CLI mode: `python main.py --cli`
2. Install customtkinter: `pip install customtkinter`
3. Check for display server issues on Linux

### Memory database errors
1. Delete `data/jarvis.db` to reset
2. Database will be recreated automatically

## Performance Tips

- Use Ollama for offline mode (no API costs)
- Keep `MEMORY_MAX_ITEMS` reasonable (default 100)
- Enable wake word to reduce false positives
- Use CLI mode for faster startup
- Monitor logs for optimization opportunities

## Security Considerations

- Never commit `.env` files with real API keys
- Use environment variables for sensitive data
- Keep dependencies updated
- Review plugin code before installation
- Use strong microphone permissions

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

MIT License - See LICENSE file for details

## Support

- 📖 Documentation: See this README
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

## Changelog

### Version 2.0.0 (Pro Upgrade)
- Complete rewrite with type hints
- SQLite-based memory system
- Multi-model AI support
- Advanced search integration
- Vision system with OCR
- Modern GUI interface
- Plugin system
- Comprehensive testing
- Production-ready code

## Roadmap

### 2.1.0
- Advanced analytics
- Voice commands learning
- Custom wake word training

### 2.2.0
- Mobile app integration
- Cloud sync
- Multi-device support

### 2.3.0
- Email integration
- Calendar management
- Document processing

## Credits

Created with ❤️ by the JARVIS Team

Thanks to:
- Google Gemini API
- OpenAI
- Ollama
- SerpAPI
- Python community

---

**JARVIS Pro 2.0.0** - Your Intelligent Digital Assistant

Production Ready ✅ | Fully Featured ✅ | Well Tested ✅
