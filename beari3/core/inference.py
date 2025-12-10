"""
Inference Engine
Extracts patterns and learning conclusions from prompt-response pairs
"""

import json
import re


class InferenceEngine:
    def __init__(self, db):
        self.db = db
    
    def draw_conclusions(self, prompt_analysis, response_text):
        """
        Analyze the relationship between a prompt and its response
        Extract patterns and learning conclusions
        """
        conclusions = []
        response_strategy = []
        
        # Check for affirmations/interjections at the start
        affirmations = ['cool', 'wow', 'nice', 'great', 'awesome', 'oh', 'hey']
        response_lower = response_text.lower()
        
        for affirm in affirmations:
            if response_lower.startswith(affirm):
                conclusions.append(f"Detected affirmation: '{affirm.title()}'")
                response_strategy.append("affirmation")
                break
        
        # Check if response is a question
        if response_text.strip().endswith('?'):
            conclusions.append("Response strategy is INTERROGATIVE (asking for more info)")
            response_strategy.append("question")
        
        # Check if response references the target/object from prompt
        if prompt_analysis['target']:
            if prompt_analysis['target'].lower() in response_lower:
                conclusions.append(
                    f"Response focuses on the target '{prompt_analysis['target']}'"
                )
                response_strategy.append(f"target_callback:{prompt_analysis['target']}")
        
        # Check if response references the verb from prompt
        if prompt_analysis['verb']:
            if prompt_analysis['verb'].lower() in response_lower:
                conclusions.append(
                    f"Response references the action '{prompt_analysis['verb']}'"
                )
        
        # Identify pattern structure
        pattern_desc = self._describe_pattern(prompt_analysis, response_strategy)
        if pattern_desc:
            conclusions.append(f"PATTERN LEARNED: {pattern_desc}")
        
        self._print_conclusions(conclusions)
        
        return {
            "conclusions": conclusions,
            "response_strategy": "_".join(response_strategy) if response_strategy else "unknown",
            "pattern": pattern_desc
        }
    
    def _describe_pattern(self, prompt_analysis, response_strategy):
        """Generate a human-readable pattern description"""
        prompt_type = prompt_analysis['type']
        
        if prompt_type == "STATEMENT" and "question" in response_strategy:
            if "target_callback" in "_".join(response_strategy):
                return f"[Statement: Action] -> [Affirmation + Question about Target]"
            else:
                return f"[Statement] -> [Question for clarification]"
        
        return None
    
    def _print_conclusions(self, conclusions):
        """Print conclusions in a formatted way"""
        print("\n" + "=" * 30)
        print("   LEARNING CONCLUSIONS")
        print("=" * 30)
        
        if conclusions:
            for i, conclusion in enumerate(conclusions, 1):
                print(f"{i}. {conclusion}")
        else:
            print("No specific patterns detected.")
        
        print("=" * 30 + "\n")
    
    def save_conversational_unit(self, prompt_analysis, response_text, inference_result):
        """Save the complete training interaction to the database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Extract key words from prompt
        key_words = []
        if prompt_analysis['subject']:
            key_words.append(prompt_analysis['subject'])
        if prompt_analysis['verb']:
            key_words.append(prompt_analysis['verb'])
        if prompt_analysis['target']:
            key_words.append(prompt_analysis['target'])
        key_words.extend(prompt_analysis['adjectives'])
        
        # Get structure as JSON
        prompt_structure = json.dumps({
            "subject": prompt_analysis['subject'],
            "verb": prompt_analysis['verb'],
            "target": prompt_analysis['target'],
            "adjectives": prompt_analysis['adjectives'],
            "type": prompt_analysis['type']
        })
        
        cursor.execute("""
            INSERT INTO ConversationalUnits 
            (prompt_raw, prompt_structure, response_raw, response_strategy, key_words)
            VALUES (?, ?, ?, ?, ?)
        """, (
            prompt_analysis['original'],
            prompt_structure,
            response_text,
            inference_result['response_strategy'],
            ", ".join(key_words)
        ))
        
        conn.commit()
        c_unit_id = cursor.lastrowid
        conn.close()
        
        print(f"✓ Saved Conversational Unit #{c_unit_id}")
        
        # Save pattern if one was learned
        if inference_result['pattern']:
            self._save_pattern(prompt_analysis, inference_result)
    
    def _save_pattern(self, prompt_analysis, inference_result):
        """Save or update a learned pattern"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Create input pattern description
        input_pattern = f"{prompt_analysis['type']}:{prompt_analysis['verb'] or 'unknown'}"
        response_pattern = inference_result['response_strategy']
        
        # Check if pattern already exists
        cursor.execute("""
            SELECT id, usage_count FROM PatternMap 
            WHERE input_pattern = ? AND response_pattern = ?
        """, (input_pattern, response_pattern))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update usage count
            cursor.execute("""
                UPDATE PatternMap 
                SET usage_count = usage_count + 1
                WHERE id = ?
            """, (existing[0],))
            print(f"✓ Updated pattern (seen {existing[1] + 1} times)")
        else:
            # Create new pattern
            cursor.execute("""
                INSERT INTO PatternMap (input_pattern, response_pattern, usage_count)
                VALUES (?, ?, 1)
            """, (input_pattern, response_pattern))
            print(f"✓ New pattern saved: {input_pattern} -> {response_pattern}")
        
        conn.commit()
        conn.close()
