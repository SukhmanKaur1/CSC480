import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time


class GoFishGUI:
    def __init__(self, game):
        self.game = game
        self.root = tk.Tk()
        self.root.title("Go Fish")

        # Load card images
        self.card_images = self.load_card_images("cards")

        # Store the selected rank and target AI
        self.selected_rank = None
        self.selected_target = None

        # Create GUI elements
        self.create_widgets()

        # Dynamically adjust window size
        self.adjust_window_size()

    def load_card_images(self, card_folder):
        """Load card images from the specified folder."""
        card_images = {}
        for filename in os.listdir(card_folder):
            if filename.endswith(".png"):
                card_name = filename[:-4]  # Remove ".png" from filename
                image_path = os.path.join(card_folder, filename)
                image = Image.open(image_path)
                image = image.resize((100, 145))  # Resize images to fit the GUI
                card_images[card_name] = ImageTk.PhotoImage(image)

        # Load the back of the card image
        back_image_path = os.path.join(card_folder, "back.png")
        if os.path.exists(back_image_path):
            back_image = Image.open(back_image_path)
            back_image = back_image.resize((100, 145))
            card_images["back"] = ImageTk.PhotoImage(back_image)
        else:
            raise FileNotFoundError("The 'back.png' file is missing in the cards folder.")

        return card_images

    def create_widgets(self):
        """Create and arrange GUI elements."""
        # Frame for the player's hand
        self.hand_frame = tk.Frame(self.root)
        self.hand_frame.pack(side=tk.BOTTOM, pady=20)

        # Create a canvas and scrollbar for the AI players' hands
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.ai_frame = tk.Frame(self.canvas)

        # Configure the canvas
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.TOP, fill=tk.X)

        # Add the AI frame to the canvas
        self.canvas.create_window((0, 0), window=self.ai_frame, anchor="nw")

        # Bind the canvas to the AI frame
        self.ai_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Label for game status
        self.status_label = tk.Label(self.root, text="Your Turn", font=("Arial", 16))
        self.status_label.pack(pady=10)

        # Label for feedback messages
        self.feedback_label = tk.Label(self.root, text="", font=("Arial", 12), wraplength=800)
        self.feedback_label.pack(pady=10)

        # Button to start the game
        self.start_button = tk.Button(self.root, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=10)

        # Button to submit the selected rank and target
        self.submit_button = tk.Button(self.root, text="Ask for Card", command=self.submit_move, state=tk.DISABLED)
        self.submit_button.pack(pady=10)

    def adjust_window_size(self):
        """Adjust the window size dynamically based on the number of AI players and cards."""
        num_ai_players = len(self.game.ai_players)
        cards_per_ai = max(len(ai.hand) for ai in self.game.ai_players) if self.game.ai_players else 0
        card_width = 100  # Width of each card
        card_height = 145  # Height of each card
        padding = 20  # Padding between elements

        # Calculate the required width
        required_width = num_ai_players * (cards_per_ai * card_width + padding) + padding
        required_height = card_height * 2 + padding * 4  # Space for player's hand, AI hands, and other elements

        # Set the window size
        self.root.geometry(f"{min(required_width, 1200)}x{min(required_height, 800)}")

    def start_game(self):
        """Start the game and update the GUI."""
        self.start_button.pack_forget()  # Hide the start button
        self.update_gui()

    def update_gui(self):
        """Update the GUI to reflect the current game state."""
        # Clear previous cards
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        for widget in self.ai_frame.winfo_children():
            widget.destroy()

        # Display the player's hand
        for card in self.game.human.hand:
            card_image = self.card_images.get(card, self.card_images["back"])
            card_label = tk.Label(self.hand_frame, image=card_image)
            card_label.pack(side=tk.LEFT, padx=5)
            # Make the card clickable
            card_label.bind("<Button-1>", lambda event, c=card: self.select_rank(c.split("_")[0]))

        # Display the AI players' hands (back of cards)
        for ai in self.game.ai_players:
            ai_label = tk.Label(self.ai_frame, text=f"{ai.name}'s Hand", font=("Arial", 12))
            ai_label.pack(side=tk.LEFT, padx=20)
            for _ in ai.hand:
                card_label = tk.Label(self.ai_frame, image=self.card_images["back"])
                card_label.pack(side=tk.LEFT, padx=5)
            # Make the AI player clickable
            ai_label.bind("<Button-1>", lambda event, a=ai: self.select_target(a))

        # Update the status label
        self.status_label.config(text=f"{self.game.current_player.name}'s Turn")

        # Enable the submit button if a rank and target are selected
        if self.selected_rank and self.selected_target:
            self.submit_button.config(state=tk.NORMAL)
        else:
            self.submit_button.config(state=tk.DISABLED)

    def select_rank(self, rank):
        """Handle card clicks to select a rank."""
        self.selected_rank = rank
        self.feedback_label.config(text=f"Selected rank: {rank}")
        self.update_gui()

    def select_target(self, target):
        """Handle AI player selection."""
        self.selected_target = target
        self.feedback_label.config(text=f"Selected target: {target.name}")
        self.update_gui()

    def submit_move(self):
        """Handle the submit button click to make a move."""
        if self.selected_rank and self.selected_target:
            # Perform the move
            if self.selected_target.has_rank(self.selected_rank):
                self.feedback_label.config(text=f"{self.selected_target.name} gives you all {self.selected_rank}s!")
                received_cards = self.selected_target.give_cards(self.selected_rank)
                for card in received_cards:
                    self.game.human.receive_card(card)
                self.game.human.check_for_books()
            else:
                self.feedback_label.config(text=f"{self.selected_target.name} says 'Go Fish!'")
                if self.game.deck:
                    drawn_card = self.game.deck.pop()
                    self.feedback_label.config(text=f"{self.feedback_label.cget('text')} You draw a {drawn_card}.")
                    self.game.human.receive_card(drawn_card)

            # Update AI memory
            for ai in self.game.ai_players:
                if ai != self.game.human:
                    ai.update_request_history(self.selected_rank, self.game.human.name, self.selected_target.has_rank(self.selected_rank))

            # Reset selections
            self.selected_rank = None
            self.selected_target = None

            # Update the GUI
            self.update_gui()

            # Check if the game is over
            if self.game.check_winner():
                self.game.end_game()
                return

            # Switch to the next player's turn
            self.game.next_turn()

            # If the next player is an AI, trigger its turn
            if isinstance(self.game.current_player, type(self.game.ai_players[0])):
                self.root.after(1000, self.ai_turn)  # Delay for 1 second before AI's turn
            else:
                self.update_gui()

    def ai_turn(self):
        """Handle the AI's turn."""
        if isinstance(self.game.current_player, type(self.game.ai_players[0])):
            # Simulate AI thinking
            self.feedback_label.config(text=f"{self.game.current_player.name} is thinking...")
            self.root.update()  # Force update the GUI
            time.sleep(1.5)  # Simulate thinking time

            # Perform the AI's turn
            self.game.ai_turn()

            # Update the feedback label with AI's actions
            self.feedback_label.config(text=self.get_ai_turn_feedback())
            self.update_gui()

            # Check if the game is over
            if self.game.check_winner():
                self.game.end_game()
                return

            # Switch to the next player's turn
            self.game.next_turn()

            # If the next player is an AI, trigger its turn
            if isinstance(self.game.current_player, type(self.game.ai_players[0])):
                self.root.after(1000, self.ai_turn)  # Delay for 1 second before next AI's turn
            else:
                self.update_gui()

    def get_ai_turn_feedback(self):
        """Generate feedback text for the AI's turn."""
        feedback = []
        if isinstance(self.game.current_player, type(self.game.ai_players[0])):
            # Get the rank and target from the AI's last move
            rank, target = self.game.current_player.choose_request(self.game.players)
            if rank is None or target is None:
                feedback.append(f"{self.game.current_player.name} has no valid move. Turn skipped.")
            else:
                feedback.append(f"{self.game.current_player.name}'s Turn:")
                feedback.append(f"{self.game.current_player.name} asks {target.name} for {rank}s.")
                if target.has_rank(rank):
                    feedback.append(f"{target.name} gives {self.game.current_player.name} all {rank}s.")
                else:
                    feedback.append(f"{target.name} says 'Go Fish!'")
                    if self.game.deck:
                        feedback.append(f"{self.game.current_player.name} draws a card.")
        return "\n".join(feedback)

    def run(self):
        """Run the GUI main loop."""
        self.root.mainloop()
