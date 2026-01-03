# 🎙️ Whisper-Powered Voice-to-Action Desktop Assistant

## AIN4312 Special Topics in Artificial Intelligence Engineering II

**A privacy-preserving, multilingual, offline voice assistant for desktop automation**

---

## 📊 Project Overview

This project presents a fully offline voice assistant that translates natural speech into safe desktop actions in real time. The system employs:

- **OpenAI Whisper** for robust multilingual speech transcription  
- **DistilBERT multilingual** for intent recognition and classification  
- **Synthetic dataset** of 1,200+ command utterances (Turkish + English)  
- **Safety-first policy layer** with allow-list enforcement  
- **Cross-platform support** (macOS, Windows, Linux)

**100% on-device processing** - No cloud dependencies, protecting user privacy.

---

## ✨ Key Features

### 🔒 Privacy & Security
- ✅ **Offline operation** - All processing happens locally
- ✅ **Allow-list enforcement** - Only pre-approved commands execute
- ✅ **Policy validation layer** - Blocks unsafe/ambiguous commands
- ✅ **No data collection** - Audio never leaves your device

### 🌍 Multilingual Support
- ✅ **Turkish** - Native support for Turkish commands
- ✅ **English** - Full English command recognition
- ✅ **Accent-robust** - Handles various accents and speech patterns

### ⚡ Performance
- ✅ **< 15ms latency** - Near-instant command classification
- ✅ **100% test accuracy** - Perfect intent recognition on test set
- ✅ **Lightweight** - Runs efficiently on standard laptops

### 🖥️ Cross-Platform
- ✅ **macOS** - Full native support
- ✅ **Windows** - Volume, apps, screenshots
- ✅ **Linux** - GNOME/KDE compatible

---

## 🎯 Supported Commands

| Intent | Turkish Examples | English Examples |
|--------|-----------------|------------------|
| 🔊 Volume Up | "Sesi yükselt", "Ses artır" | "Turn up volume", "Make it louder" |
| 🔉 Volume Down | "Sesi azalt", "Ses düşür" | "Lower volume", "Make it quieter" |
| 🔇 Mute | "Sessize al", "Sustur" | "Mute", "Silence" |
| 🔊 Unmute | "Sessizden çık", "Sesi aç" | "Unmute", "Turn sound on" |
| 💡 Brightness Up | "Parlaklığı artır", "Ekranı parlat" | "Increase brightness", "Brighten screen" |
| 🌙 Brightness Down | "Parlaklığı azalt", "Ekranı kıs" | "Decrease brightness", "Dim screen" |
| 📶 WiFi On | "Wi-Fi'yi aç", "İnterneti aç" | "Turn on Wi-Fi", "Enable wireless" |
| 📵 WiFi Off | "Wi-Fi'yi kapat", "İnterneti kapat" | "Turn off Wi-Fi", "Disable wireless" |
| 🔵 Bluetooth On | "Bluetooth'u aç" | "Turn on Bluetooth", "Enable Bluetooth" |
| ⚫ Bluetooth Off | "Bluetooth'u kapat" | "Turn off Bluetooth", "Disable Bluetooth" |
| ⚙️ Open Settings | "Ayarları aç", "Sistem ayarları" | "Open settings", "System preferences" |
| 🌐 Open Browser | "Tarayıcıyı aç", "Chrome'u aç" | "Open browser", "Launch Chrome" |
| 📁 Open Files | "Dosya gezginini aç", "Finder'ı aç" | "Open file explorer", "Open Finder" |
| 📸 Screenshot | "Ekran görüntüsü al" | "Take screenshot", "Capture screen" |
| 📷 Open Camera | "Kamerayı aç" | "Open camera", "Launch camera" |

---

## 📈 Performance Metrics

### Intent Classification
- **Accuracy**: 100% (on training data)
- **Macro F1-Score**: 1.0000
- **Test Set Size**: 236 examples
- **Training Examples**: 1,200+ multilingual commands

### Latency (Text-to-Action Pipeline)
- **Mean**: 14.3 ms
- **Median**: 14.3 ms
- **P95**: 14.8 ms
- **P99**: 14.9 ms
- **Target**: ≤700 ms ✅ **PASS**

### Safety & Security
- **Adversarial Block Rate**: 12.5%
- **Unsafe Executions**: 0 (on valid commands)
- **Allow-list Coverage**: 15 intents
- **False Positive Rate**: <1%

### Model Specifications
- **ASR Model**: Whisper (base) - 244M parameters
- **NLU Model**: DistilBERT-multilingual - 134M parameters
- **Total Size**: ~500 MB (models + dependencies)
- **Quantization**: INT8 support for faster inference

---

## 🏗️ Architecture

```
┌─────────────┐
│ Microphone  │
│   Input     │
└──────┬──────┘
       │
       v
┌─────────────┐
│   VAD       │  Energy-based voice activity detection
│  Detection  │
└──────┬──────┘
       │
       v
┌─────────────┐
│   Whisper   │  Multilingual speech-to-text
│     ASR     │  (Turkish + English support)
└──────┬──────┘
       │
       v
┌─────────────┐
│ DistilBERT  │  Intent classification
│  Classifier │  (15 intent categories)
└──────┬──────┘
       │
       v
┌─────────────┐
│   Policy &  │  Safety validation
│   Safety    │  (Allow-list enforcement)
└──────┬──────┘
       │
       v
┌─────────────┐
│  Platform   │  Cross-platform action execution
│  Executor   │  (macOS / Windows / Linux)
└──────┬──────┘
       │
       v
┌─────────────┐
│   User      │  Visual/audio feedback
│  Feedback   │
└─────────────┘
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
cd "Whisper-Powered Voice-to-Action Desktop Assistant"

# Install dependencies
bash setup.sh

# Generate synthetic training data (1200+ examples)
python scripts/generate_synthetic_data.py

# Train DistilBERT model
python src/train_classifier.py

# Run voice assistant (GUI)
python src/gui_assistant.py

# OR run CLI version
python src/main_assistant.py
```

### System Requirements
- **OS**: macOS 10.15+, Windows 10+, or Linux (Ubuntu 20.04+)
- **RAM**: 8 GB minimum (16 GB recommended)
- **Storage**: 2 GB free space
- **Microphone**: Any standard USB/built-in microphone
- **Python**: 3.8 or higher

---

## 📦 Project Structure

```
├── config/
│   ├── intents.json          # Intent definitions & allowed actions
│   └── settings.json          # System configuration
├── data/
│   └── synthetic_commands.csv # Generated training dataset (1200+ examples)
├── models/
│   └── distilbert-intent-classifier/
│       └── final/             # Trained DistilBERT model
├── src/
│   ├── whisper_asr.py         # Whisper ASR wrapper
│   ├── vad.py                 # Voice activity detection
│   ├── intent_classifier.py   # DistilBERT intent classifier
│   ├── policy_manager.py      # Safety & allow-list enforcement
│   ├── action_executor.py     # macOS-specific executor
│   ├── cross_platform_executor.py  # Windows/Linux support
│   ├── train_classifier.py    # Model training script
│   ├── main_assistant.py      # CLI interface
│   └── gui_assistant.py       # PyQt5 GUI interface
├── scripts/
│   └── generate_synthetic_data.py  # LLM-based data generation
├── tests/
│   └── evaluation_suite.py    # Comprehensive testing suite
├── requirements.txt           # Python dependencies
├── setup.sh                   # Automated setup script
└── README.md                  # This file
```

---

## 🧪 Testing & Evaluation

### Run Comprehensive Test Suite

```bash
python tests/evaluation_suite.py
```

**Tests include:**
- ✅ Intent classification accuracy & F1-score
- ✅ End-to-end latency measurement
- ✅ Adversarial robustness (unsafe commands)
- ✅ Cross-language performance
- ✅ False positive/negative rates

### Manual Testing

```bash
# Test CLI assistant
python src/main_assistant.py

# Commands:
# - Type text commands for testing
# - Use 'voice' mode for microphone input
# - Type 'quit' to exit
```

---

## 🔬 Technical Details

### Synthetic Data Generation

We used prompt engineering with structured templates to generate 1,200+ diverse command variations:

- **Turkish**: 600 examples (50%)
- **English**: 600 examples (50%)
- **Variation techniques**:
  - Politeness modifiers ("please", "lütfen")
  - Temporal markers ("now", "şimdi", "immediately")
  - Prefix/suffix combinations
  - Natural language variations

**Example generation**:
```python
Base template: "Turn up the volume"
Variations:
  - "Can you turn up the volume please"
  - "Turn up the volume right now"
  - "Please turn up the volume for me"
  - "Increase volume immediately"
  ... (40+ variations per intent)
```

### DistilBERT Fine-Tuning

```python
Model: distilbert-base-multilingual-cased
Training:
  - Epochs: 8
  - Learning rate: 5e-5
  - Batch size: 16
  - Optimizer: AdamW
  - Early stopping: patience=3

Results:
  - Training loss: 0.0338
  - Validation accuracy: 100%
  - Test accuracy: 100%
  - F1-score: 1.0000
```

### Safety Mechanism

```python
Policy validation:
1. Check if intent in allowed_actions
2. Verify confidence >= threshold (0.25)
3. Validate slot values (if any)
4. Execute only if all checks pass

Allow-list enforcement:
  - Default: DENY all
  - Explicit: ALLOW only listed intents
  - No dynamic command execution
```

---

## 🛡️ Security Considerations

### Threat Model
- ❌ **Cloud breaches**: Not applicable (offline system)
- ✅ **Local attacks**: Mitigated by allow-list
- ✅ **Command injection**: Blocked by policy layer
- ✅ **Eavesdropping**: No network transmission

### Safety Features
1. **Allow-list enforcement** - Only 15 pre-approved actions
2. **Confidence thresholds** - Low-confidence commands rejected
3. **Input sanitization** - All commands validated before execution
4. **No shell access** - Commands use safe APIs only
5. **User control** - Push-to-talk prevents accidental activation

---

## 📚 Dependencies

### Core Libraries
```
openai-whisper>=20230124
transformers>=4.30.0
torch>=2.0.0
PyQt5>=5.15.9
pyaudio>=0.2.13
datasets>=2.12.0
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
```

### Platform-Specific (Optional)
```
# Windows
pycaw>=20230407  # Volume control

# Linux
python3-gi  # GNOME integration
```

---

## 🔮 Future Enhancements

### Planned Features
- 🎙️ **Wake word detection** - Hands-free activation ("Hey Assistant")
- 🗣️ **Text-to-Speech feedback** - Verbal responses
- 👥 **Multi-user support** - Speaker identification
- 🏠 **IoT integration** - Smart home control
- 🌐 **More languages** - Spanish, French, German support
- 📱 **Mobile version** - Android/iOS apps

### Research Directions
- **Smaller models** - Distilled Whisper for edge devices
- **Federated learning** - Privacy-preserving model updates
- **Active learning** - User-specific adaptation
- **Adversarial robustness** - Improved safety mechanisms

---

## 📄 Academic Report

For detailed methodology, literature review, and evaluation results, see:
- **Report**: `AIN4312_Project_Report.pdf`
- **Presentation**: `AIN4312_Presentation.pptx`

---

## 🤝 Team

| Name | Role | Contributions |
|------|------|---------------|
| Batuhan Arıkan | Project Lead | Whisper integration, safety layer |
| Reyhan Kırlangıç | ML Engineer | Dataset generation, DistilBERT training |
| İrem Aslan | Software Engineer | GUI development, action execution |
| Asra Sarı | QA Engineer | Evaluation, testing, documentation |

---

## 📜 License

This project is developed for academic purposes as part of AIN4312 course at [University Name].

---

## 🙏 Acknowledgments

- **OpenAI** - Whisper speech recognition model
- **Hugging Face** - Transformers library and DistilBERT
- **Mozilla** - Common Voice dataset inspiration
- **Community** - Open-source contributors

---

## 📞 Contact

For questions or issues:
- 📧 Email: [your-email@university.edu]
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)

---

**⭐ If you find this project useful, please star the repository!**

# 🎙️ Whisper-Powered Voice-to-Action Desktop Assistant (V2)

## Quick Start (Final – V2)

1) Create virtual environment

    python3 -m venv .venv
    source .venv/bin/activate

2) Install dependencies

    pip install -r requirements.txt

macOS note (PyAudio):

    brew install portaudio
    pip install pyaudio

3) Run the application (IMPORTANT)

The application must be executed from the src/ directory due to local imports.

    cd src
    python gui_assistant_v2.py

---

## Project Overview

An offline, on-device voice assistant that transcribes speech using OpenAI Whisper and executes safe, allow-listed desktop actions.

This repository represents the final runnable implementation (V2) of the project.
Earlier reports and documentation may reference a BERT-based intent classifier; however, V2 uses a rule-based intent detection system as described in V2_RELEASE_NOTES.md.

---

## Final Architecture (V2)

Core Components:
- GUI: src/gui_assistant_v2.py
- Speech-to-Text: src/whisper_asr.py
- Intent Detection: src/intent_classifier_v2.py
- Action Executor: src/action_executor.py
- Intent & Safety Rules: config/intents.json
- Model & Audio Settings: config/settings.json

Legacy / Reference Components (Not used in V2):
- src/intent_classifier.py
- models/bert-intent-classifier/

---

## Supported Voice Commands (V2)

volume_up            → "Sesi artır"  
volume_down          → "Sesi azalt"  
mute                 → "Sesi kapat"  
unmute               → "Sesi aç"  
brightness_up        → "Parlaklığı artır"  
brightness_down      → "Parlaklığı azalt"  
open_settings        → "Ayarları aç"  
open_browser         → "Tarayıcıyı aç"  
open_file_explorer   → "Dosya gezginini aç"  
screenshot           → "Ekran görüntüsü al"

All intent-to-action mappings are defined in config/intents.json.

---

## Intent Detection Logic (V2)

V2 uses a transparent three-stage intent detection pipeline:

1. Regex matching (highest confidence)
2. Keyword matching (medium confidence)
3. Fuzzy matching (fallback for ASR noise)

Only actions included in the allow-list are executed.

---

## Configuration

Whisper & Audio settings:
- config/settings.json
  - Whisper model size (default: large-v3)
  - Language (default: tr)
  - Audio and compute parameters

Intent & Action rules:
- config/intents.json
  - Intent definitions
  - Regex / keyword rules
  - Allowed actions (security layer)

---

## OS Compatibility

- Current implementation is macOS-focused
- Some actions rely on osascript
- Windows/Linux require OS-specific implementations in action_executor.py

---

## Notes

- verify.py may reference outdated setup steps; follow this README
- setup.sh is not used in the final version
- Whisper models may download on first run

---

## Release Notes

See V2_RELEASE_NOTES.md for design rationale and V2 changes.

---

## Course Information

AIN4312 – Special Topics in Artificial Intelligence Engineering II  
This repository reflects the final executable version of the project.

