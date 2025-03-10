from src.player import Player
from src.config import GameConfig
from src.settings import VERBOSE, ACTION_REWARD, BET_REWARD
from src.rating.manager import RatingManager, GameResult
import asyncio

class Game:
    def __init__(self, players: list[Player], config: GameConfig, rating_manager: RatingManager = None):
        self.players = players
        self.config = config
        self.turn = 0
        self.previous_actions = []
        # Initialize score history dictionary
        self.model_score_history = {model.name: [] for model in config.models}
        
        # Initialize rating manager if provided
        self.rating_manager = rating_manager

    @classmethod
    def create_game(cls, config: GameConfig, rating_manager: RatingManager = None) -> 'Game':
        players = []
        for model_config in config.models:
            for i in range(model_config.num_agents):
                player_number = len(players) + 1
                players.append(Player(f"Player{player_number}", model_config.name, config))
        return cls(players, config, rating_manager)

    def display_final_results(self) -> None:
        print("\n=== Final Results ===")
        self.display_overall_scores()
        self.display_average_model_scores()
        self.display_score_history()
        
        # Display Elo ratings if rating manager is available
        if self.rating_manager:
            self.display_model_ratings()

    def display_overall_scores(self) -> None:
        print("\nOverall Scores:")
        overall_scores = self.get_overall_scores()
        for player_name, score in overall_scores.items():
            print(f"{player_name}: {score:.2f}")

    def display_average_model_scores(self) -> None:
        print("\nAverage Scores per Model:")
        model_scores = self._get_model_scores()
        
        for model_name, avg_score in model_scores.items():
            print(f"{model_name}: {avg_score:.2f}")

    def display_score_history(self) -> None:
        print("\nScore History per Model:")
        score_history = self.get_model_score_history()
        for model_name, history in score_history.items():
            print(f"\n{model_name}:")
            for turn, score in enumerate(history):
                print(f"Turn {turn}: {score:.2f}")
    
    def display_model_ratings(self) -> None:
        """Display the Elo ratings of models if available."""
        if not self.rating_manager:
            return
            
        print("\nElo Ratings:")
        rankings = self.rating_manager.get_model_rankings()
        for i, (model_name, rating) in enumerate(rankings, 1):
            print(f"{i}. {model_name}: {rating}")

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
        
        # After the game is over, update Elo ratings if rating manager is available
        if self.rating_manager:
            self.update_model_ratings()

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
        model_scores = self._get_model_scores(use_average=True)
        
        # Store average score for each model
        for model_name, avg_score in model_scores.items():
            self.model_score_history[model_name].append(avg_score)

    def _get_model_scores(self, use_average: bool = True) -> dict:
        """
        Get scores for each model.
        
        Args:
            use_average: If True, return average scores, otherwise return all scores.
            
        Returns:
            Dictionary mapping model name to score or list of scores.
        """
        # Group scores by model
        model_scores = {model.name: [] for model in self.config.models}
        for player in self.players:
            model_scores[player.model_name].append(player.score)
        
        # Calculate average if requested
        if use_average:
            return {
                model_name: sum(scores) / len(scores) if scores else 0
                for model_name, scores in model_scores.items()
            }
        
        return model_scores

    def get_model_score_history(self) -> dict:
        return self.model_score_history

    def get_overall_scores(self) -> dict[str, float]:
        return {player.get_name(): player.score for player in self.players}
    
    def update_model_ratings(self) -> None:
        """Update Elo ratings based on game results."""
        if not self.rating_manager:
            return
            
        # Get the final average scores for each model
        model_scores = self._get_model_scores(use_average=True)
            
        # Create a game result and process it
        result = GameResult(
            models=list(model_scores.keys()),
            scores=model_scores
        )
        
        self.rating_manager.process_game_result(result)
        print("\nUpdated Elo ratings based on game results.")