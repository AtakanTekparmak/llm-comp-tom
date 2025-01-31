from src.game import Game
from src.player import Player
from src.settings import NUM_PLAYERS, MODELS
import asyncio

async def main():
    # Create players with alternating models
    players = []
    model_names = ["deepseek-r1-70b", "deepseek-r1-14b"]  # We want 4 of each
    players_per_model = NUM_PLAYERS // len(model_names)
    
    for model_name in model_names:
        for i in range(players_per_model):
            player_number = len(players) + 1
            players.append(Player(f"Player{player_number}", MODELS[model_name]))

    game = Game(players)
    await game.play()
    overall_scores = game.get_overall_scores()
    print("\nOverall Scores:")
    for player_name, score in overall_scores.items():
        print(f"{player_name}: {score}")

if __name__ == "__main__":
    asyncio.run(main())