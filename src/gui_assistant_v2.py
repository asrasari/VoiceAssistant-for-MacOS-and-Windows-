"""
GUI Voice Assistant V2 - With Transparency & Feedback
Simple graphical interface with detailed feedback for each step.
"""

import sys
import numpy as np
import pyaudio
import threading
import time
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QHBoxLayout, QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QFont, QColor, QTextCursor

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from whisper_asr import WhisperASR
from intent_classifier_v2 import IntentClassifierV2
from action_executor import ActionExecutor
from vad import VoiceActivityDetector


class WorkerSignals(QObject):
    """Signals for worker thread."""
    status_update = pyqtSignal(str)
    # payload: (transcribed_text, result_dict, confirm_request)
    confirm_request = pyqtSignal(object)


class VoiceAssistantGUIV2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎙️ Sesli Asistan V2")
        self.setGeometry(100, 100, 700, 600)
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QPushButton { 
                border-radius: 8px; 
                border: none;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover { opacity: 0.9; }
            QTextEdit { 
                border-radius: 4px;
                border: 1px solid #ddd;
                background-color: white;
                font-family: Courier;
            }
            QLabel { color: #333; }
        """)
        
        # Initialize components
        self.signals = WorkerSignals()
        self.signals.status_update.connect(self.update_status)
        self.signals.confirm_request.connect(self._handle_confirm_request)
        
        self.init_assistant()
        self.init_ui()
        
        # Audio settings
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.is_listening = False
        self.audio = None
        self.stream = None
        self.audio_buffer = []
    
    def init_assistant(self):
        """Initialize assistant components."""
        print("Loading components...")
        # Initialize components individually so a failure in one
        # doesn't prevent others from being available. Ensure
        # `self.vad` exists as a fallback.
        self.status_text = "✅ Hazır"

        # ASR
        try:
            self.asr = WhisperASR()
        except Exception as e:
            print(f"[ERROR] ASR yuklenemedi: {e}")
            self.asr = None
            self.status_text = f"❌ ASR hata"

        # Classifier
        try:
            self.classifier = IntentClassifierV2()
        except Exception as e:
            print(f"[ERROR] Classifier yuklenemedi: {e}")
            self.classifier = None
            self.status_text = f"❌ Classifier hata"

        # Executor
        try:
            self.executor = ActionExecutor()
        except Exception as e:
            print(f"[ERROR] Executor yuklenemedi: {e}")
            self.executor = None
            self.status_text = f"❌ Executor hata"

        # VAD (always provide a fallback energy-based VAD)
        try:
            self.vad = VoiceActivityDetector()
        except Exception as e:
            print(f"[ERROR] VAD yuklenemedi: {e}. Varsayilan enerji tabanli VAD kullaniliyor.")
            # Create a minimal fallback VAD with the same interface
            class _FallbackVAD:
                def is_speech(self, chunk):
                    return np.sqrt(np.mean(np.array(chunk, dtype=np.float32) ** 2)) > 0.02
            self.vad = _FallbackVAD()

        print("[OK] Component initialization finished.")
    
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🎙️ Sesli Asistan V2")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Status
        self.status_label = QLabel(self.status_text)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Listen button
        button_layout = QHBoxLayout()
        self.listen_button = QPushButton("🎤 Dinlemeye Başla")
        self.listen_button.setFont(QFont("Arial", 14))
        self.listen_button.setMinimumHeight(60)
        self.listen_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.listen_button.clicked.connect(self.toggle_listening)
        button_layout.addWidget(self.listen_button)
        
        # Clear button
        clear_button = QPushButton("🗑️ Temizle")
        clear_button.setFont(QFont("Arial", 11))
        clear_button.setMinimumHeight(60)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        clear_button.clicked.connect(self.clear_results)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        # Results display with scroll
        results_label = QLabel("📋 İşlem Detayları:")
        results_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(results_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier", 9))
        self.results_text.setMinimumHeight(300)
        
        scroll.setWidget(self.results_text)
        layout.addWidget(scroll)
        
        central_widget.setLayout(layout)
    
    def toggle_listening(self):
        """Toggle listening state."""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """Start listening for voice commands."""
        self.is_listening = True
        self.listen_button.setText("🛑 Durdurmak İçin Tıkla")
        self.listen_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
        """)
        self.update_status("🎤 Dinleniyor...")
        self.log_message("🎤 Dinlemeye başlandı. Konuşabilirsiniz...")
        
        # Start audio in separate thread
        self.audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.audio_thread.start()
    
    def stop_listening(self):
        """Stop listening."""
        self.is_listening = False
        self.listen_button.setText("🎤 Dinlemeye Başla")
        self.listen_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
            }
        """)
        self.update_status("✅ Durduruldu")
        self.log_message("⏹️ Dinleme durduruldu.")
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
    
    def _audio_loop(self):
        """Audio recording and processing loop."""
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=None  # Use default device
            )
            
            self.log_message("🔊 Mikrofon açıldı.")
            
            # Listen for up to 15 seconds or until silence detected
            max_duration = 15  # seconds
            start_time = time.time()
            silence_count = 0
            audio_data = []
            speech_started = False
            
            while self.is_listening:
                try:
                    chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_chunk = np.frombuffer(chunk, dtype=np.float32)
                    
                    # Ensure array is mutable and correct dtype
                    audio_chunk = np.array(audio_chunk, dtype=np.float32)
                    audio_data.append(audio_chunk)
                    
                    # Check for silence
                    is_speech = self.vad.is_speech(audio_chunk)
                    
                    if is_speech:
                        silence_count = 0
                        speech_started = True
                    else:
                        silence_count += 1
                    
                    # Stop if silence detected after speech (2 seconds of silence)
                    if speech_started and silence_count > 20:  # 20 chunks ≈ 0.5s
                        self.log_message("⏹️ Sessizlik algılandı, işleniyor...")
                        break
                    
                    # Stop if max duration exceeded
                    if time.time() - start_time > max_duration:
                        self.log_message("⏹️ Maksimum süre aşıldı, işleniyor...")
                        break
                    
                except Exception as e:
                    self.log_message(f"❌ Ses kaydı hatası: {str(e)}")
                    break
            
            # Process audio only if we have meaningful data
            if audio_data and len(audio_data) > 5:  # At least 0.1s of audio
                audio_array = np.concatenate(audio_data)
                
                # Debug: show audio stats
                audio_rms = np.sqrt(np.mean(audio_array ** 2))
                self.log_message(f"📊 Audio level: {audio_rms:.3f}")
                
                if audio_rms > 0.01:  # Reasonable audio level
                    self._process_audio(audio_array)
                else:
                    self.log_message("❌ Ses seviyesi çok düşük. Mikrofonu kontrol et.")
            else:
                self.log_message("❌ Ses kaydı başarısız. Lütfen tekrar dene.")
            
            self.is_listening = False
            self.listen_button.setText("🎤 Dinlemeye Başla")
            self.listen_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                }
            """)
            
        except Exception as e:
            self.log_message(f"❌ Audio loop hatası: {str(e)}")
        
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.audio:
                self.audio.terminate()
    
    def _process_audio(self, audio_array):
        """Process recorded audio through ASR → Classifier → Executor."""
        try:
            # Step 1: Transcription
            self.log_message("🔄 Whisper ile işleniyor...")
            self.update_status("🔄 İşleniyor...")
            
            transcribed_text = self.asr.transcribe(audio_array)
            if not transcribed_text or transcribed_text.strip() == "":
                self.log_message("❌ Konuşma anlaşılamadı. Lütfen tekrar deneyin.")
                self.update_status("❌ Hata")
                return
            
            self.log_message(f"📝 Whisper Transkripsiyon: \"{transcribed_text}\"")
            
            # Step 2: Intent Classification
            self.log_message("🧠 Intent sınıflandırılıyor...")

            # Use classifier if available, otherwise fallback to lightweight keyword matcher
            if getattr(self, 'classifier', None) is not None:
                result = self.classifier.predict(transcribed_text, return_details=True)
            else:
                result = self._fallback_classify(transcribed_text)
            
            # Step 3: Display detailed result
            self.log_message("─" * 50)
            self.log_message(f"✅ SONUÇ:")
            self.log_message(f"   Intent: {result['intent_name']}")
            self.log_message(f"   Güven: {result['confidence_pct']}")
            self.log_message(f"   Yöntem: {result['method'].upper()}")
            
            if result['matched_keywords']:
                self.log_message(f"   Eşleşen Anahtar Kelimeler: {', '.join(result['matched_keywords'])}")
            
            self.log_message("─" * 50)
            
            # Step 4: Execute action with confirmation flow
            trigger_execute = False
            if result['intent'] != "unknown":
                conf = result['confidence']
                action = result['action']

                if conf >= 0.60:
                    trigger_execute = True
                elif conf >= 0.40:
                    # ask user to confirm
                    confirm_request = {'event': threading.Event(), 'answer': None}
                    self.signals.confirm_request.emit((transcribed_text, result, confirm_request))
                    self.log_message("💡 Onay bekleniyor (15s)...")
                    # wait up to 15 seconds
                    confirm_request['event'].wait(15)
                    if confirm_request.get('answer'):
                        trigger_execute = True
                    else:
                        self.log_message("❌ Kullanıcı onaylamadı veya zaman aşımı.")

            if trigger_execute:
                self.log_message(f"🚀 Aksiyon yürütülüyor: {action.upper()}")
                exec_res = self.executor.execute(action, transcribed_text)
                # executor.execute returns dict with 'success' and 'message' keys
                if isinstance(exec_res, dict):
                    success = exec_res.get('success', False)
                    message = exec_res.get('message', 'Unknown result')
                else:
                    # backwards compatibility: treat truthy as success and message as string
                    success = bool(exec_res)
                    message = str(exec_res)

                if success:
                    # Log executor's message for better feedback (e.g., time, screenshot path)
                    self.log_message(f"✅ Aksiyon başarıyla tamamlandı! — {message}")
                    self.update_status(f"✅ {result['intent_name']}")
                else:
                    self.log_message(f"⚠️ Aksiyon yürütülemedi: {message}")
                    self.update_status("⚠️ Aksiyon başarısız")
            else:
                if result['intent'] == "unknown" or result['confidence'] < 0.40:
                    self.log_message("[ERROR] Guven seviyesi dusuk (<%40). Tekrar deneyiniz.")
                    self.update_status("❌ Anlayamadım")
            
            self.log_message("")
            
        except Exception as e:
            self.log_message(f"❌ İşlem hatası: {str(e)}")
            self.update_status("❌ Hata oluştu")

    def _fallback_classify(self, text):
        """Simple keyword-based fallback classifier when the main classifier is unavailable.

        Returns a dict with the same keys used by the GUI flow.
        """
        try:
            from pathlib import Path
            import json

            cfg_path = Path(__file__).parent.parent / "config" / "intents.json"
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)

            intent_defs = cfg.get('intents', {})
            text_l = text.lower()

            best = None
            best_score = 0
            best_matches = []

            for intent_name, spec in intent_defs.items():
                keywords = spec.get('keywords', [])
                score = 0
                matches = []
                for kw in keywords:
                    kw_l = kw.lower()
                    if kw_l in text_l:
                        score += 1
                        matches.append(kw)
                if score > best_score:
                    best_score = score
                    best = (intent_name, spec)
                    best_matches = matches

            if best is None or best_score == 0:
                return {
                    'intent_name': 'unknown',
                    'intent': 'unknown',
                    'confidence': 0.0,
                    'confidence_pct': '0%',
                    'method': 'fallback',
                    'matched_keywords': [],
                    'action': None
                }

            intent_name, spec = best
            # Simple confidence: normalize by number of keywords (cap at 0.95)
            kw_count = max(1, len(spec.get('keywords', [])))
            confidence = min(0.95, best_score / kw_count)

            return {
                'intent_name': spec.get('description', intent_name),
                'intent': intent_name,
                'confidence': confidence,
                'confidence_pct': f"{int(confidence*100)}%",
                'method': 'fallback',
                'matched_keywords': best_matches,
                'action': spec.get('action')
            }
        except Exception:
            return {
                'intent_name': 'unknown',
                'intent': 'unknown',
                'confidence': 0.0,
                'confidence_pct': '0%',
                'method': 'fallback',
                'matched_keywords': [],
                'action': None
            }
    
    def log_message(self, message):
        """Add message to results text area."""
        cursor = self.results_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Color code messages
        if message.startswith("✅"):
            format = cursor.charFormat()
            format.setForeground(QColor("#27ae60"))
            cursor.setCharFormat(format)
        elif message.startswith("❌"):
            format = cursor.charFormat()
            format.setForeground(QColor("#e74c3c"))
            cursor.setCharFormat(format)
        elif message.startswith("⏹️") or message.startswith("🔄"):
            format = cursor.charFormat()
            format.setForeground(QColor("#3498db"))
            cursor.setCharFormat(format)
        else:
            format = cursor.charFormat()
            format.setForeground(QColor("#333"))
            cursor.setCharFormat(format)
        
        cursor.insertText(message + "\n")
        self.results_text.setTextCursor(cursor)
        self.results_text.ensureCursorVisible()

    def _handle_confirm_request(self, payload):
        """Show confirmation dialog on GUI thread. Payload: (transcribed_text, result, confirm_request)"""
        try:
            transcribed_text, result, confirm_request = payload
            intent_name = result.get('intent_name', result.get('intent'))
            conf_pct = result.get('confidence_pct', f"{result.get('confidence',0)*100:.0f}%")
            msg = (f"Whisper: \"{transcribed_text}\"\n\n"
                   f"Anladığım: {intent_name} ({conf_pct}).\n"
                   "Onaylıyor musunuz?")
            reply = QMessageBox.question(self, 'Onayla', msg,
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            confirm_request['answer'] = (reply == QMessageBox.Yes)
        except Exception as e:
            confirm_request['answer'] = False
        finally:
            # signal waiting thread
            try:
                confirm_request['event'].set()
            except Exception:
                pass
    
    def update_status(self, status):
        """Update status label."""
        self.status_label.setText(status)
    
    def clear_results(self):
        """Clear results text area."""
        self.results_text.clear()
        self.log_message("📋 Temizlendi.\n")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = VoiceAssistantGUIV2()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
