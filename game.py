import random
import time
from player import Player, GoFishAI

# Standard 52-card deck (only ranks, ignoring suits)
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


class GoFishGame:
    """Main game engine: Human vs multiple AI players."""

    def __init__(self, num_ai_players):
        self.deck = RANKS * 4  # Full deck (4 of each rank)
        random.shuffle(self.deck)
        self.human = Player("You")
        self.ai_players = [GoFishAI(f"AI {i + 1}") for i in range(num_ai_players)]  # Create AI players
        self.players = [self.human] + self.ai_players  # All players in the game
        self.current_player = self.human  # Start with the human

        # Determine the number of starting cards based on the number of players
        total_players = len(self.players)
        if total_players <= 3:
            starting_cards = 7
        elif total_players <= 6:
            starting_cards = 5
        else:
            starting_cards = 4

        # Deal starting cards to each player
        for _ in range(starting_cards):
            for player in self.players:
                if self.deck:
                    player.receive_card(self.deck.pop())

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

        self.display_score()  # Show score after every turn!

    def human_turn(self):
        """Handles the human player's turn."""
        print(f"Your hand: {self.human.hand}")
        rank = input("Choose a rank to ask for: ").strip()

        if rank not in self.human.hand:
            print("You can only ask for a rank that you have!")
            return self.human_turn()  # Ask again

        # Prompt for AI player selection
        target_name = input(
            f"Which AI player do you want to ask? ({', '.join(ai.name for ai in self.ai_players)}): ").strip()

        # Handle input: AI name (e.g., "AI 3") or number (e.g., "3")
        if target_name.isdigit():
            target_number = int(target_name)
            if 1 <= target_number <= len(self.ai_players):
                target_name = f"AI {target_number}"
            else:
                print(f"Invalid AI number. Please enter a number between 1 and {len(self.ai_players)}.")
                return self.human_turn()
        else:
            target_name = target_name

        # Find the target AI player
        target = next((ai for ai in self.ai_players if ai.name == target_name), None)

        if not target:
            print(f"Invalid AI player: {target_name}. Try again.")
            return self.human_turn()

        if target.has_rank(rank):
            print(f"{target.name} gives you all {rank}s!")
            received_cards = target.give_cards(rank)
            for card in received_cards:
                self.human.receive_card(card)
            self.human.check_for_books()
        else:
            print(f"{target.name} says 'Go Fish!'")
            if self.deck:
                drawn_card = self.deck.pop()
                print(f"You draw a {drawn_card}.")
                self.human.receive_card(drawn_card)

        # Update AI memory
        for ai in self.ai_players:
            if ai != self.human:
                ai.update_request_history(rank, self.human.name, target.has_rank(rank))

        self.next_turn()

    def ai_turn(self):
        """Handles the AI's turn automatically with a slight delay."""
        time.sleep(1.5)  # Add delay before AI makes a move

        # Ensure the current player is an AI before calling choose_request
        if isinstance(self.current_player, GoFishAI):
            rank, target = self.current_player.choose_request(self.players)
        else:
            print(f"{self.current_player.name} is not an AI player. Turn skipped.")
            self.next_turn()
            return

        if rank is None or target is None:
            print(f"{self.current_player.name} has no valid move. Turn skipped.")
            self.next_turn()
            return

        print(f"{self.current_player.name} thinks... ")  # Simulate thinking time
        time.sleep(1.5)  # Another slight pause before AI speaks
        print(f"{self.current_player.name} asks {target.name} for {rank}s.")

        if target.has_rank(rank):
            time.sleep(1)  # Delay before showing target's response
            print(f"{target.name} gives {self.current_player.name} all {rank}s.")
            received_cards = target.give_cards(rank)
            for card in received_cards:
                self.current_player.receive_card(card)
            self.current_player.check_for_books()
        else:
            time.sleep(1)  # Delay before saying "Go Fish!"
            print(f"{target.name} says 'Go Fish!'")
            if self.deck:
                time.sleep(1)  # Delay before AI draws a card
                drawn_card = self.deck.pop()
                print(f"{self.current_player.name} draws a card.")
                self.current_player.receive_card(drawn_card)

        # Update AI memory
        for ai in self.ai_players:
            if ai != self.current_player:
                ai.update_request_history(rank, target.name, target.has_rank(rank))

        self.next_turn()

    def next_turn(self):
        """Switches to the next player's turn."""
        current_index = self.players.index(self.current_player)
        next_index = (current_index + 1) % len(self.players)
        self.current_player = self.players[next_index]

    def check_winner(self):
        """Checks if the game is over when either player runs out of cards."""
        total_books = sum(len(player.books) for player in self.players)

        # If all books are completed (13 books total), game ends
        if total_books == len(RANKS):
            return True

        # If any player has no cards left, game ends
        if any(not player.hand for player in self.players):
            return True

        return False

    def end_game(self):
        """Handles end of game and announces winner."""
        self.display_score()  # Show the final score before announcing the winner

        print("\n🎉 Game Over! 🎉")
        for player in self.players:
            print(f"{player.name} completed books: {player.books}")

        max_books = max(len(player.books) for player in self.players)
        winners = [player.name for player in self.players if len(player.books) == max_books]

        if len(winners) == 1:
            print(f"🎉 {winners[0]} wins!")
        else:
            print("🤝 It's a tie between:", ", ".join(winners))

        exit()  # Stop the game loop immediately

    def play_game(self):
        """Runs the full game loop."""
        print(f"Starting Go Fish (You vs {len(self.ai_players)} AI players)!")
        while not self.check_winner():
            self.play_turn()

        self.end_game()  # Ensure the game ends properly

    def display_score(self):
        """Displays the current book count for all players."""
        print("\n📊 Score Update:")
        for player in self.players:
            print(f"{player.name}: {len(player.books)} books")
