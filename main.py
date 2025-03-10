from src.game import Game
from src.config import GameConfig, ModelConfig
from src.rating.manager import RatingManager
import asyncio
import os

async def main():
    # Create data directory for ratings
    os.makedirs("data/ratings", exist_ok=True)
    
    # Create rating manager
    rating_manager = RatingManager(data_dir="data/ratings")
    
    # Create game configuration with equal agents per model
    agents_per_model = 4
    config = GameConfig(
        num_actions=16,  # Number of possible actions
        num_turns=4,     # Number of turns
        agents_per_model=agents_per_model,  # Ensure equal distribution of agents per model
        models=[
            ModelConfig("deepseek-r1-32b", "deepseek/deepseek-r1-distill-qwen-32b", agents_per_model),  # Model name, model API name, number of agents
            ModelConfig("deepseek-r1-14b", "deepseek/deepseek-r1-distill-qwen-14b", agents_per_model),
            ModelConfig("deepseek-r1-1.5b", "deepseek/deepseek-r1-distill-qwen-1.5b", agents_per_model),
        ]
    )

    # Create and play game with rating manager
    game = Game.create_game(config, rating_manager)
    await game.play()
    
    # Display results including Elo ratings
    game.display_final_results()
    
    # Generate a rating report
    rating_manager.generate_rating_report()
    print("\nRating report has been generated in data/ratings/")

if __name__ == "__main__":
    asyncio.run(main())