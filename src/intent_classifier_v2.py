"""
Intent Classifier V2 - Robust Regex + Fuzzy Matching
Classifies Turkish voice commands with transparency and confidence scoring.
"""

import json
import re
from pathlib import Path
from difflib import SequenceMatcher


class IntentClassifierV2:
    def __init__(self, config_path=None):
        """
        Initialize the intent classifier with regex and fuzzy matching.
        
        Args:
            config_path: Path to intents configuration file
        """
        # Load intents configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "intents.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.intents_map = self.config.get('intents', {})
        self.precompile_patterns()
        
        print("[INFO] Loading classifier (Regex + Fuzzy Matching)...")
        print(f"[OK] {len(self.intents_map)} intents loaded")
    
    def precompile_patterns(self):
        """Precompile regex patterns for faster matching."""
        self.patterns = {}
        self.keywords = {}
        
        for intent_id, intent_data in self.intents_map.items():
            # Compile regex patterns
            patterns_list = intent_data.get('patterns', [])
            compiled = []
            for pattern in patterns_list:
                try:
                    compiled.append(re.compile(pattern, re.IGNORECASE))
                except re.error:
                    print(f"[WARN] Invalid pattern: {pattern}")
            
            self.patterns[intent_id] = compiled
            self.keywords[intent_id] = intent_data.get('keywords', [])
    
    def predict(self, text, return_confidence=True, return_details=False):
        """
        Predict intent for given text with transparency.
        
        Args:
            text: Input text (transcribed speech)
            return_confidence: Whether to return confidence scores
            return_details: Whether to return detailed matching info
            
        Returns:
            If return_details: {intent, confidence, method, matched_keywords}
            If return_confidence: (intent, confidence)
            Otherwise: intent
        """
        text = self._preprocess_text(text)
        # Normalize common ASR confusions and collapse repeated letters
        text = self._normalize_text(text)
        
        best_intent = None
        best_confidence = 0.0
        best_method = None
        best_matched = []
        
        # Stage 1: Regex pattern matching (highest priority)
        for intent_id, patterns_list in self.patterns.items():
            for pattern in patterns_list:
                if pattern.search(text):
                    confidence = 0.95  # High confidence for regex match
                    return self._format_result(
                        intent_id, confidence, "regex", [], 
                        return_confidence, return_details
                    )
        
        # Stage 2: Keyword matching (medium priority)
        for intent_id, keywords_list in self.keywords.items():
            matched_keywords = []

            # Require at least 50% of keywords to match
            required_matches = max(1, len(keywords_list) // 2)

            for keyword in keywords_list:
                kw = keyword.lower().strip()
                if not kw:
                    continue
                # Word-boundary match to avoid substring false-positives
                try:
                    if re.search(rf"\b{re.escape(kw)}\b", text):
                        matched_keywords.append(keyword)
                except re.error:
                    # fallback simple substring
                    if kw in text:
                        matched_keywords.append(keyword)

            if len(matched_keywords) >= required_matches:
                # Increase confidence when multiple keywords match
                keyword_match_ratio = len(matched_keywords) / max(1, len(keywords_list))
                confidence = min(0.92, 0.60 + (keyword_match_ratio * 0.32))
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_intent = intent_id
                    best_method = "keywords"
                    best_matched = matched_keywords
        
        # Stage 3: Fuzzy matching (lowest priority)
        if best_intent is None or best_confidence < 0.7:
            fuzzy_match = self._fuzzy_match(text)
            if fuzzy_match:
                intent_id, confidence = fuzzy_match
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_intent = intent_id
                    best_method = "fuzzy"
                    best_matched = []
        
        # If still no match, return unknown with confidence info
        if best_intent is None:
            return self._format_result(
                "unknown", 0.0, "none", [],
                return_confidence, return_details
            )
        
        return self._format_result(
            best_intent, best_confidence, best_method, best_matched,
            return_confidence, return_details
        )
    
    def _fuzzy_match(self, text, threshold=0.6):
        """
        Fuzzy match text against intent keywords.
        Strict matching: require at least 2 words to match.
        
        Returns:
            (intent_id, confidence) or None
        """
        words = text.split()
        if len(words) < 2:  # Require at least 2 words
            return None
        
        best_intent = None
        best_score = 0.0
        
        for intent_id, keywords_list in self.keywords.items():
            if len(keywords_list) < 2:
                continue  # Skip intents with too few keywords
            
            matched_count = 0
            for keyword in keywords_list:
                for word in words:
                    similarity = SequenceMatcher(None, word, keyword).ratio()
                    if similarity > threshold:
                        matched_count += 1
                        if similarity > best_score:
                            best_score = similarity
            
            # Require at least 50% keyword match
            keyword_match_ratio = matched_count / len(keywords_list)
            if keyword_match_ratio >= 0.5 and best_score > threshold:
                best_intent = intent_id
                break
        
        if best_intent and best_score > threshold:
            # Lower confidence for fuzzy matches
            confidence = min(0.65, best_score * 0.7)
            return (best_intent, confidence)
        
        return None

    def _normalize_text(self, text):
        """
        Normalize transcript by correcting likely ASR confusions using
        nearby intent keywords and fuzzy matching. Returns normalized text.
        """
        words = text.split()
        if not words:
            return text

        # Build flat keyword list per intent for quick checks
        normalized_words = list(words)
        # Quick phonetic substitutions for common ASR confusions
        phonetic_map = {
            'kiz': 'kıs',
            'kız': 'kıs',
            'kizik': 'kısık',
            'kis': 'kıs',
            'kisik': 'kısık',
            'kisa': 'kıs',
            'kısa': 'kıs'
        }
        # Apply simple word-boundary replacements first
        for k, v in phonetic_map.items():
            text = re.sub(rf'\b{k}\b', v, text)
        words = text.split()

        for intent_id, keywords_list in self.keywords.items():
            # Check if at least one keyword already appears (substring match)
            present = any(
                any(kw.lower() in w for w in words) or kw.lower() in text
                for kw in keywords_list
            )
            if not present:
                continue

            # If one keyword present, try to correct nearby words to other keywords
            for i, w in enumerate(words):
                w_low = w.lower()
                # skip if already matches a keyword
                if any(kw.lower() == w_low or kw.lower() in w_low for kw in keywords_list):
                    continue

                best_kw = None
                best_score = 0.0
                for kw in keywords_list:
                    score = SequenceMatcher(None, w_low, kw.lower()).ratio()
                    if score > best_score:
                        best_score = score
                        best_kw = kw

                # If similarity is reasonably high, and keyword length >=2, replace
                if best_score >= 0.6 and best_kw and len(best_kw) >= 2:
                    normalized_words[i] = best_kw

        return " ".join(normalized_words)
    
    def _format_result(self, intent_id, confidence, method, matched_kw, 
                      return_confidence, return_details):
        """Format the result based on requested output format."""
        
        # Get friendly name
        intent_data = self.intents_map.get(intent_id, {})
        intent_name = intent_data.get('description', intent_id)
        action = intent_data.get('action', None)
        
        if return_details:
            return {
                'intent': intent_id,
                'intent_name': intent_name,
                'action': action,
                'confidence': confidence,
                'method': method,
                'matched_keywords': matched_kw,
                'confidence_pct': f"{confidence*100:.0f}%"
            }
        
        if return_confidence:
            return (intent_id, confidence)
        
        return intent_id
    
    def _preprocess_text(self, text):
        """Preprocess text for classification."""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove common Turkish suffixes for better matching
        # (This helps with different verb forms)
        # Collapse repeated characters (ASR sometimes doubles letters):
        text = re.sub(r'(\w)\1{1,}', r'\1', text)

        replacements = [
            (r'ı$', ''),  # Remove ı ending
            (r'i$', ''),  # Remove i ending
            (r'y$', ''),  # Remove y ending
        ]

        for old, new in replacements:
            text = re.sub(old, new, text)
        
        return text
    
    def get_action_for_intent(self, intent_id):
        """Get the action associated with an intent."""
        if intent_id in self.intents_map:
            return self.intents_map[intent_id].get('action', None)
        return None
    
    def get_intent_description(self, intent_id):
        """Get the description for an intent."""
        if intent_id in self.intents_map:
            return self.intents_map[intent_id].get('description', intent_id)
        return "Bilinmeyen komut"


if __name__ == "__main__":
    # Test the classifier
    classifier = IntentClassifierV2()
    
    test_texts = [
        "sesi yükselt",
        "sesi azalt lütfen",
        "ayarları aç",
        "tarayıcıyı aç",
        "ekran görüntüsü al",
        "parlaklığı düşür",
        "sessize al",
        "bilinmeyen komut"
    ]
    
    print("\n[TEST] Testing V2 Classifier:\n")
    for text in test_texts:
        result = classifier.predict(text, return_details=True)
        print(f"[INPUT] Input: '{text}'")
        print(f"   Intent: {result['intent_name']} OK {result['confidence_pct']}")
        print(f"   Method: {result['method']}")
        if result['matched_keywords']:
            print(f"   Keywords: {', '.join(result['matched_keywords'])}")
        print()
