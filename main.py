from src.game import Game
from src.player import Player
from src.config import GameConfig, ModelConfig
import asyncio

async def main():
    # Example of creating a custom configuration
    config = GameConfig(
        num_actions=16,
        num_turns=8,
        models=[
            ModelConfig("deepseek-r1-32b", "deepseek/deepseek-r1-distill-qwen-32b", 8),
            ModelConfig("deepseek-r1-1.5b", "deepseek/deepseek-r1-distill-qwen-1.5b", 8)
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
    
    print("\n=== Final Results ===")
    
    print("\nOverall Scores:")
    overall_scores = game.get_overall_scores()
    for player_name, score in overall_scores.items():
        print(f"{player_name}: {score:.2f}")
    
    print("\nAverage Scores per Model:")
    model_scores = {model.name: [] for model in config.models}
    for player in players:
        model_scores[player.model_name].append(player.score)
    
    for model_name, scores in model_scores.items():
        avg_score = sum(scores) / len(scores)
        print(f"{model_name}: {avg_score:.2f}")

    print("\nScore History per Model:")
    score_history = game.get_model_score_history()
    for model_name, history in score_history.items():
        print(f"\n{model_name}:")
        for turn, score in enumerate(history):
            print(f"Turn {turn}: {score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())