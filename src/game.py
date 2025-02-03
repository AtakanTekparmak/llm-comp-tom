from src.player import Player
from src.config import GameConfig
from src.settings import VERBOSE, ACTION_REWARD, BET_REWARD
import asyncio

class Game:
    def __init__(self, players: list[Player], config: GameConfig):
        self.players = players
        self.config = config
        self.turn = 0
        self.previous_actions = []
        # Initialize score history dictionary
        self.model_score_history = {model.name: [] for model in config.models}

    @classmethod
    def create_game(cls, config: GameConfig) -> 'Game':
        players = []
        for model_config in config.models:
            for i in range(model_config.num_agents):
                player_number = len(players) + 1
                players.append(Player(f"Player{player_number}", model_config.name, config))
        return cls(players, config)

    def display_final_results(self) -> None:
        print("\n=== Final Results ===")
        self.display_overall_scores()
        self.display_average_model_scores()
        self.display_score_history()

    def display_overall_scores(self) -> None:
        print("\nOverall Scores:")
        overall_scores = self.get_overall_scores()
        for player_name, score in overall_scores.items():
            print(f"{player_name}: {score:.2f}")

    def display_average_model_scores(self) -> None:
        print("\nAverage Scores per Model:")
        model_scores = {model.name: [] for model in self.config.models}
        for player in self.players:
            model_scores[player.model_name].append(player.score)
        
        for model_name, scores in model_scores.items():
            avg_score = sum(scores) / len(scores)
            print(f"{model_name}: {avg_score:.2f}")

    def display_score_history(self) -> None:
        print("\nScore History per Model:")
        score_history = self.get_model_score_history()
        for model_name, history in score_history.items():
            print(f"\n{model_name}:")
            for turn, score in enumerate(history):
                print(f"Turn {turn}: {score:.2f}")

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
            score = ACTION_REWARD * action_counts[action] + BET_REWARD * action_counts[bet]
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