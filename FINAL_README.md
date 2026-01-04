# Voice-to-Action Desktop Assistant

A privacy-focused, offline voice assistant that executes desktop commands using Turkish and English speech. Built for AIN4312 course project.


## What This Does

Speak a command in Turkish or English, and the assistant will:
- Control system settings (volume, brightness, WiFi, Bluetooth)
- Open applications (browser, file explorer, settings)
- Take screenshots, search Google/YouTube
- Control music playback (Spotify, Music app)
- Get system info (time, battery, disk space)

**Everything runs locally on your machine** - no internet required (except for downloading models initially).

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

**macOS users**: Install PyAudio dependencies first:
```bash
brew install portaudio
pip install pyaudio
```

### 2. Run the Application

```bash
cd src
python gui_assistant_v2.py
```

**Important**: You must run from the `src/` directory due to local imports.

### 3. Use the Assistant

1. Click "🎤 Dinlemeye Başla" (Start Listening)
2. Speak your command clearly
3. Wait for silence detection or 15 seconds
4. See the transcription and action execution

---

## How It Works

### Pipeline

```
Your Voice → Whisper (Speech-to-Text) → Intent Classifier → Action Executor
```

### Components

**Whisper ASR** (`whisper_asr.py`)
- Converts your speech to text
- Supports Turkish and English
- Uses OpenAI's Whisper large-v3 model
- First run will download ~3GB model automatically

**Intent Classifier V2** (`intent_classifier_v2.py`)
- Determines what you want to do
- Uses 3-stage matching:
  1. **Regex patterns** - Exact phrase matching (95% confidence)
  2. **Keyword matching** - Finds key words in your command (60-92% confidence)
  3. **Fuzzy matching** - Handles typos and ASR mistakes (60-75% confidence)

**Action Executor** (`action_executor.py`)
- Executes the actual command on your system
- Uses AppleScript on macOS, PowerShell on Windows
- 47 different actions supported

**Voice Activity Detection** (`vad.py`)
- Detects when you stop speaking
- Uses energy-based detection
- Automatically stops recording after silence

### Confidence System

- **≥60%**: Executes immediately
- **40-59%**: Asks for confirmation
- **<40%**: Rejects and asks you to try again

---

## Supported Commands

### System Controls
- "Sesi yükselt" / "Turn up volume"
- "Sesi azalt" / "Lower volume"
- "Sessize al" / "Mute"
- "Parlaklığı artır" / "Increase brightness"
- "Parlaklığı azalt" / "Decrease brightness"

### Network
- "Wi-Fi'yi aç" / "Turn on WiFi"
- "Wi-Fi'yi kapat" / "Turn off WiFi"
- "Bluetooth'u aç" / "Turn on Bluetooth"
- "Bluetooth'u kapat" / "Turn off Bluetooth"

### Applications
- "Tarayıcıyı aç" / "Open browser"
- "Ayarları aç" / "Open settings"
- "Dosya gezginini aç" / "Open file explorer"
- "Hesap makinesi aç" / "Open calculator"
- "Terminal aç" / "Open terminal"

### Media & Web
- "Spotify'dan müzik çal" / "Play music on Spotify"
- "Google'da ara [konu]" / "Search Google for [topic]"
- "YouTube'da ara [konu]" / "Search YouTube for [topic]"

### Utilities
- "Ekran görüntüsü al" / "Take screenshot"
- "Saat kaç" / "What time is it"
- "Pil kaç" / "Battery level"

**See full list**: Check `config/intents.json` for all 47 supported commands.

---

## Configuration

### Settings (`config/settings.json`)

```json
{
  "whisper": {
    "model_size": "large-v3",    // Model: tiny, base, small, medium, large-v3
    "language": "tr",             // Language: tr (Turkish), en (English)
    "device": "cpu"               // Device: cpu or cuda
  },
  "audio": {
    "sample_rate": 16000,         // Don't change
    "chunk_size": 1024            // Don't change
  }
}
```

**For faster performance** (lower accuracy):
- Change `model_size` to `"base"` or `"small"`
- First-time download will be smaller

### Intents (`config/intents.json`)

Defines all commands with:
- Keywords for matching
- Regex patterns
- Action mappings

**To add a new command**, edit this file and add the corresponding action to `action_executor.py`.

---

## Troubleshooting

### "Model not found" or slow first run
- Whisper downloads models on first use (~3GB for large-v3)
- Takes 5-10 minutes depending on internet speed
- Models cached in `~/.cache/whisper/`

### "Microphone not working"
- **macOS**: Grant microphone permission in System Settings → Privacy & Security
- **Windows**: Check microphone settings and permissions
- Test microphone in system settings first

### "Commands not recognized"
- Speak clearly and wait for the recording to finish
- Check the transcription shown in the GUI
- Try speaking louder if audio level is low (<0.01)
- Add more keywords to `config/intents.json`

### "Import errors" when running
- Make sure you're in the `src/` directory: `cd src`
- Virtual environment activated: `source .venv/bin/activate`
- All dependencies installed: `pip install -r requirements.txt`

### "Actions not executing"
- **macOS**: Some actions require external tools:
  - Brightness: Install `brightness` via Homebrew (optional)
  - Bluetooth: Install `blueutil` via Homebrew (optional)
- **Windows**: Most actions use built-in PowerShell commands
- Check the GUI output for specific error messages

### "SSL Certificate Error"
- If Whisper model download fails, check internet connection
- Try downloading manually from [Whisper GitHub](https://github.com/openai/whisper)

---

## Platform Support

### macOS (Primary)
- ✅ All features fully supported
- Uses AppleScript for system control

### Windows (Partial)
- ✅ Volume, brightness, WiFi
- ✅ App launching, screenshots
- ⚠️ Some features limited (Bluetooth, system info)

### Linux (Experimental)
- ⚠️ Not tested
- May work with GNOME/KDE modifications

---

## Project Structure

```
├── src/
│   ├── gui_assistant_v2.py       # Main GUI application (START HERE)
│   ├── whisper_asr.py             # Speech-to-text
│   ├── intent_classifier_v2.py   # Command understanding
│   ├── action_executor.py         # Action execution
│   └── vad.py                     # Voice activity detection
├── config/
│   ├── intents.json               # Command definitions
│   └── settings.json              # System settings
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## Technical Details

### Why V2 Instead of Machine Learning?

The project initially used a BERT-based classifier (V1) but switched to rule-based matching (V2) for:
- **Transparency**: See exactly why a command was recognized
- **Reliability**: No need to train models
- **Speed**: Instant classification (<15ms)
- **Simplicity**: Easier to debug and extend

See `V2_RELEASE_NOTES.md` for full explanation.

### Performance

- **Transcription**: ~2-4 seconds (depends on Whisper model size)
- **Classification**: <15ms
- **Total latency**: ~2-5 seconds from speech to action

### Privacy & Security

- **100% offline**: No data sent to cloud
- **No storage**: Audio deleted after processing
- **Allow-list**: Only 47 pre-approved actions can execute
- **Safe defaults**: Destructive actions (shutdown, restart) require confirmation

---

## For Developers

### Running Tests

```bash
python tests/evaluation_suite.py
```

Tests accuracy, latency, and adversarial robustness.

### Adding New Commands

1. Edit `config/intents.json`:
```json
"my_new_intent": {
  "keywords": ["keyword1", "keyword2"],
  "patterns": ["regex.*pattern"],
  "action": "my_action",
  "description": "Description in Turkish"
}
```

2. Add to `allowed_actions` list in same file

3. Implement in `action_executor.py`:
```python
def _my_action(self):
    # Your implementation
    return "Success message"

# Add to action_map in __init__:
self.action_map['my_action'] = self._my_action
```

### Project Dependencies

**Core**:
- `openai-whisper` - Speech recognition
- `PyQt5` - GUI framework
- `torch` - Whisper backend
- `numpy` - Audio processing

**Optional**:
- `transformers` - For V1 BERT classifier (not used in V2)
- `scikit-learn` - Evaluation metrics

---

## Course Information

**AIN4312** - Special Topics in Artificial Intelligence Engineering II

This is the final executable version (V2) of the course project.

---

## License

Academic project for educational purposes.

---

## Getting Help

1. Check the GUI output for detailed error messages
2. Review this README's troubleshooting section
3. Check `V2_RELEASE_NOTES.md` for V2-specific details
4. Verify all requirements are installed: `pip list`
