from src.game import Game
from src.player import Player
from src.config import GameConfig, ModelConfig
import asyncio

async def main():
    # Example of creating a custom configuration
    config = GameConfig(
        num_actions=16,
        num_turns=16,
        models=[
            #ModelConfig("deepseek-r1-70b", "deepseek/deepseek-r1-distill-llama-70b", 8),
            #ModelConfig("deepseek-r1-14b", "deepseek/deepseek-r1-distill-qwen-14b", 8)
            ModelConfig("qwen-2.5-7b", "qwen/qwen-2.5-7b-instruct", 16),
            ModelConfig("qwen-2.5-72b", "qwen/qwen-2.5-72b-instruct", 16)
        ]
    )

    # Create players based on configuration
    players = []
    for model_config in config.models:
        for i in range(model_config.num_agents):
            player_number = len(players) + 1
            players.append(Player(f"Player{player_number}", model_config.name, config))

    game = Game(players, config)
    await game.play()
    overall_scores = game.get_overall_scores()
    print("\nOverall Scores:")
    for player_name, score in overall_scores.items():
        print(f"{player_name}: {score}")
    
    # Calculate and display average scores per model
    model_scores = {model.name: [] for model in config.models}
    for player in players:
        model_scores[player.model_name].append(player.score)
    
    print("\nAverage Scores per Model:")
    for model_name, scores in model_scores.items():
        avg_score = sum(scores) / len(scores)
        print(f"{model_name}: {avg_score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())