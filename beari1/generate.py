import random

def generate_response(self, user_input, length=10):
    """
    Takes a starting word (user input) and tries to predict the next words.
    """
    # We only look at the last word the user typed to start our chain
    input_words = user_input.lower().split()
    if not input_words:
        return "Please say something."
        
    current_word = input_words[-1] 
    response = []

    for _ in range(length):
        # Check if the AI knows this word
        if current_word in self.brain:
            # 3. Inference (The "Prediction" Phase):
            # Look at all the words that have historically followed the current word
            possible_next_words = self.brain[current_word]
            
            # Pick one randomly. 
            # Because we stored duplicates during training, this is a "weighted" random choice.
            next_word = random.choice(possible_next_words)
            
            response.append(next_word)
            current_word = next_word # Move the 'cursor' forward
        else:
            # If the AI hits a word it doesn't know, it stops.
            break
    
    return " ".join(response)