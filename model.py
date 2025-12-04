import random

class BarebonesAI:
    def __init__(self):
        # This dictionary is the "Model." 
        # In a massive AI like GPT, this would be billions of numeric weights.
        # Here, it is a simple map of: Word -> [List of possible next words]
        self.brain = {}

    def save_model(self, filename):
        """
        Saves the trained model to a file so we don't have to retrain every time.
        """
        import json
        with open(filename, 'w') as f:
            json.dump(self.brain, f)
        print(f"Model saved to {filename}")

    def load_model(self, filename):
        """
        Loads a previously trained model from a file.
        """
        import json
        try:
            with open(filename, 'r') as f:
                self.brain = json.load(f)
            print(f"Model loaded from {filename}")
            print(f"Loaded {len(self.brain)} unique words.")
        except FileNotFoundError:
            print(f"Error: Model file '{filename}' not found.")
