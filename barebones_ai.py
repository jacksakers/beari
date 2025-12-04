import random
import sys

class BarebonesAI:
    def __init__(self):
        # This dictionary is the "Model." 
        # In a massive AI like GPT, this would be billions of numeric weights.
        # Here, it is a simple map of: Word -> [List of possible next words]
        self.brain = {}

    def train(self, filename):
        """
        Reads a text file and 'learns' the patterns of words.
        """
        print(f"Training on {filename}...")
        
        try:
            with open(filename, 'r') as f:
                text = f.read()
        except FileNotFoundError:
            print("Error: File not found. Make sure 'training_data.txt' exists.")
            return

        # 1. Tokenization:
        # We clean the text (lowercase it) and split it into a list of words.

        # add `/n` to new lines to preserve sentence breaks
        text = text.replace('\n', ' newline ')

        # print text for debugging
        print("Original Text Sample:")
        print(text[:500])  # print first 500 characters

        # In professional AI, this step is very complex. Here, we just split by spaces.
        words = text.lower().split()

        # 2. Building the Parameters (The "Training" Phase):
        # We loop through the text and look at pairs of words.
        # If we see "the cat", we learn that "cat" can follow "the".
        for i in range(len(words) - 1):
            current_word = words[i]
            next_word = words[i + 1]

            # If the model hasn't seen this word before, create a new entry
            if current_word not in self.brain:
                self.brain[current_word] = []

            # Append the next word to the list of possibilities.
            # Note: If "is" follows "python" twice, "is" will appear twice in the list.
            # This naturally handles probability! Randomly picking from the list
            # will favor words that appear more often.
            self.brain[current_word].append(next_word)
        
        print("Training complete!")
        print(f"I learned {len(self.brain)} unique words.")

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

def main():
    # Initialize the AI
    ai = BarebonesAI()
    
    # Train it
    ai.train("training_data.txt")

    print("\n--- AI Ready. Type 'quit' to exit. ---")
    print("(Try typing words that are in the text file to see how it predicts the next words)")

    # The Chat Loop
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
        
        # Get response
        reply = ai.generate_response(user_input)

        # Replace the placeholder token with actual newlines for better readability
        reply = reply.replace(' newline ', '\n')
        
        if reply:
            print(f"AI: {reply}")
        else:
            print("AI: I don't know that word, so I can't predict what comes next.")

if __name__ == "__main__":
    main()