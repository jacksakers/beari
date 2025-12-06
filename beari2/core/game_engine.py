"""
Beari Game Engine - Conversation as Chess
Implements the scoring system for optimal response generation.

The engine treats every interaction as a "turn" in a game where
Beari aims to maximize a score based on:
- User Happiness (empathy)
- Knowledge Gain (learning)
- Flow & Continuity (conversation)
- Personality Bias (the "good" filter)
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import random


@dataclass
class ResponseCandidate:
    """A potential response with its metadata."""
    text: str
    candidate_type: str  # 'learner', 'empath', 'connector'
    score: float = 0.0
    score_breakdown: Dict[str, float] = None
    
    def __post_init__(self):
        if self.score_breakdown is None:
            self.score_breakdown = {}


class SentimentAnalyzer:
    """
    Simple rule-based sentiment analysis.
    Detects positive, negative, or neutral sentiment from user input.
    """
    
    # Sentiment word lists
    POSITIVE_WORDS = {
        'good', 'great', 'happy', 'love', 'like', 'wonderful', 'amazing',
        'excellent', 'beautiful', 'nice', 'awesome', 'fantastic', 'joy',
        'enjoy', 'pleased', 'glad', 'best', 'fun', 'excited', 'win', 'won',
        'success', 'perfect', 'brilliant', 'delighted', 'thrilled'
    }
    
    NEGATIVE_WORDS = {
        'bad', 'sad', 'hate', 'terrible', 'awful', 'horrible', 'angry',
        'upset', 'worried', 'afraid', 'scared', 'hurt', 'pain', 'lost',
        'fail', 'failed', 'wrong', 'poor', 'worst', 'disappointing',
        'frustrated', 'annoyed', 'tired', 'bored', 'lonely', 'sick'
    }
    
    INTENSIFIERS = {
        'very', 'really', 'extremely', 'so', 'quite', 'absolutely',
        'incredibly', 'terribly', 'awfully'
    }
    
    NEGATORS = {'not', "don't", "doesn't", "didn't", "won't", "can't", "never", "no"}
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of input text.
        
        Args:
            text: User input text
            
        Returns:
            Dictionary with sentiment label and score
        """
        words = text.lower().split()
        
        positive_count = 0
        negative_count = 0
        intensity = 1.0
        negated = False
        
        for i, word in enumerate(words):
            # Check for negation
            if word in self.NEGATORS:
                negated = True
                continue
            
            # Check for intensifiers
            if word in self.INTENSIFIERS:
                intensity = 1.5
                continue
            
            # Count sentiment words (flip if negated)
            if word in self.POSITIVE_WORDS:
                if negated:
                    negative_count += intensity
                else:
                    positive_count += intensity
                negated = False
                intensity = 1.0
                
            elif word in self.NEGATIVE_WORDS:
                if negated:
                    positive_count += intensity
                else:
                    negative_count += intensity
                negated = False
                intensity = 1.0
        
        # Calculate overall sentiment
        total = positive_count + negative_count
        if total == 0:
            return {'label': 'neutral', 'score': 0.0, 'positive': 0, 'negative': 0}
        
        score = (positive_count - negative_count) / max(total, 1)
        
        if score > 0.2:
            label = 'positive'
        elif score < -0.2:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'label': label,
            'score': score,
            'positive': positive_count,
            'negative': negative_count
        }


class GameEngine:
    """
    The Conversation Game Engine.
    
    Treats conversation as a game where each response is a "move"
    and aims to maximize a utility function based on:
    - User Happiness
    - Knowledge Gain
    - Conversation Flow
    - Personality constraints
    """
    
    # Scoring weights
    DEFAULT_WEIGHTS = {
        'happiness': 1.5,
        'knowledge': 2.0,
        'flow': 1.0
    }
    
    # Personality keywords
    EVIL_WORDS = {'hate', 'hurt', 'kill', 'destroy', 'stupid', 'ugly', 'die'}
    GOOD_WORDS = {'help', 'good', 'friend', 'happy', 'love', 'care', 'kind'}
    
    # Flow indicators
    QUESTION_MARKERS = {'?', 'what', 'how', 'why', 'when', 'where', 'who', 'which'}
    DEAD_END_RESPONSES = {'okay', 'ok', 'yes', 'no', 'sure', 'fine', 'alright'}
    
    # Empathy templates
    EMPATHY_POSITIVE = [
        "That's wonderful! {continuation}",
        "I'm so glad to hear that! {continuation}",
        "That sounds great! {continuation}",
        "How exciting! {continuation}",
    ]
    
    EMPATHY_NEGATIVE = [
        "I'm sorry to hear that. {continuation}",
        "That sounds difficult. {continuation}",
        "I understand that must be hard. {continuation}",
        "I'm here with you. {continuation}",
    ]
    
    EMPATHY_NEUTRAL = [
        "I see. {continuation}",
        "Interesting! {continuation}",
        "Tell me more. {continuation}",
    ]
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize the game engine.
        
        Args:
            weights: Optional custom scoring weights
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Game state
        self.total_score = 0
        self.turn_count = 0
        self.score_history = []
    
    def evaluate_move(self, candidate: ResponseCandidate, 
                      user_sentiment: Dict, 
                      has_gap_opportunity: bool,
                      context_objects: List[str] = None,
                      is_question_input: bool = False) -> float:
        """
        Calculate the score for a response candidate.
        
        Uses the utility function:
        S = (W_h × Happiness) + (W_k × Knowledge) + (W_f × Flow) + PersonalityBias
        
        Args:
            candidate: The response candidate to evaluate
            user_sentiment: Sentiment analysis of user input
            has_gap_opportunity: Whether there's a knowledge gap to fill
            context_objects: Objects mentioned in conversation
            is_question_input: Whether the user asked a question
            
        Returns:
            Total score for this candidate
        """
        score_breakdown = {}
        
        # 1. Personality Check - The "Evil" Penalty
        evil_penalty = self._check_evil(candidate.text)
        if evil_penalty < 0:
            candidate.score = evil_penalty
            candidate.score_breakdown = {'evil_penalty': evil_penalty}
            return evil_penalty
        
        # 2. Happiness Score
        happiness = self._calculate_happiness(candidate.text, user_sentiment)
        score_breakdown['happiness'] = happiness * self.weights['happiness']
        
        # 3. Knowledge Score
        knowledge = self._calculate_knowledge(candidate.text, has_gap_opportunity)
        score_breakdown['knowledge'] = knowledge * self.weights['knowledge']
        
        # 4. Flow Score
        flow = self._calculate_flow(candidate.text)
        score_breakdown['flow'] = flow * self.weights['flow']
        
        # 5. Personality Bonus (the "Good" bias)
        personality = self._calculate_personality_bonus(candidate.text)
        score_breakdown['personality'] = personality
        
        # 6. Answerer Bonus - prioritize answering questions
        if is_question_input and candidate.candidate_type == 'answerer':
            score_breakdown['answerer_bonus'] = 15  # High priority to answer questions
        
        # Calculate total
        total = sum(score_breakdown.values())
        
        candidate.score = total
        candidate.score_breakdown = score_breakdown
        
        return total
    
    def _check_evil(self, text: str) -> float:
        """
        Check for "evil" content that should be banned.
        
        Args:
            text: Response text to check
            
        Returns:
            Large negative penalty if evil detected, 0 otherwise
        """
        words = set(text.lower().split())
        evil_found = words & self.EVIL_WORDS
        
        if evil_found:
            return -1000.0
        return 0.0
    
    def _calculate_happiness(self, text: str, user_sentiment: Dict) -> float:
        """
        Calculate happiness contribution.
        
        Matches empathetic responses to user sentiment.
        
        Args:
            text: Response text
            user_sentiment: User's detected sentiment
            
        Returns:
            Happiness score (0-10)
        """
        text_lower = text.lower()
        user_label = user_sentiment.get('label', 'neutral')
        
        # Check if response is appropriately empathetic
        empathy_score = 0
        
        if user_label == 'negative':
            # Look for supportive language
            supportive_words = {'sorry', 'understand', 'difficult', 'hard', 'hope', 'better', 'here for you'}
            for word in supportive_words:
                if word in text_lower:
                    empathy_score += 3
            
        elif user_label == 'positive':
            # Look for celebratory language
            celebratory_words = {'great', 'wonderful', 'glad', 'excited', 'congratulations', 'amazing'}
            for word in celebratory_words:
                if word in text_lower:
                    empathy_score += 3
        
        return min(empathy_score, 10)  # Cap at 10
    
    def _calculate_knowledge(self, text: str, has_gap: bool) -> float:
        """
        Calculate knowledge gain contribution.
        
        Questions about gaps score highly.
        
        Args:
            text: Response text
            has_gap: Whether there's a knowledge gap available
            
        Returns:
            Knowledge score (0-10)
        """
        score = 0
        
        # Asking a question is valuable for learning
        if '?' in text:
            score += 5
            
            # Even more valuable if there's a gap to fill
            if has_gap:
                score += 5
        
        return score
    
    def _calculate_flow(self, text: str) -> float:
        """
        Calculate flow/continuity contribution.
        
        Responses that keep conversation going score higher.
        
        Args:
            text: Response text
            
        Returns:
            Flow score (-5 to 10)
        """
        score = 0
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        # Dead end penalty
        if text_lower in self.DEAD_END_RESPONSES or len(words) <= 2:
            score -= 5
        
        # Question bonus (keeps conversation going)
        if text.endswith('?'):
            score += 5
        
        # Elaboration bonus (longer responses tend to be more engaging)
        if len(words) > 10:
            score += 2
        
        # Connection phrases bonus
        connection_phrases = ['reminds me', 'speaking of', 'that makes me think', 'related to']
        for phrase in connection_phrases:
            if phrase in text_lower:
                score += 3
                break
        
        return score
    
    def _calculate_personality_bonus(self, text: str) -> float:
        """
        Calculate personality bonus for "good" content.
        
        Args:
            text: Response text
            
        Returns:
            Personality bonus (0-5)
        """
        words = set(text.lower().split())
        good_found = words & self.GOOD_WORDS
        
        return len(good_found) * 2  # +2 per good word
    
    def generate_candidates(self, user_input: str, 
                           parsed: Dict,
                           gap_field: Optional[str],
                           gap_object: Optional[Any],
                           related_objects: List[Any] = None,
                           answer_result: Optional[Dict] = None) -> List[ResponseCandidate]:
        """
        Generate response candidates from different strategies.
        
        Creates different types based on input:
        - For questions: Answerer, then Elaborator or Learner
        - For statements: Learner, Empath, Connector
        - Connector: Connects to related objects
        
        Args:
            user_input: Original user input
            parsed: Parsed sentence components
            gap_field: Missing field name (if any)
            gap_object: Object with gap (if any)
            related_objects: Other objects that could be mentioned
            answer_result: Result from QuestionAnswerer (if user asked a question)
            
        Returns:
            List of ResponseCandidate objects
        """
        candidates = []
        user_sentiment = self.sentiment_analyzer.analyze(user_input)
        sentence_type = parsed.get('sentence_type', 'statement')
        
        # If user asked a question, prioritize answering
        if sentence_type == 'question' and answer_result:
            answerer = self._generate_answerer_candidate(answer_result, parsed, gap_field, gap_object)
            if answerer:
                candidates.append(answerer)
        
        # Candidate A: The Learner (asks about gaps)
        learner = self._generate_learner_candidate(gap_field, gap_object)
        if learner:
            candidates.append(learner)
        
        # Candidate B: The Empath
        empath = self._generate_empath_candidate(user_sentiment, gap_field, gap_object)
        candidates.append(empath)
        
        # Candidate C: The Connector
        connector = self._generate_connector_candidate(parsed, related_objects)
        if connector:
            candidates.append(connector)
        
        # Candidate D: The Elaborator (for statements, provides more info)
        if sentence_type == 'statement':
            elaborator = self._generate_elaborator_candidate(parsed, related_objects)
            if elaborator:
                candidates.append(elaborator)
        
        return candidates
    
    def _generate_answerer_candidate(self, answer_result: Dict, parsed: Dict,
                                     gap_field: Optional[str] = None,
                                     gap_object: Optional[Any] = None) -> Optional[ResponseCandidate]:
        """
        Generate a response that answers the user's question.
        Combines the answer with a follow-up (elaboration or question).
        """
        if not answer_result:
            return None
        
        answer_text = answer_result.get('answer', '')
        answered = answer_result.get('answered', False)
        confidence = answer_result.get('confidence', 0)
        
        # Build response: answer + follow-up
        follow_up = ''
        
        if answered and confidence > 0.5:
            # We answered successfully, add elaboration or ask about related gap
            if gap_field and gap_object:
                from core.question_generator import generate_question
                word = gap_object.word if hasattr(gap_object, 'word') else str(gap_object)
                pos = gap_object.pos if hasattr(gap_object, 'pos') else 'Noun'
                follow_up = f" By the way, {generate_question(word, gap_field, pos).lower()}"
            else:
                # Self-relation or elaboration
                obj_word = answer_result.get('object', '')
                elaborations = [
                    f" I find {obj_word} quite interesting!",
                    f" Would you like to know more about {obj_word}?",
                    f" Tell me more about your experience with {obj_word}!",
                ]
                follow_up = random.choice(elaborations)
        else:
            # We didn't know, the answer already asks the user to teach
            pass
        
        full_response = answer_text + follow_up
        
        return ResponseCandidate(
            text=full_response,
            candidate_type='answerer'
        )
    
    def _generate_elaborator_candidate(self, parsed: Dict,
                                       related_objects: List[Any] = None) -> Optional[ResponseCandidate]:
        """
        Generate an elaboration response for statements.
        Acknowledges the statement and adds related information or self-relation.
        """
        subject = parsed.get('subject', '')
        obj = parsed.get('object', '')
        
        if not subject and not obj:
            return None
        
        topic = subject or obj
        
        # Different elaboration strategies
        templates = [
            f"That's interesting about {topic}! I'd love to know more.",
            f"I see! {topic.title()} sounds fascinating. What else can you tell me?",
            f"Thanks for sharing! That helps me understand {topic} better.",
        ]
        
        # If we have related objects, try to connect
        if related_objects:
            related = random.choice(related_objects)
            related_word = related.word if hasattr(related, 'word') else str(related)
            templates.append(
                f"Interesting! That reminds me of {related_word}. Are they related?"
            )
        
        return ResponseCandidate(
            text=random.choice(templates),
            candidate_type='elaborator'
        )
    
    def _generate_learner_candidate(self, gap_field: Optional[str], 
                                    gap_object: Optional[Any]) -> Optional[ResponseCandidate]:
        """Generate a learning-focused response asking about gaps."""
        if not gap_field or not gap_object:
            return None
        
        # Import here to avoid circular imports
        from core.question_generator import generate_question
        
        word = gap_object.word if hasattr(gap_object, 'word') else str(gap_object)
        pos = gap_object.pos if hasattr(gap_object, 'pos') else 'Noun'
        
        question = generate_question(word, gap_field, pos)
        
        return ResponseCandidate(
            text=question,
            candidate_type='learner'
        )
    
    def _generate_empath_candidate(self, user_sentiment: Dict,
                                   gap_field: Optional[str] = None,
                                   gap_object: Optional[Any] = None) -> ResponseCandidate:
        """Generate an empathy-focused response matching user sentiment."""
        label = user_sentiment.get('label', 'neutral')
        
        # Select template based on sentiment
        if label == 'positive':
            templates = self.EMPATHY_POSITIVE
        elif label == 'negative':
            templates = self.EMPATHY_NEGATIVE
        else:
            templates = self.EMPATHY_NEUTRAL
        
        template = random.choice(templates)
        
        # Add continuation if we have a gap to ask about
        if gap_field and gap_object:
            from core.question_generator import generate_question
            word = gap_object.word if hasattr(gap_object, 'word') else str(gap_object)
            pos = gap_object.pos if hasattr(gap_object, 'pos') else 'Noun'
            question = generate_question(word, gap_field, pos)
            continuation = f"By the way, {question.lower()}"
        else:
            continuation = "Tell me more!"
        
        text = template.format(continuation=continuation)
        
        return ResponseCandidate(
            text=text,
            candidate_type='empath'
        )
    
    def _generate_connector_candidate(self, parsed: Dict,
                                      related_objects: List[Any] = None) -> Optional[ResponseCandidate]:
        """Generate a response that connects to related objects."""
        if not related_objects or not parsed.get('subject'):
            return None
        
        # Pick a random related object
        related = random.choice(related_objects)
        related_word = related.word if hasattr(related, 'word') else str(related)
        subject = parsed.get('subject', 'that')
        
        templates = [
            f"Speaking of {subject}, it reminds me of {related_word}.",
            f"That makes me think of {related_word}. Are they related?",
            f"Interesting! {subject.title()} and {related_word} might be connected.",
        ]
        
        return ResponseCandidate(
            text=random.choice(templates),
            candidate_type='connector'
        )
    
    def play_turn(self, user_input: str,
                  parsed: Dict,
                  gap_field: Optional[str],
                  gap_object: Optional[Any],
                  related_objects: List[Any] = None,
                  base_response: Optional[str] = None,
                  answer_result: Optional[Dict] = None) -> Dict:
        """
        Execute a game turn: generate candidates, score them, pick the best.
        
        This is the main entry point for the game engine.
        
        Args:
            user_input: User's message
            parsed: Parsed sentence components
            gap_field: Missing field (if any)
            gap_object: Object with gap (if any)
            related_objects: Other relevant objects
            base_response: Base confirmation to build upon
            answer_result: Result from QuestionAnswerer (if user asked a question)
            
        Returns:
            Dictionary with selected response and game state
        """
        self.turn_count += 1
        
        # Analyze user sentiment
        user_sentiment = self.sentiment_analyzer.analyze(user_input)
        
        # Generate candidates
        candidates = self.generate_candidates(
            user_input, parsed, gap_field, gap_object, related_objects, answer_result
        )
        
        if not candidates:
            # Fallback if no candidates generated
            return {
                'response': base_response or "I'm listening.",
                'type': 'fallback',
                'sentiment': user_sentiment,
                'turn': self.turn_count
            }
        
        # Score all candidates
        has_gap = gap_field is not None
        is_question = parsed.get('sentence_type') == 'question'
        for candidate in candidates:
            self.evaluate_move(candidate, user_sentiment, has_gap, is_question_input=is_question)
        
        # Sort by score
        candidates.sort(key=lambda c: c.score, reverse=True)
        
        # Get best candidate
        best = candidates[0]
        
        # Check if we should create a hybrid (combine responses)
        final_response = self._maybe_create_hybrid(candidates, base_response, is_question)
        
        # Update game state
        self.total_score += best.score
        self.score_history.append({
            'turn': self.turn_count,
            'score': best.score,
            'type': best.candidate_type
        })
        
        return {
            'response': final_response,
            'selected_type': best.candidate_type,
            'score': best.score,
            'score_breakdown': best.score_breakdown,
            'sentiment': user_sentiment,
            'sentence_type': parsed.get('sentence_type', 'statement'),
            'turn': self.turn_count,
            'total_score': self.total_score,
            'all_candidates': [
                {'text': c.text, 'type': c.candidate_type, 'score': c.score}
                for c in candidates
            ]
        }
    
    def _maybe_create_hybrid(self, candidates: List[ResponseCandidate],
                             base_response: Optional[str],
                             is_question: bool = False) -> str:
        """
        Create a hybrid response combining the best strategies.
        
        The "Advanced Move" - combines empathy with learning or answer with follow-up.
        
        Args:
            candidates: Sorted list of candidates
            base_response: Original confirmation response
            is_question: Whether user input was a question
            
        Returns:
            Final response text
        """
        # Find candidates by type
        empath = next((c for c in candidates if c.candidate_type == 'empath'), None)
        learner = next((c for c in candidates if c.candidate_type == 'learner'), None)
        answerer = next((c for c in candidates if c.candidate_type == 'answerer'), None)
        
        best = candidates[0]
        
        # If user asked a question and we have an answerer, prioritize it
        if is_question and answerer and answerer.score > 0:
            return answerer.text
        
        # If best is empath and learner exists with decent score, combine them
        if best.candidate_type == 'empath' and learner and learner.score > 0:
            # Empath already includes learning continuation
            return best.text
        
        # If best is learner but sentiment is strongly negative, lead with empathy
        if best.candidate_type == 'learner' and empath:
            empath_sentiment = any(word in empath.text.lower() 
                                   for word in ['sorry', 'understand', 'difficult'])
            if empath_sentiment:
                # Extract just the empathy part and add the question
                empathy_intro = empath.text.split('{')[0].strip()
                if empathy_intro.endswith('.'):
                    return f"{empathy_intro} {learner.text}"
        
        # If we have a base response (for statements), combine with best candidate
        if base_response and best.candidate_type in ['learner', 'elaborator']:
            return f"{base_response} {best.text}"
        
        return best.text
    
    def get_game_stats(self) -> Dict:
        """
        Get current game statistics.
        
        Returns:
            Dictionary with game stats
        """
        return {
            'total_score': self.total_score,
            'turn_count': self.turn_count,
            'average_score': self.total_score / max(self.turn_count, 1),
            'history': self.score_history[-10:]  # Last 10 turns
        }
    
    def reset_game(self) -> None:
        """Reset game state for a new session."""
        self.total_score = 0
        self.turn_count = 0
        self.score_history = []
