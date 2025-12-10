from model import BarebonesAI
import sys

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

def main():
    # Initialize the AI
    ai = BarebonesAI()
    
    # Get training file from command line or use default
    training_file = sys.argv[1] if len(sys.argv) > 1 else "training_data.txt"
    
    # Train it
    train(ai, training_file)
    
    # Save the trained model
    model_file = "trained_model.json"
    ai.save_model(model_file)
    
    print(f"\n✓ Training complete! Model saved to '{model_file}'")
    print("Now you can run 'python chat.py' to chat with the AI.")

if __name__ == "__main__":
    main()
