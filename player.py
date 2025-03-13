from collections import defaultdict
import random


class Player:
    """Represents a human player."""

    def __init__(self, name):
        self.name = name
        self.hand = []
        self.books = []  # Completed sets of four cards of the same rank

    def receive_card(self, card):
        """Adds a card to the player's hand."""
        self.hand.append(card)
        self.check_for_books()

    def check_for_books(self):
        """Checks if the player has a full set of 4 cards of the same rank."""
        rank_counts = defaultdict(int)
        for card in self.hand:
            rank = card.split("_")[0]  # Extract the rank from the card name
            rank_counts[rank] += 1

        for rank, count in rank_counts.items():
            if count == 4:  # Found a book (set of four)
                self.books.append(rank)
                self.hand = [c for c in self.hand if not c.startswith(rank)]  # Remove all cards of this rank
                print(f"{self.name} completed a book of {rank}s!")

    def has_rank(self, rank):
        """Checks if the player has a given rank."""
        return any(card.startswith(rank) for card in self.hand)

    def give_cards(self, rank):
        """Gives all cards of a specific rank to another player."""
        given_cards = [card for card in self.hand if card.startswith(rank)]
        self.hand = [card for card in self.hand if not card.startswith(rank)]
        return given_cards

    def choose_request(self, players):
        """Human players do not use this method."""
        raise NotImplementedError("Human players do not use choose_request.")

    def __str__(self):
        return f"{self.name}: Hand={self.hand}, Books={self.books}"


class GoFishAI(Player):
    """Represents an AI player."""

    def __init__(self, name):
        super().__init__(name)
        self.request_history = defaultdict(int)  # Track other players' past requests
        self.player_probabilities = defaultdict(lambda: defaultdict(float))  # Probabilities of what other players might have
        self.last_received_rank = None  # Tracks AI's last successful request

    def choose_request(self, players):
        """AI selects the best rank to request and the target player based on probability & strategy."""
        if not self.hand:
            return None, None  # No valid move

        rank_counts = defaultdict(int)
        for card in self.hand:
            rank = card.split("_")[0]  # Extract the rank from the card name
            rank_counts[rank] += 1

        available_ranks = [rank for rank in rank_counts if rank not in self.books]

        if not available_ranks:
            return None, None  # No valid move

        # **Priority 1:** Avoid ranks that have failed too many times
        failed_ranks = [rank for rank, count in self.request_history.items() if count >= 4]
        smart_choices = [rank for rank in available_ranks if rank not in failed_ranks]

        # **Priority 2:** Prioritize asking for ranks AI just received
        if self.last_received_rank in smart_choices:
            return self.last_received_rank, random.choice([p for p in players if p != self])

        # **Priority 3:** If AI has at least 2 of a rank, prioritize asking for that
        for rank in smart_choices:
            if rank_counts[rank] >= 2:
                return rank, random.choice([p for p in players if p != self])

        # **Priority 4:** If no strong choice, pick a random rank from available ones
        rank_choice = random.choice(smart_choices) if smart_choices else random.choice(available_ranks)
        return rank_choice, random.choice([p for p in players if p != self])

    def update_request_history(self, rank, player_name, success):
        """Updates AI's knowledge of the game state."""
        self.request_history[rank] += 1  # Track how often a player asks for a rank
        if success:
            self.player_probabilities[player_name][rank] += 0.3  # More likely the player has this
        else:
            self.player_probabilities[player_name][rank] -= 0.2  # Less likely the player has this
        self.player_probabilities[player_name][rank] = max(0, min(1, self.player_probabilities[player_name][rank]))
        # Keep between 0-1
