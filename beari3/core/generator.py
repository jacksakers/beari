"""
Response Generator
Auto mode that matches pattern signatures and generates responses
"""

import json
import re


class ResponseGenerator:
    def __init__(self, db, analyzer):
        self.db = db
        self.analyzer = analyzer
    
    def generate_response(self, user_input):
        """
        Generate a response by finding similar patterns in the database
        Returns: (response, confidence, match_info)
        """
        # Analyze the input
        analysis = self.analyzer.analyze(user_input)
        
        # Try to find exact signature match
        exact_match = self._find_by_signature(analysis['signature'])
        if exact_match:
            response = self._fill_template(exact_match, analysis)
            return response, 1.0, f"Exact match: {analysis['signature']}"
        
        # Try to find partial signature match (same category, different tense)
        partial_match = self._find_partial_signature(analysis)
        if partial_match:
            response = self._fill_template(partial_match, analysis)
            return response, 0.7, f"Partial match: {partial_match['pattern_signature']}"
        
        # No match found
        return None, 0.0, "No matching pattern found"
    
    def _find_by_signature(self, signature):
        """Find a conversational unit with exact signature match"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, response_raw, response_template, pattern_signature
            FROM ConversationalUnits
            WHERE pattern_signature = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (signature,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "response_raw": result[1],
                "response_template": result[2],
                "pattern_signature": result[3]
            }
        return None
    
    def _find_partial_signature(self, analysis):
        """Find a signature that matches on key categories (ignore tense)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Extract category from signature (e.g., SELF_PAST_FOOD -> look for any SELF_*_FOOD)
        sig_parts = analysis['signature'].split('_')
        
        if len(sig_parts) >= 3:
            # Look for signatures with same subject and category
            pattern = f"{sig_parts[0]}_%_{sig_parts[-1]}"
            
            cursor.execute("""
                SELECT id, response_raw, response_template, pattern_signature
                FROM ConversationalUnits
                WHERE pattern_signature LIKE ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (pattern.replace('_', '%'),))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "id": result[0],
                    "response_raw": result[1],
                    "response_template": result[2],
                    "pattern_signature": result[3]
                }
        
        conn.close()
        return None
    
    def _fill_template(self, match, analysis):
        """Fill in a response template with current analysis data"""
        template = match.get('response_template')
        
        if not template:
            # No template, return raw response
            return match['response_raw']
        
        # Replace placeholders with actual values
        response = template
        
        # Common replacements
        replacements = {
            '{target}': analysis.get('target', 'it'),
            '{verb}': analysis.get('verb', 'do'),
            '{subject}': analysis.get('subject', 'you')
        }
        
        for placeholder, value in replacements.items():
            if placeholder in response:
                response = response.replace(placeholder, value or 'it')
        
        return response
    
    def create_template_from_response(self, response_text, analysis):
        """
        Create a template from a response by replacing specific nouns with placeholders
        Example: "How was the curry?" -> "How was the {target}?"
        """
        template = response_text
        
        # Replace target noun if present
        if analysis.get('target'):
            target = analysis['target']
            # Use word boundaries to avoid partial replacements
            template = re.sub(r'\b' + re.escape(target) + r'\b', '{target}', template, flags=re.IGNORECASE)
        
        # Only return template if we actually made substitutions
        if template != response_text:
            return template
        
        # No substitutions made, return None (will use raw response)
        return None
    
    def test_generation(self):
        """Test the response generator with available patterns"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_signature, COUNT(*) as count
            FROM ConversationalUnits
            WHERE pattern_signature IS NOT NULL
            GROUP BY pattern_signature
            ORDER BY count DESC
        """)
        
        patterns = cursor.fetchall()
        conn.close()
        
        print("\n" + "=" * 60)
        print("   AVAILABLE PATTERNS FOR GENERATION")
        print("=" * 60)
        
        if patterns:
            for signature, count in patterns:
                print(f"  {signature:<40} ({count} example(s))")
        else:
            print("  No patterns available yet. Train the model first!")
        
        print("=" * 60 + "\n")
