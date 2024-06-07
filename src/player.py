import random

# Define constants
NUM_ACTIONS = 16

class Player:
    def __init__(self, name: str):
        self.name = name
        self.score = 0
    
    def get_name(self) -> str:
        return self.name
    
    def get_bet(self, num_actions: int) -> int:
        return random.randint(0, num_actions - 1)
    
    def choose_action(self, num_actions: int, bet_influences: list[int]) -> int:
        return random.randint(0, num_actions - 1)
    
    def calculate_bet_influences(self, players: list['Player'], public_bets: list[int]) -> list[int]:
        bet_influences = [0] * NUM_ACTIONS
        for i, bet in enumerate(public_bets):
            if players[i] != self:
                bet_influences[bet] += 1
        return bet_influences
    
    def add_points(self, points: float) -> None:
        self.score += points