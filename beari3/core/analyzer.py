"""
Sentence Analyzer
Uses spaCy for NLP analysis and extracts sentence components
"""

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available. Install with: pip install spacy")
    print("Then download model with: python -m spacy download en_core_web_sm")

import json
import re


class SentenceAnalyzer:
    def __init__(self, vocab_manager):
        self.vocab_manager = vocab_manager
        
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
        """Use spaCy for advanced NLP analysis"""
        doc = self.nlp(text)
        
        # Extract components
        subject = None
        verb = None
        target = None
        adjectives = []
        
        # Find subject (noun phrases with nsubj dependency)
        for token in doc:
            if token.dep_ in ["nsubj", "nsubj:pass"]:
                subject = token.text
            if token.pos_ == "VERB" and not verb:
                verb = token.lemma_
            if token.dep_ in ["dobj", "pobj", "attr"] and not target:
                target = token.text
            if token.pos_ == "ADJ":
                adjectives.append(token.text)
        
        # Determine sentence type
        sentence_type = self._get_sentence_type(text)
        
        # Extract all content words for vocabulary check
        content_words = [token.text for token in doc 
                        if token.pos_ in ["NOUN", "VERB", "ADJ", "ADV"] 
                        and not token.is_stop]
        
        # Check for unknown words
        unknowns = self.vocab_manager.get_unknown_words(content_words)
        
        result = {
            "original": text,
            "subject": subject,
            "verb": verb,
            "target": target,
            "adjectives": adjectives,
            "type": sentence_type,
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
        for word in words:
            if word in ['took', 'take', 'ate', 'eat', 'went', 'go', 'did', 'made']:
                verb = word
                break
        
        # Get sentence type
        sentence_type = self._get_sentence_type(text)
        
        # Check for unknown words
        unknowns = self.vocab_manager.get_unknown_words(words)
        
        result = {
            "original": text,
            "subject": subject,
            "verb": verb,
            "target": None,
            "adjectives": [],
            "type": sentence_type,
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
    
    def _print_analysis(self, result):
        """Print the analysis in a clear, formatted way"""
        print("\n" + "=" * 30)
        print("   ANALYSIS REPORT")
        print("=" * 30)
        print(f"Input: \"{result['original']}\"")
        print(f"Type: {result['type']}")
        print(f"Subject: {result['subject'] or 'N/A'}")
        print(f"Verb: {result['verb'] or 'N/A'}")
        print(f"Target: {result['target'] or 'N/A'}")
        print(f"Adjectives: {result['adjectives'] if result['adjectives'] else 'None'}")
        
        if result['unknowns']:
            print(f"\n⚠️  Unknown words detected: {result['unknowns']}")
            print("These will need to be added to vocabulary...")
        else:
            print(f"\n✓ All words recognized")
        
        print("=" * 30 + "\n")
    
    def get_structure_json(self, analysis):
        """Convert analysis to JSON structure for database storage"""
        return json.dumps({
            "subject": analysis['subject'],
            "verb": analysis['verb'],
            "target": analysis['target'],
            "adjectives": analysis['adjectives'],
            "type": analysis['type']
        })
