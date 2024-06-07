from src.player import Player
from src.config import NUM_ACTIONS, NUM_PLAYERS, NUM_TURNS


class GameConfig:
    """A class to store the configuration for a game."""
    def __init__(self, player_configs: list[tuple[str, int]]):
        self.player_configs = player_configs
    
    def create_players(self) -> list[Player]:
        players = []
        for name, count in self.player_configs:
            players.extend([Player(name) for _ in range(count)])
        return players

class Game:
    def __init__(self, config: GameConfig):
        self.config = config
        self.players = self.config.create_players()
        self.turn = 0
    
    def is_game_over(self) -> bool:
        return self.turn >= NUM_TURNS
    
    def play(self) -> None:
        while not self.is_game_over():
            # Step 1: Each player publicly bets on a number
            public_bets = self.get_public_bets()
            
            # Step 2: Each player privately chooses a number/action based on the public bets
            private_actions = self.get_private_actions(public_bets)
            
            # Step 3: Calculate scores and update player points
            scores = self.calculate_scores(public_bets, private_actions)
            self.update_player_points(scores)
            
            self.turn += 1
    
    def get_public_bets(self) -> list[int]:
        public_bets = []
        for player in self.players:
            bet = player.get_bet(NUM_ACTIONS)
            public_bets.append(bet)
        return public_bets
    
    def get_private_actions(self, public_bets: list[int]) -> list[int]:
        private_actions = []
        for player in self.players:
            action = self.get_player_action(player, public_bets)
            private_actions.append(action)
        return private_actions
    
    def get_player_action(self, player: Player, public_bets: list[int]) -> int:
        # Calculate the influence of each player's public bet on the current player's action
        bet_influences = player.calculate_bet_influences(self.players, public_bets)
        
        # Use the bet influences to determine the player's action
        action = player.choose_action(NUM_ACTIONS, bet_influences)
        
        return action
    
    def calculate_scores(self, public_bets: list[int], private_actions: list[int]) -> list[float]:
        scores = [0] * NUM_PLAYERS
        action_counts = [0] * NUM_ACTIONS
        
        for action in private_actions:
            action_counts[action] += 1
        
        for player, action in enumerate(private_actions):
            scores[player] += action_counts[action] - 1
            
        for player, bet in enumerate(public_bets):
            scores[player] += 0.5 * action_counts[bet]
        
        return scores
    
    def update_player_points(self, scores: list[float]) -> None:
        for player, score in zip(self.players, scores):
            player.add_points(score)
    
    def get_overall_scores(self) -> dict[str, float]:
        overall_scores = {}
        for player in self.players:
            name = player.get_name()
            if name in overall_scores:
                overall_scores[name] += player.score
            else:
                overall_scores[name] = player.score
        return overall_scores