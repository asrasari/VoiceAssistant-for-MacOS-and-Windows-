"""
Intent Classifier Module
Classifies Turkish voice commands into predefined intents using a fine-tuned BERT model.
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import json
import os
from pathlib import Path


class IntentClassifier:
    def __init__(self, model_path=None, config_path=None):
        """
        Initialize the intent classifier.
        
        Args:
            model_path: Path to the fine-tuned model
            config_path: Path to intents configuration file
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load intents configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "intents.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.intents = list(self.config['intents'].keys())
        self.intent2id = {intent: i for i, intent in enumerate(self.intents)}
        self.id2intent = {i: intent for intent, i in self.intent2id.items()}
        
        # Load or initialize model
        self.model = None
        self.tokenizer = None
        
        if model_path is None:
            # Auto-detect model path
            project_root = Path(__file__).parent.parent
            model_path = project_root / "models" / "distilbert-intent-classifier" / "final"
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            print("⚠️  Model not found. Please train the model first using train_classifier.py")
            print(f"   Expected path: {model_path}")
    
    def load_model(self, model_path):
        """
        Load the fine-tuned model and tokenizer.
        
        Args:
            model_path: Path to the fine-tuned model
        """
        print(f"📥 Loading model from {model_path}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.model.to(self.device)
            self.model.eval()
            print("✅ Model and tokenizer loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("Using simple keyword-based classification instead...")
            self.model = None
            self.tokenizer = None
    
    def predict(self, text, return_confidence=True):
        """
        Predict intent for given text.
        
        Args:
            text: Input text (transcribed speech)
            return_confidence: Whether to return confidence scores
            
        Returns:
            If return_confidence: (intent, confidence)
            Otherwise: intent
        """
        if self.model is None:
            # Use simple keyword-based fallback
            return self._predict_fallback(text, return_confidence)
        
        # Preprocess text
        text = self._preprocess_text(text)
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=64,
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            confidence, pred_idx = torch.max(probs, dim=-1)
        
        intent = self.id2intent[pred_idx.item()]
        confidence_score = confidence.item()
        
        if return_confidence:
            return intent, confidence_score
        return intent
    
    def _predict_fallback(self, text, return_confidence=True):
        """Simple keyword-based classification when model is not available."""
        text = self._preprocess_text(text)
        
        # Simple keyword matching
        keywords = {
            'volume_up': ['ses', 'yükselt', 'louder'],
            'volume_down': ['ses', 'azalt', 'quieter', 'lower'],
            'brightness_up': ['parlaklık', 'artır', 'brighter'],
            'brightness_down': ['parlaklık', 'azalt', 'darker'],
            'wifi_on': ['wifi', 'aç', 'connect'],
            'bluetooth_on': ['bluetooth', 'aç'],
            'browser_open': ['browser', 'chrome', 'aç', 'firefox'],
            'file_explorer_open': ['file', 'explorer', 'aç', 'finder'],
            'screenshot': ['screenshot', 'görüntüsü', 'ekran']
        }
        
        best_match = 'unknown'
        best_score = 0.0
        
        for intent, keywords_list in keywords.items():
            if intent in self.intents:
                match_count = sum(1 for kw in keywords_list if kw in text)
                score = match_count / len(keywords_list) if keywords_list else 0
                if score > best_score:
                    best_score = score
                    best_match = intent
        
        if best_score == 0:
            best_match = self.intents[0] if self.intents else 'unknown'
            best_score = 0.1
        
        if return_confidence:
            return best_match, best_score
        return best_match
    
    def predict_top_k(self, text, k=3):
        """
        Predict top-k intents with confidence scores.
        
        Args:
            text: Input text
            k: Number of top predictions to return
            
        Returns:
            List of tuples (intent, confidence)
        """
        if self.model is None:
            return [("unknown", 0.0)]
        
        # Preprocess text
        text = self._preprocess_text(text)
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=64,
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            top_probs, top_indices = torch.topk(probs[0], k=min(k, len(self.intents)))
        
        results = [
            (self.id2intent[idx.item()], prob.item())
            for idx, prob in zip(top_indices, top_probs)
        ]
        
        return results
    
    def _preprocess_text(self, text):
        """Preprocess text for classification."""
        # Convert to lowercase and strip whitespace
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        return text
    
    def get_action_for_intent(self, intent):
        """Get the action associated with an intent."""
        if intent in self.config['intents']:
            return self.config['intents'][intent]['action']
        return None


if __name__ == "__main__":
    # Test the classifier
    classifier = IntentClassifier()
    
    test_texts = [
        "sesi yükselt lütfen",
        "parlaklığı azalt",
        "chrome'u aç",
        "ekran görüntüsü al"
    ]
    
    print("\n🧪 Testing classifier:\n")
    for text in test_texts:
        intent, conf = classifier.predict(text)
        action = classifier.get_action_for_intent(intent)
        print(f"Text: '{text}'")
        print(f"  → Intent: {intent} ({conf:.2%})")
        print(f"  → Action: {action}\n")
