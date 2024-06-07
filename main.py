import random

from src.player import Player
from src.game import Game, GameConfig

# Define Player configuration
PLAYERS_CONFIG = [
    ("qwen2-0.5", 32),
    ("qwen2-1.5", 32)
]

def main():
    config = GameConfig(PLAYERS_CONFIG)
    game = Game(config)
    game.play()
    overall_scores = game.get_overall_scores()
    print("Overall Scores:")
    for player_name, score in overall_scores.items():
        print(f"{player_name}: {score}")

if __name__ == "__main__":
    main()