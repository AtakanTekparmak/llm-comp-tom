from src.game import Game
from src.config import GameConfig, ModelConfig
import asyncio

async def main():
    # Create game configuration
    config = GameConfig(
        num_actions=16,
        num_turns=4,
        models=[
            ModelConfig("deepseek-r1-32b", "deepseek/deepseek-r1-distill-qwen-32b", 8),
            ModelConfig("deepseek-r1-1.5b", "deepseek/deepseek-r1-distill-qwen-1.5b", 8)
        ]
    )

    # Create and play game
    game = Game.create_game(config)
    await game.play()
    game.display_final_results()

if __name__ == "__main__":
    asyncio.run(main())