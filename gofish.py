import random
import time 
from collections import defaultdict

# Standard 52-card deck (only ranks, ignoring suits)
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

class Player:
    """Represents a Go Fish player (human or AI)."""
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.books = []  # Completed sets of four cards

    def receive_card(self, card):
        """Adds a card to the AI's hand and tracks the last received rank."""
        self.hand.append(card)
        self.last_received_rank = card  # Remember the last rank received
        self.check_for_books()

    def check_for_books(self):
        """Checks if the player has a full set of 4 cards of the same rank."""
        rank_counts = defaultdict(int)
        for card in self.hand:
            rank_counts[card] += 1
        
        for rank, count in rank_counts.items():
            if count == 4:  # Found a book (set of four)
                self.books.append(rank)
                self.hand = [c for c in self.hand if c != rank]  # Remove from hand
                print(f"{self.name} completed a book of {rank}s!")

    def has_rank(self, rank):
        """Checks if the player has a given rank."""
        return rank in self.hand

    def give_cards(self, rank):
        """Gives all cards of a specific rank to another player."""
        given_cards = [card for card in self.hand if card == rank]
        self.hand = [card for card in self.hand if card != rank]
        return given_cards

    def __str__(self):
        return f"{self.name}: Hand={self.hand}, Books={self.books}"

class GoFishAI(Player):
    """AI player with strategic decision-making."""
    def __init__(self, name):
        super().__init__(name)
        self.request_history = defaultdict(int)  # Track human's past requests
        self.human_probabilities = defaultdict(float)  # Probabilities of what human might have
        self.last_received_rank = None  # Tracks AI's last successful request

    def update_request_history(self, rank, success):
        """Updates AI's knowledge of the game state."""
        self.request_history[rank] += 1  # Track how often human asks for a rank
        if success:
            self.human_probabilities[rank] += 0.3  # More likely human has this
        else:
            self.human_probabilities[rank] -= 0.2  # Less likely human has this
        self.human_probabilities[rank] = max(0, min(1, self.human_probabilities[rank]))  # Keep between 0-1

    def choose_request(self):
        """AI selects the best rank to request based on probability & strategy."""
        if not self.hand:
            return None  # No valid move

        rank_counts = {rank: self.hand.count(rank) for rank in set(self.hand)}
        available_ranks = [rank for rank in rank_counts if rank not in self.books]

        if not available_ranks:
            return None  # No valid move

        # **Priority 1:** Avoid ranks that have failed too many times
        failed_ranks = [rank for rank, count in self.request_history.items() if count >= 4]
        smart_choices = [rank for rank in available_ranks if rank not in failed_ranks]

        # **Priority 2:** Prioritize asking for ranks AI just received
        if self.last_received_rank in smart_choices:
            return self.last_received_rank

        # **Priority 3:** If AI has at least 2 of a rank, prioritize asking for that
        for rank in smart_choices:
            if rank_counts[rank] >= 2:
                return rank  

        # **Priority 4:** If no strong choice, pick a random rank from available ones
        return random.choice(smart_choices) if smart_choices else random.choice(available_ranks)

    
class GoFishGame:
    """Main game engine: Human vs AI"""
    def __init__(self):
        self.deck = RANKS * 4  # Full deck (4 of each rank)
        random.shuffle(self.deck)
        self.human = Player("You")
        self.ai = GoFishAI("AI")
        self.current_player = self.human  # Start with the human

        # Deal 7 cards to each player
        for _ in range(7):
            if self.deck:
                self.human.receive_card(self.deck.pop())
            if self.deck:
                self.ai.receive_card(self.deck.pop())

    def play_turn(self):
        """Handles the turn for the current player (Human or AI)."""
        if self.check_winner():  # Check if the game should end before the turn starts
            self.end_game()
            return
        
        print(f"\n{self.current_player.name}'s turn...")

        if not self.current_player.hand:
            print(f"{self.current_player.name} has no cards left and skips this turn.")
            self.next_turn()
            return

        if self.current_player == self.human:
            self.human_turn()
        else:
            self.ai_turn()

        self.display_score()  # 🔹 Add this here to show score after every turn!


    def human_turn(self):
        """Handles the human player's turn."""
        print(f"Your hand: {self.human.hand}")
        rank = input("Choose a rank to ask for: ").strip()
        
        if rank not in self.human.hand:
            print("You can only ask for a rank that you have!")
            return self.human_turn()  # Ask again

        target = self.ai  # Only one opponent in 1v1 mode

        if target.has_rank(rank):
            print(f"AI gives you all {rank}s!")
            received_cards = target.give_cards(rank)
            for card in received_cards:
                self.human.receive_card(card)
            self.human.check_for_books()
        else:
            print("AI says 'Go Fish!'")
            if self.deck:
                drawn_card = self.deck.pop()
                print(f"You draw a {drawn_card}.")
                self.human.receive_card(drawn_card)

        # AI updates memory
        self.ai.update_request_history(rank, target.has_rank(rank))

        self.next_turn()

    def ai_turn(self):
        """Handles the AI's turn automatically with a slight delay."""
        time.sleep(1.5)  # Add delay before AI makes a move
        rank = self.ai.choose_request()

        if rank is None:
            print("AI has no valid move. Turn skipped.")
            self.next_turn()
            return

        print(f"AI thinks... ")  # Simulate thinking time
        time.sleep(1.5)  # Another slight pause before AI speaks
        print(f"AI asks you for {rank}s.")

        if self.human.has_rank(rank):
            time.sleep(1)  # Delay before showing human's response
            print(f"You give AI all {rank}s.")
            received_cards = self.human.give_cards(rank)
            for card in received_cards:
                self.ai.receive_card(card)
            self.ai.check_for_books()
        else:
            time.sleep(1)  # Delay before saying "Go Fish!"
            print("You say 'Go Fish!'")
            if self.deck:
                time.sleep(1)  # Delay before AI draws a card
                drawn_card = self.deck.pop()
                print(f"AI draws a card.")
                self.ai.receive_card(drawn_card)

        self.next_turn()

    def next_turn(self):
        """Switches to the next player's turn."""
        self.current_player = self.human if self.current_player == self.ai else self.ai

    def check_winner(self):
        """Checks if the game is over when either player runs out of cards."""
        total_books = len(self.human.books) + len(self.ai.books)
        
        # If all books are completed (13 books total), game ends
        if total_books == len(RANKS):
            return True

        # **NEW RULE: If AI or Human has no cards left, game should also end immediately**
        if not self.human.hand or not self.ai.hand:
            return True  # This will now trigger an immediate game end

        return False

    def end_game(self):
            """Handles end of game and announces winner."""
            self.display_score()  # 🔹 Show the final score before announcing the winner
            
            print("\n🎉 Game Over! 🎉")
            print(f"You completed books: {self.human.books}")
            print(f"AI completed books: {self.ai.books}")

            if len(self.human.books) > len(self.ai.books):
                print("🎉 You win!")
            elif len(self.human.books) < len(self.ai.books):
                print("🤖 AI wins!")
            else:
                print("🤝 It's a tie!")

            exit()  # Stop the game loop immediately

    def play_game(self):
        """Runs the full game loop."""
        print("Starting Go Fish (1v1: You vs AI)!")
        while not self.check_winner():
            self.play_turn()

        self.end_game()  # Ensure the game ends properly

    def display_score(self):
        """Displays the current book count for both players."""
        print(f"\n📊 Score Update: You - {len(self.human.books)} books | AI - {len(self.ai.books)} books")


# Run the game
if __name__ == "__main__":
    game = GoFishGame()
    game.play_game()
