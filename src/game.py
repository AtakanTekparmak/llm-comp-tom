from src.player import Player
from src.config import GameConfig
from src.settings import VERBOSE
import asyncio

class Game:
    def __init__(self, players: list[Player], config: GameConfig):
        self.players = players
        self.config = config
        self.turn = 0
        self.previous_actions = []
        # Initialize score history dictionary
        self.model_score_history = {model.name: [] for model in config.models}

    async def play(self) -> None:
        while self.turn < self.config.num_turns:
            public_bets = await self.get_public_bets()
            private_actions = await self.get_private_actions(public_bets)

            scores = self.calculate_scores(public_bets, private_actions)
            self.update_player_points(scores)
            self.update_model_score_history()
            self.previous_actions = private_actions
            print(f"\nTurn {self.turn}:")
            print(f"Public bets: {public_bets}")
            print(f"Actions: {private_actions}")
            print(f"Scores: {scores}")
            self.turn += 1

    async def get_public_bets(self) -> list[int]:
        tasks = [player.get_bet(self.previous_actions) for player in self.players]
        return await asyncio.gather(*tasks)

    async def get_private_actions(self, public_bets: list[int]) -> list[int]:
        tasks = [player.choose_action(self.turn, public_bets) for player in self.players]
        return await asyncio.gather(*tasks)

    def calculate_scores(self, public_bets: list[int], private_actions: list[int]) -> list[float]:
        action_counts = [0] * self.config.num_actions
        for action in private_actions:
            action_counts[action] += 1

        scores = [0] * self.config.num_players
        for player_idx, (bet, action) in enumerate(zip(public_bets, private_actions)):
            score = action_counts[action] + 0.5 * action_counts[bet]
            scores[player_idx] = score
        return scores

    def update_player_points(self, scores: list[float]) -> None:
        for player, score in zip(self.players, scores):
            player.add_points(score)

    def update_model_score_history(self) -> None:
        # Group current scores by model
        model_scores = {model.name: [] for model in self.config.models}
        for player in self.players:
            model_scores[player.model_name].append(player.score)
        
        # Calculate and store average score for each model
        for model_name, scores in model_scores.items():
            if scores:  # Add check to prevent division by zero
                avg_score = sum(scores) / len(scores)
                self.model_score_history[model_name].append(avg_score)

    def get_model_score_history(self) -> dict:
        return self.model_score_history

    def get_overall_scores(self) -> dict[str, float]:
        return {player.get_name(): player.score for player in self.players}