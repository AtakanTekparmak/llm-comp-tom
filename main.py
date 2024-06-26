from src.game import Game, GameConfig
from src.config import NUM_PLAYERS

from dotenv import load_dotenv

# Define Player configuration
PLAYERS_CONFIG = [
    #("qwen2-1.5", NUM_PLAYERS // 2),
    #("qwen2-0.5", NUM_PLAYERS // 2)
    #("qwen2-7", NUM_PLAYERS)
    ("llama3-70b", NUM_PLAYERS)
]

def main():
    load_dotenv()
    config = GameConfig(PLAYERS_CONFIG)
    game = Game(config)
    game.play()
    overall_scores = game.get_overall_scores()
    print("Overall Scores:")
    for player_name, score in overall_scores.items():
        print(f"{player_name}: {score}")

if __name__ == "__main__":
    main()