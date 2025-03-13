from game import GoFishGame
from gui import GoFishGUI


def get_number_of_ai_players():
    """Prompts the user to select the number of AI players (1-9)."""
    while True:
        try:
            num_ai = int(input("How many AI players do you want to play with? (1-9): "))
            if 1 <= num_ai <= 9:
                return num_ai
            else:
                print("Please enter a number between 1 and 9.")
        except ValueError:
            print("Invalid input. Please enter a number.")


# Run the game
if __name__ == "__main__":
    num_ai_players = get_number_of_ai_players()
    game = GoFishGame(num_ai_players)
    gui = GoFishGUI(game)
    gui.run()
