from src.player import Player
from src.settings import NUM_ACTIONS, NUM_TURNS, VERBOSE, NUM_PLAYERS
import asyncio

class Game:
    def __init__(self, players: list[Player]):
        self.players = players
        self.turn = 0
        self.previous_actions = []

    async def play(self) -> None:
        while self.turn < NUM_TURNS:
            public_bets = await self.get_public_bets()
            private_actions = await self.get_private_actions(public_bets)

            if VERBOSE:
                print(f"Turn {self.turn} public bets:\n {public_bets}\n~~~~~~~~~~~")
                print(f"Turn {self.turn} private actions:\n {private_actions}\n~~~~~~~~~~~")

            scores = self.calculate_scores(public_bets, private_actions)
            self.update_player_points(scores)
            self.previous_actions = private_actions
            print(f"Turn {self.turn} scores: {scores}")
            self.turn += 1

    async def get_public_bets(self) -> list[int]:
        tasks = [player.get_bet(self.previous_actions) for player in self.players]
        return await asyncio.gather(*tasks)

    async def get_private_actions(self, public_bets: list[int]) -> list[int]:
        tasks = [player.choose_action(self.turn, public_bets) for player in self.players]
        return await asyncio.gather(*tasks)

    def calculate_scores(self, public_bets: list[int], private_actions: list[int]) -> list[float]:
        action_counts = [0] * NUM_ACTIONS
        for action in private_actions:
            action_counts[action] += 1

        scores = [0] * NUM_PLAYERS
        for player_idx, (bet, action) in enumerate(zip(public_bets, private_actions)):
            score = action_counts[action] + 0.5 * action_counts[bet]
            scores[player_idx] = score
        return scores

    def update_player_points(self, scores: list[float]) -> None:
        for player, score in zip(self.players, scores):
            player.add_points(score)

    def get_overall_scores(self) -> dict[str, float]:
        return {player.get_name(): player.score for player in self.players}