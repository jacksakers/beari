"""
Sentence Analyzer
Uses spaCy for NLP analysis and extracts sentence components
Includes tense detection, sentiment analysis, and pattern signature generation
"""

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available. Install with: pip install spacy")
    print("Then download model with: python -m spacy download en_core_web_sm")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: TextBlob not available. Install with: pip install textblob")

import json
import re


class SentenceAnalyzer:
    def __init__(self, vocab_manager, semantic_manager):
        self.vocab_manager = vocab_manager
        self.semantic_manager = semantic_manager
        
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                self.use_spacy = True
            except OSError:
                print("Warning: spaCy model not found. Using basic parsing.")
                print("Download with: python -m spacy download en_core_web_sm")
                self.use_spacy = False
        else:
            self.use_spacy = False
    
    def analyze(self, text):
        """
        Analyze a sentence and extract components
        Returns a structured analysis dict
        """
        if self.use_spacy:
            return self._analyze_with_spacy(text)
        else:
            return self._analyze_basic(text)
    
    def _analyze_with_spacy(self, text):
        """Use spaCy for advanced NLP analysis with abstraction"""
        doc = self.nlp(text)
        
        # Extract components
        subject = None
        verb = None
        verb_token = None
        target = None
        adjectives = []
        
        # Find subject (noun phrases with nsubj dependency)
        for token in doc:
            if token.dep_ in ["nsubj", "nsubj:pass"]:
                subject = token.text
            if token.pos_ == "VERB" and not verb:
                verb = token.lemma_
                verb_token = token
            if token.dep_ in ["dobj", "pobj", "attr"] and not target:
                target = token.text
            if token.pos_ == "ADJ":
                adjectives.append(token.text)
        
        # Determine sentence type
        sentence_type = self._get_sentence_type(text)
        
        # Tense detection
        tense = self._detect_tense(doc, verb_token)
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment(text)
        
        # Extract all content words for vocabulary check
        content_words = [token.text for token in doc 
                        if token.pos_ in ["NOUN", "VERB", "ADJ", "ADV"] 
                        and not token.is_stop]
        
        # Check for unknown words
        unknowns = self.vocab_manager.get_unknown_words(content_words)
        
        # Get semantic tags for key entities
        semantic_tags = self._get_semantic_tags(verb, target, adjectives)
        
        # Generate pattern signature
        signature = self._generate_signature(subject, verb, target, tense, semantic_tags)
        
        result = {
            "original": text,
            "subject": subject,
            "verb": verb,
            "target": target,
            "adjectives": adjectives,
            "type": sentence_type,
            "tense": tense,
            "sentiment": sentiment,
            "semantic_tags": semantic_tags,
            "signature": signature,
            "unknowns": unknowns,
            "all_tokens": [{"text": t.text, "pos": t.pos_, "dep": t.dep_} for t in doc]
        }
        
        self._print_analysis(result)
        return result
    
    def _analyze_basic(self, text):
        """Basic analysis without spaCy"""
        # Simple word extraction
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Try to find subject (usually first pronoun or noun)
        subject = words[0] if words else None
        
        # Try to find verb (look for common patterns)
        verb = None
        target = None
        for i, word in enumerate(words):
            if word in ['took', 'take', 'ate', 'eat', 'went', 'go', 'did', 'made', 'cooked', 'cook']:
                verb = word
                # Try to get target (noun after verb)
                if i + 1 < len(words):
                    target = words[i + 1]
                break
        
        # Get sentence type
        sentence_type = self._get_sentence_type(text)
        
        # Basic tense detection
        tense = self._detect_tense_basic(text, verb)
        
        # Basic sentiment
        sentiment = self._analyze_sentiment(text)
        
        # Check for unknown words
        unknowns = self.vocab_manager.get_unknown_words(words)
        
        # Get semantic tags
        semantic_tags = self._get_semantic_tags(verb, target, [])
        
        # Generate signature
        signature = self._generate_signature(subject, verb, target, tense, semantic_tags)
        
        result = {
            "original": text,
            "subject": subject,
            "verb": verb,
            "target": target,
            "adjectives": [],
            "type": sentence_type,
            "tense": tense,
            "sentiment": sentiment,
            "semantic_tags": semantic_tags,
            "signature": signature,
            "unknowns": unknowns,
            "all_tokens": []
        }
        
        self._print_analysis(result)
        return result
    
    def _get_sentence_type(self, text):
        """Determine if statement, question, or exclamation"""
        text = text.strip()
        if text.endswith('?'):
            return "QUESTION"
        elif text.endswith('!'):
            return "EXCLAMATION"
        else:
            return "STATEMENT"
    
    def _detect_tense(self, doc, verb_token):
        """Detect tense using spaCy morphological features"""
        if not verb_token:
            return "PRESENT"
        
        # Check for modal verbs indicating future
        for token in doc:
            if token.text.lower() in ['will', 'shall', 'going']:
                return "FUTURE"
        
        # Check verb tense from spaCy
        if verb_token.tag_ in ['VBD', 'VBN']:  # Past tense or past participle
            return "PAST"
        elif verb_token.tag_ in ['VBG', 'VBP', 'VBZ']:  # Present participle or present
            return "PRESENT"
        
        return "PRESENT"
    
    def _detect_tense_basic(self, text, verb):
        """Basic tense detection without spaCy"""
        text_lower = text.lower()
        
        # Future indicators
        if 'will' in text_lower or 'going to' in text_lower:
            return "FUTURE"
        
        # Past indicators
        if verb and verb.endswith('ed'):
            return "PAST"
        if any(word in text_lower for word in ['was', 'were', 'did', 'had']):
            return "PAST"
        
        return "PRESENT"
    
    def _analyze_sentiment(self, text):
        """Analyze sentiment polarity (-1 to 1)"""
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                return round(blob.sentiment.polarity, 2)
            except:
                pass
        
        # Fallback: simple positive/negative word counting
        positive_words = ['good', 'great', 'happy', 'love', 'nice', 'awesome', 'excellent', 'wonderful']
        negative_words = ['bad', 'sad', 'hate', 'terrible', 'awful', 'horrible', 'angry']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 0.5
        elif neg_count > pos_count:
            return -0.5
        return 0.0
    
    def _get_semantic_tags(self, verb, target, adjectives):
        """Extract semantic categories for key words"""
        tags = {}
        
        # Get verb category
        if verb:
            verb_cat = self.semantic_manager.get_category(verb)
            if verb_cat:
                tags['verb_category'] = verb_cat['category']
        
        # Get target category
        if target:
            target_cat = self.semantic_manager.get_category(target)
            if target_cat:
                tags['target_category'] = target_cat['category']
        
        return tags
    
    def _generate_signature(self, subject, verb, target, tense, semantic_tags):
        """
        Generate an abstract pattern signature like: SELF_PAST_FOOD
        This allows generalization across similar sentences
        """
        parts = []
        
        # Subject part
        if subject and subject.lower() in ['i', 'me', 'my']:
            parts.append("SELF")
        elif subject:
            parts.append("OTHER")
        else:
            parts.append("UNKNOWN")
        
        # Tense part
        parts.append(tense)
        
        # Verb category (if available)
        if 'verb_category' in semantic_tags:
            parts.append(semantic_tags['verb_category'])
        elif verb:
            parts.append("ACTION")
        
        # Target category (if available)
        if 'target_category' in semantic_tags:
            parts.append(semantic_tags['target_category'])
        elif target:
            parts.append("OBJECT")
        
        return "_".join(parts)
    
    def _print_analysis(self, result):
        """Print the analysis in a clear, formatted way"""
        print("\n" + "=" * 50)
        print("   EXTENDED ANALYSIS REPORT")
        print("=" * 50)
        print(f"Input: \"{result['original']}\"")
        print(f"Type: {result['type']}")
        print(f"Subject: {result['subject'] or 'N/A'}")
        print(f"Verb: {result['verb'] or 'N/A'}")
        print(f"Target: {result['target'] or 'N/A'}")
        print(f"Adjectives: {result['adjectives'] if result['adjectives'] else 'None'}")
        
        # New abstraction fields
        print(f"\n--- ABSTRACTION LAYER ---")
        print(f"Tense: {result.get('tense', 'N/A')}")
        sentiment_val = result.get('sentiment', 0)
        sentiment_label = "Positive" if sentiment_val > 0.1 else "Negative" if sentiment_val < -0.1 else "Neutral"
        print(f"Sentiment: {sentiment_val} ({sentiment_label})")
        
        if result.get('semantic_tags'):
            print(f"Semantic Tags: {result['semantic_tags']}")
        
        print(f"\n>>> PATTERN SIGNATURE:")
        print(f">>> {result.get('signature', 'N/A')}")
        print("-" * 50)
        
        if result.get('unknowns'):
            print(f"\n⚠️  Unknown words detected: {result['unknowns']}")
            print("These will need to be added to vocabulary...")
        else:
            print(f"\n✓ All words recognized")
        
        print("=" * 50 + "\n")
    
    def get_structure_json(self, analysis):
        """Convert analysis to JSON structure for database storage"""
        return json.dumps({
            "subject": analysis['subject'],
            "verb": analysis['verb'],
            "target": analysis['target'],
            "adjectives": analysis['adjectives'],
            "type": analysis['type']
        })
