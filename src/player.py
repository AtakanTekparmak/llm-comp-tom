import random

from src.agent import Agent
from src.config import get_system_prompt, NUM_ACTIONS

class Player:
    def __init__(self, name: str):
        self.name = name
        self.score = 0
        self.agent = Agent(name, get_system_prompt())
    
    def get_name(self) -> str:
        return self.name
    
    def start_playing(self) -> int:
        return self.agent.start_playing()
    
    def get_bet(self, previous_actions: list[int]) -> int:
        return self.agent.reveal_score_and_actions(self.score, previous_actions)
    
    def choose_action(self, turn: int, bet_influences: list[int]) -> int:
        return self.agent.reveal_bets(turn, bet_influences)
    
    def calculate_bet_influences(self, players: list['Player'], public_bets: list[int]) -> list[int]:
        return public_bets
    
    def add_points(self, points: float) -> None:
        self.score += points