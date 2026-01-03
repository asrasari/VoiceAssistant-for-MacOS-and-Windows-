#!/usr/bin/env python3
"""
Quick verification script to check if all components can be imported.
Run this after setup.sh to verify installation.
"""

import sys
from pathlib import Path

print("="*60)
print("🔍 Sistem Kontrolü Başlatılıyor...")
print("="*60)
print()

# Check Python version
print("1️⃣  Python versiyonu kontrol ediliyor...")
if sys.version_info < (3, 8):
    print("   ❌ Python 3.8+ gerekli!")
    sys.exit(1)
print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
print()

# Check required packages
print("2️⃣  Gerekli paketler kontrol ediliyor...")

required_packages = [
    ('numpy', 'NumPy'),
    ('torch', 'PyTorch'),
    ('transformers', 'HuggingFace Transformers'),
    ('whisper', 'OpenAI Whisper'),
    ('pyaudio', 'PyAudio'),
    ('PyQt5', 'PyQt5'),
]

all_packages_ok = True
for package, name in required_packages:
    try:
        __import__(package)
        print(f"   ✅ {name}")
    except ImportError:
        print(f"   ❌ {name} bulunamadı!")
        all_packages_ok = False

print()

if not all_packages_ok:
    print("❌ Bazı paketler eksik. Lütfen setup.sh scriptini çalıştırın.")
    sys.exit(1)

# Check project structure
print("3️⃣  Proje yapısı kontrol ediliyor...")

base_dir = Path(__file__).parent
required_dirs = [
    'src',
    'config',
    'models',
    'data',
]

required_files = [
    'config/intents.json',
    'config/settings.json',
    'src/whisper_asr.py',
    'src/intent_classifier.py',
    'src/policy_manager.py',
    'src/action_executor.py',
    'src/train_classifier.py',
    'src/main_assistant.py',
    'src/gui_assistant.py',
    'queries_tırnaksız (1).csv',
]

structure_ok = True

for dir_name in required_dirs:
    dir_path = base_dir / dir_name
    if dir_path.exists():
        print(f"   ✅ {dir_name}/")
    else:
        print(f"   ❌ {dir_name}/ bulunamadı!")
        structure_ok = False

for file_name in required_files:
    file_path = base_dir / file_name
    if file_path.exists():
        print(f"   ✅ {file_name}")
    else:
        print(f"   ❌ {file_name} bulunamadı!")
        structure_ok = False

print()

if not structure_ok:
    print("❌ Proje yapısında eksiklikler var!")
    sys.exit(1)

# Check if model is trained
print("4️⃣  Model kontrolü...")
model_path = base_dir / "models" / "bert-intent-classifier" / "final"

if model_path.exists():
    print(f"   ✅ Model eğitilmiş: {model_path}")
else:
    print(f"   ⚠️  Model henüz eğitilmemiş")
    print(f"      Model eğitmek için:")
    print(f"      python src/train_classifier.py")

print()

# Test imports
print("5️⃣  Modüller import ediliyor...")

sys.path.insert(0, str(base_dir / 'src'))

try:
    from whisper_asr import WhisperASR
    print("   ✅ whisper_asr")
except Exception as e:
    print(f"   ❌ whisper_asr: {e}")
    structure_ok = False

try:
    from intent_classifier import IntentClassifier
    print("   ✅ intent_classifier")
except Exception as e:
    print(f"   ❌ intent_classifier: {e}")
    structure_ok = False

try:
    from policy_manager import PolicyManager
    print("   ✅ policy_manager")
except Exception as e:
    print(f"   ❌ policy_manager: {e}")
    structure_ok = False

try:
    from action_executor import ActionExecutor
    print("   ✅ action_executor")
except Exception as e:
    print(f"   ❌ action_executor: {e}")
    structure_ok = False

try:
    from vad import VoiceActivityDetector
    print("   ✅ vad")
except Exception as e:
    print(f"   ❌ vad: {e}")
    structure_ok = False

print()
print("="*60)

if structure_ok and model_path.exists():
    print("✅ TÜM KONTROLLER BAŞARILI!")
    print()
    print("Sistemi çalıştırmak için:")
    print("  ./run.sh")
    print()
    print("veya:")
    print("  python src/gui_assistant.py")
elif structure_ok:
    print("⚠️  Kurulum tamam, ancak model eğitilmemiş!")
    print()
    print("Model eğitmek için:")
    print("  python src/train_classifier.py")
else:
    print("❌ Bazı problemler var!")
    print()
    print("Kurulum yapmak için:")
    print("  ./setup.sh")

print("="*60)
