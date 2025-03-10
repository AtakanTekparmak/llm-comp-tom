"""
Example script demonstrating how to use the Elo rating system.

This script creates a game with multiple models, plays it,
and then updates the Elo ratings based on the results.
"""

import asyncio
import os
import sys

# Add the parent directory to the path so we can import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.game import Game
from src.config import GameConfig, ModelConfig
from src.rating.core import EloConfig
from src.rating.manager import RatingManager

async def run_single_game():
    """
    Run a single game with multiple models and update Elo ratings.
    """
    print("=== Running a single game with Elo rating updates ===")
    
    # Create rating manager
    rating_manager = RatingManager(data_dir="data/ratings")
    
    # Create game configuration with equal agents per model
    config = GameConfig(
        num_actions=16,  # Number of possible actions
        num_turns=10,    # Number of turns
        agents_per_model=2,  # Ensure same number of agents per model
        models=[
            ModelConfig("deepseek-r1-32b", "deepseek/deepseek-r1-distill-qwen-32b", 2),
            ModelConfig("deepseek-r1-1.5b", "deepseek/deepseek-r1-distill-qwen-1.5b", 2)
        ]
    )
    
    # Create and play game
    game = Game.create_game(config, rating_manager)
    await game.play()
    game.display_final_results()
    
    # Generate rating report
    rating_manager.generate_rating_report()
    
    return game

async def run_tournament():
    """
    Run a tournament with multiple games to build up Elo ratings.
    """
    print("\n=== Running a tournament with multiple games ===")
    
    # Create rating manager with custom Elo config
    elo_config = EloConfig(
        initial_rating=1200,  # Starting rating
        k_factor=24,          # How quickly ratings change
        scale_factor=400      # Standard Elo scale factor
    )
    rating_manager = RatingManager(data_dir="data/tournament", elo_config=elo_config)
    
    # Define different model configurations for the tournament
    # Each model will have exactly 2 agents
    agents_per_model = 2
    models = [
        ModelConfig("deepseek-r1-32b", "deepseek/deepseek-r1-distill-qwen-32b", agents_per_model),
        ModelConfig("deepseek-r1-1.5b", "deepseek/deepseek-r1-distill-qwen-1.5b", agents_per_model),
        ModelConfig("llama-2-7b", "meta-llama/llama-2-7b", agents_per_model),
        ModelConfig("mistral-7b", "mistralai/mistral-7b", agents_per_model)
    ]
    
    # Play multiple games with different model combinations
    for i in range(5):
        print(f"\n--- Tournament Game {i+1} ---")
        
        # Create a different combination of models for each game
        # Always use exactly 2 models per game
        game_models = [models[i % len(models)], models[(i + 1) % len(models)]]
        
        config = GameConfig(
            num_actions=16,
            num_turns=5,  # Shorter games for the tournament
            agents_per_model=agents_per_model,  # Enforce equal agents per model
            models=game_models
        )
        
        # Create and play game
        game = Game.create_game(config, rating_manager)
        await game.play()
        game.display_final_results()
    
    # Generate comprehensive report
    print("\n=== Tournament Results ===")
    rating_manager.generate_rating_report()
    
    # Export match history to CSV
    rating_manager.export_to_csv("data/tournament/match_history.csv")

async def main():
    """Main function to run examples."""
    # Ensure data directories exist
    os.makedirs("data/ratings", exist_ok=True)
    os.makedirs("data/tournament", exist_ok=True)
    
    # Run single game example
    await run_single_game()
    
    # Run tournament example
    await run_tournament()
    
    print("\n=== All examples completed ===")
    print("Rating data and visualizations have been saved to the data/ directory.")

if __name__ == "__main__":
    asyncio.run(main()) 