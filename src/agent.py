import re
from src.model import chat_with_model_async
from src.settings import NUM_ACTIONS, VERBOSE
import random
import asyncio

class Agent:
    def __init__(self, name: str, model_name: str, system_prompt: str):
        self.name = name
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.messages = [
            {"role": "system", "content": system_prompt},
        ]

    def extract_data(self, model_response: str, xml_tag: str):
        if "<think>" in model_response:
            thoughts = model_response[model_response.find("<think>")+len("<think>"):model_response.find("</think>")]
            if VERBOSE:
                print(f"Model {self.model_name} thoughts:\n {thoughts}")

        patterns = [
            rf"<{xml_tag}>\s*(.*?)\s*</{xml_tag}>",
            rf"<{xml_tag}>(.*?)</{xml_tag}>",
            rf"\[{xml_tag}>(.*?)</{xml_tag}\]",
            rf"\[(xml_tag)>\s(.*?)\s</{xml_tag}\]",
            rf"\[{xml_tag}>(.*?)\]",
            rf"<{xml_tag}>(.*?)(?:<|$)",
            rf"<{xml_tag}>\s*(\d+)",
            rf"{xml_tag}>\s*(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, model_response, re.DOTALL | re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                number_match = re.search(r'\d+', value)
                if number_match:
                    return number_match.group(0)
                return value

        print(f"Warning: {xml_tag} not found in response: {model_response}")
        return None

    async def generate_and_extract(self, content: str, extract_tag: str) -> int:
        self.messages.append({"role": "user", "content": content})
        response = await chat_with_model_async(messages=self.messages, model_name=self.model_name)
        self.messages.append({"role": "assistant", "content": response})
        
        extracted_value = self.extract_data(response, extract_tag)
        if extracted_value is None:
            return random.randint(0, NUM_ACTIONS - 1)
        
        try:
            value = int(extracted_value)
            if 0 <= value < NUM_ACTIONS:
                return value
            else:
                print(f"Value out of range: {value}")
                return random.randint(0, NUM_ACTIONS - 1)
        except ValueError:
            print(f"Invalid {extract_tag}: {extracted_value}")
            return random.randint(0, NUM_ACTIONS - 1)

    async def start_playing(self) -> int:
        return await self.generate_and_extract("<game_start>", "personal_bet")

    async def reveal_bets(self, round_number: int, public_bets: list[int]) -> int:
        bets_data = f"<round_number>{round_number}</round_number>\n<bets>\n" + "\n".join(f"Player {i}: {bet}" for i, bet in enumerate(public_bets)) + "\n</bets>"
        return await self.generate_and_extract(bets_data, "action")

    async def reveal_score_and_actions(self, agent_score: float, opponent_actions: list[int]) -> int:
        score_actions_data = f"<score>{agent_score}</score>\n<opponent_choices>\n" + "\n".join(f"Player {i}: {action}" for i, action in enumerate(opponent_actions)) + "\n</opponent_choices>"
        return await self.generate_and_extract(score_actions_data, "personal_bet")