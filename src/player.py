from src.agent import Agent
from src.settings import SYSTEM_PROMPT
from src.config import GameConfig

class Player:
    def __init__(self, name: str, model_name: str, config: GameConfig):
        self.name = name
        self.model_name = model_name
        self.score = 0
        self.agent = Agent(name, model_name, SYSTEM_PROMPT, config)

    def get_name(self) -> str:
        return f"{self.name} ({self.model_name})"

    async def start_playing(self) -> int:
        return await self.agent.generate_and_extract("<game_start>", "personal_bet")

    async def get_bet(self, previous_actions: list[int]) -> int:
        return await self.agent.reveal_score_and_actions(self.score, previous_actions)

    async def choose_action(self, turn: int, public_bets: list[int]) -> int:
        return await self.agent.reveal_bets(turn, public_bets)

    def add_points(self, points: float) -> None:
        self.score += points