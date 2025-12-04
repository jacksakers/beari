from model import BarebonesAI
from generate import generate_response

def main():
    # Initialize the AI
    ai = BarebonesAI()
    
    # Load the trained model
    model_file = "trained_model.json"
    ai.load_model(model_file)
    
    if not ai.brain:
        print("\nNo trained model found!")
        print("Please run 'python train.py' first to train the model.")
        return

    print("\n--- Beari is Ready. Type 'quit' to exit. ---")
    print("(Try typing words that are in the text file to see how it predicts the next words)")

    # The Chat Loop
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit' or user_input.lower() == 'q':
            break
        
        # Get response
        reply = generate_response(ai, user_input)

        # Replace the placeholder token with actual newlines for better readability
        reply = reply.replace('newline', '\n')
        
        if reply:
            print(f"Beari: {reply}")
        else:
            print("Beari: I don't know that word, so I can't predict what comes next.")

if __name__ == "__main__":
    main()
