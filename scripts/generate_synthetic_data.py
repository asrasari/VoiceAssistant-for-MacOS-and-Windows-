"""
Synthetic Dataset Generator
Uses LLM prompts to generate diverse multilingual command utterances.
"""

import json
import random
from pathlib import Path

# Intent definitions with English and Turkish examples
INTENTS = {
    "volume_up": {
        "turkish_templates": [
            "Sesi yükselt",
            "Sesi artır",
            "Ses seviyesini yükselt",
            "Daha yüksek ses",
            "Sesi biraz yükselt",
            "Müziğin sesini yükselt",
            "Ses çok düşük yükselt"
        ],
        "english_templates": [
            "Turn up the volume",
            "Increase volume",
            "Make it louder",
            "Volume up",
            "Raise the volume",
            "Turn the sound up",
            "Increase the sound level"
        ]
    },
    "volume_down": {
        "turkish_templates": [
            "Sesi azalt",
            "Sesi düşür",
            "Ses seviyesini azalt",
            "Daha sessiz yap",
            "Sesi biraz azalt",
            "Müziğin sesini azalt",
            "Ses çok yüksek azalt"
        ],
        "english_templates": [
            "Turn down the volume",
            "Decrease volume",
            "Make it quieter",
            "Volume down",
            "Lower the volume",
            "Turn the sound down",
            "Reduce the sound level"
        ]
    },
    "mute": {
        "turkish_templates": [
            "Sessize al",
            "Sesi kapat",
            "Sustur",
            "Sessiz mod",
            "Sesi tamamen kapat",
            "Mute yap"
        ],
        "english_templates": [
            "Mute",
            "Turn off sound",
            "Silence",
            "Mute the volume",
            "Turn off the audio",
            "Make it silent"
        ]
    },
    "unmute": {
        "turkish_templates": [
            "Sessizden çık",
            "Sesi aç",
            "Unmute yap",
            "Sessiz modu kapat",
            "Sesi geri getir"
        ],
        "english_templates": [
            "Unmute",
            "Turn on sound",
            "Restore sound",
            "Unmute the volume",
            "Turn the audio back on"
        ]
    },
    "brightness_up": {
        "turkish_templates": [
            "Parlaklığı artır",
            "Ekranı parlat",
            "Parlaklık yükselt",
            "Daha parlak yap",
            "Ekran parlaklığını artır",
            "Işığı artır"
        ],
        "english_templates": [
            "Increase brightness",
            "Make screen brighter",
            "Turn up brightness",
            "Brightness up",
            "Raise screen brightness",
            "Brighten the screen"
        ]
    },
    "brightness_down": {
        "turkish_templates": [
            "Parlaklığı azalt",
            "Ekranı kıs",
            "Parlaklık düşür",
            "Daha karanlık yap",
            "Ekran parlaklığını azalt",
            "Işığı azalt",
            "Parlaklığı kıs",
            "Parlaklıyı kıs",
            "Ekran kıs"
        ],
        "english_templates": [
            "Decrease brightness",
            "Make screen dimmer",
            "Turn down brightness",
            "Brightness down",
            "Lower screen brightness",
            "Dim the screen"
        ]
    },
    "wifi_on": {
        "turkish_templates": [
            "Wi-Fi'yi aç",
            "Kablosuz ağı aç",
            "WiFi'yi etkinleştir",
            "İnterneti aç",
            "Wi-Fi'yi aktif et"
        ],
        "english_templates": [
            "Turn on Wi-Fi",
            "Enable Wi-Fi",
            "Connect to Wi-Fi",
            "Wi-Fi on",
            "Activate Wi-Fi",
            "Turn wireless on"
        ]
    },
    "wifi_off": {
        "turkish_templates": [
            "Wi-Fi'yi kapat",
            "Kablosuz ağı kapat",
            "WiFi'yi devre dışı bırak",
            "İnterneti kapat",
            "Wi-Fi'yi kapat"
        ],
        "english_templates": [
            "Turn off Wi-Fi",
            "Disable Wi-Fi",
            "Disconnect Wi-Fi",
            "Wi-Fi off",
            "Deactivate Wi-Fi",
            "Turn wireless off"
        ]
    },
    "bluetooth_on": {
        "turkish_templates": [
            "Bluetooth'u aç",
            "Bluetooth'u etkinleştir",
            "Bluetooth'u aktif et",
            "Bluetooth aç"
        ],
        "english_templates": [
            "Turn on Bluetooth",
            "Enable Bluetooth",
            "Bluetooth on",
            "Activate Bluetooth",
            "Turn Bluetooth on"
        ]
    },
    "bluetooth_off": {
        "turkish_templates": [
            "Bluetooth'u kapat",
            "Bluetooth'u devre dışı bırak",
            "Bluetooth'u kapat",
            "Bluetooth kapat"
        ],
        "english_templates": [
            "Turn off Bluetooth",
            "Disable Bluetooth",
            "Bluetooth off",
            "Deactivate Bluetooth",
            "Turn Bluetooth off"
        ]
    },
    "open_settings": {
        "turkish_templates": [
            "Ayarları aç",
            "Sistem ayarlarını aç",
            "Ayarlar uygulamasını aç",
            "Ayarlara git"
        ],
        "english_templates": [
            "Open settings",
            "Open system settings",
            "Go to settings",
            "Launch settings",
            "Open preferences"
        ]
    },
    "open_browser": {
        "turkish_templates": [
            "Tarayıcıyı aç",
            "Chrome'u aç",
            "Chromu aç",
            "Google Chrome aç",
            "Safari'yi aç",
            "Safariyı aç",
            "Firefox aç",
            "İnternet tarayıcısını aç",
            "Tarayıcı aç",
            "Browser aç",
            "Web tarayıcısını aç"
        ],
        "english_templates": [
            "Open browser",
            "Open Chrome",
            "Open Google Chrome",
            "Launch Chrome",
            "Open Safari",
            "Launch Safari",
            "Open Firefox",
            "Launch browser",
            "Start web browser",
            "Open the browser"
        ]
    },
    "open_file_explorer": {
        "turkish_templates": [
            "Dosya gezginini aç",
            "Finder'ı aç",
            "Dosya yöneticisini aç",
            "Klasörleri aç"
        ],
        "english_templates": [
            "Open file explorer",
            "Open Finder",
            "Open file manager",
            "Launch file browser",
            "Show files"
        ]
    },
    "take_screenshot": {
        "turkish_templates": [
            "Ekran görüntüsü al",
            "Screenshot al",
            "Ekran görüntüsü çek",
            "Ekranı yakala"
        ],
        "english_templates": [
            "Take screenshot",
            "Capture screen",
            "Take a picture of screen",
            "Screenshot",
            "Capture screenshot"
        ]
    },
    "open_camera": {
        "turkish_templates": [
            "Kamerayı aç",
            "Kamera uygulamasını aç",
            "Kamerayı başlat"
        ],
        "english_templates": [
            "Open camera",
            "Launch camera",
            "Start camera",
            "Open camera app"
        ]
    }
}

# Politeness variations
TURKISH_VARIATIONS = [
    "",
    " lütfen",
    " şimdi",
    " hemen",
    " acilen",
    " biraz",
    " çabuk",
    " hızlıca"
]

ENGLISH_VARIATIONS = [
    "",
    " please",
    " now",
    " right now",
    " immediately",
    " quickly",
    " fast",
    " a bit"
]

# Prefix/suffix variations
TURKISH_PREFIXES = [
    "",
    "Bana ",
    "Lütfen ",
    "Şimdi ",
    "Hemen ",
    "Acilen "
]

TURKISH_SUFFIXES = [
    "",
    " yapabilir misin?",
    " yapar mısın?",
    " istiyorum",
    " gerek"
]

ENGLISH_PREFIXES = [
    "",
    "Can you ",
    "Please ",
    "Could you ",
    "Would you "
]

ENGLISH_SUFFIXES = [
    "",
    " please",
    " for me",
    " right now",
    " immediately"
]


def generate_variations(template, language="turkish"):
    """Generate multiple variations of a command template."""
    variations = []
    
    if language == "turkish":
        prefixes = TURKISH_PREFIXES
        suffixes = TURKISH_SUFFIXES
        mods = TURKISH_VARIATIONS
    else:
        prefixes = ENGLISH_PREFIXES
        suffixes = ENGLISH_SUFFIXES
        mods = ENGLISH_VARIATIONS
    
    # Base variations
    for mod in mods:
        variations.append(template + mod)
    
    # Prefix/suffix combinations
    for prefix in prefixes[:3]:  # Limit to avoid explosion
        for suffix in suffixes[:3]:
            if prefix or suffix:
                variations.append(prefix + template + suffix)
    
    return variations


def generate_synthetic_dataset(output_path, target_count=1200):
    """
    Generate synthetic dataset with balanced Turkish and English examples.
    
    Args:
        output_path: Path to save the generated CSV
        target_count: Target number of examples (will be slightly adjusted for balance)
    """
    print(f"Generating synthetic dataset with ~{target_count} examples...")
    
    all_examples = []
    intent_names = list(INTENTS.keys())
    examples_per_intent = target_count // len(intent_names)
    
    for intent_action, templates in INTENTS.items():
        # Map action back to Turkish intent name
        intent_map = {
            "volume_up": "Sesi yükselt",
            "volume_down": "Sesi azalt",
            "mute": "Sessize al",
            "unmute": "Sessizden çık",
            "brightness_up": "Parlaklığı artır",
            "brightness_down": "Parlaklığı azalt",
            "wifi_on": "Wi-Fi'yi aç",
            "wifi_off": "Wi-Fi'yi kapat",
            "bluetooth_on": "Bluetooth'u aç",
            "bluetooth_off": "Bluetooth'u kapat",
            "open_settings": "Ayarları aç",
            "open_browser": "Tarayıcıyı aç",
            "open_file_explorer": "Dosya gezginini aç",
            "take_screenshot": "Ekran görüntüsü al",
            "open_camera": "Kamerayı aç"
        }
        
        intent_name = intent_map[intent_action]
        
        # Generate Turkish examples
        turkish_examples = []
        for template in templates["turkish_templates"]:
            turkish_examples.extend(generate_variations(template, "turkish"))
        
        # Generate English examples
        english_examples = []
        for template in templates["english_templates"]:
            english_examples.extend(generate_variations(template, "english"))
        
        # Sample to get balanced distribution
        turkish_sample = random.sample(turkish_examples, 
                                      min(len(turkish_examples), examples_per_intent // 2))
        english_sample = random.sample(english_examples, 
                                      min(len(english_examples), examples_per_intent // 2))
        
        for example in turkish_sample:
            all_examples.append({
                "Adi": intent_name,
                "Sorgu": example,
                "Language": "Turkish",
                "Action": intent_action
            })
        
        for example in english_sample:
            all_examples.append({
                "Adi": intent_name,
                "Sorgu": example,
                "Language": "English",
                "Action": intent_action
            })
        
        print(f"  {intent_name}: {len(turkish_sample)} TR + {len(english_sample)} EN")
    
    # Shuffle examples
    random.shuffle(all_examples)
    
    # Write to CSV
    output_path = Path(output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Adi,Sorgu,Language,Action\n")
        for example in all_examples:
            # Escape commas in queries
            query = example["Sorgu"].replace('"', '""')
            f.write(f'{example["Adi"]},"{query}",{example["Language"]},{example["Action"]}\n')
    
    print(f"\n✓ Generated {len(all_examples)} examples")
    print(f"✓ Saved to: {output_path}")
    
    # Print statistics
    turkish_count = sum(1 for ex in all_examples if ex["Language"] == "Turkish")
    english_count = sum(1 for ex in all_examples if ex["Language"] == "English")
    print(f"\nLanguage distribution:")
    print(f"  Turkish: {turkish_count} ({turkish_count/len(all_examples)*100:.1f}%)")
    print(f"  English: {english_count} ({english_count/len(all_examples)*100:.1f}%)")
    
    return all_examples


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate dataset
    output_file = Path(__file__).parent.parent / "data" / "synthetic_commands.csv"
    output_file.parent.mkdir(exist_ok=True)
    
    generate_synthetic_dataset(output_file, target_count=1200)
