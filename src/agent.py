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
        if VERBOSE:
            print(f"\nTrying to extract {xml_tag} from response:\n{model_response}\n")
        
        # First try to extract thoughts if present
        if "<think>" in model_response:
            thoughts = model_response[model_response.find("<think>")+len("<think>"):model_response.find("</think>")]
            if VERBOSE:
                print(f"Model {self.model_name} thoughts:\n {thoughts}")

        # Clean up the response - remove markdown, extra tags, and whitespace
        model_response = model_response.replace('```xml', '').replace('```', '')
        model_response = model_response.replace('**', '')
        model_response = model_response.replace('</message>', '')
        model_response = model_response.replace('</answer>', '')
        model_response = model_response.replace('<answer>', '')
        model_response = model_response.replace('(answer)', '')
        
        # 1. Try regex patterns first
        patterns = [
            # Standard format
            rf"<{xml_tag}>\s*(.*?)\s*</{xml_tag}>",
            # Brackets instead of angle brackets
            rf"\[{xml_tag}>\s*(.*?)\s*</{xml_tag}\]",
            rf"\[{xml_tag}\]\s*(.*?)\s*\[/{xml_tag}\]",
            # Incomplete/malformed tags
            rf"<{xml_tag}>\s*(\d+)(?:</|$)",
            rf"\[{xml_tag}>\s*(\d+)(?:\]|$)",
            rf"{xml_tag}>\s*(\d+)",
            # Just the number with identifier
            rf"<{xml_tag}>(\d+)",
            rf"\[{xml_tag}\](\d+)",
            # Handle cases where wrong tag type is present but has valid number
            r"<(?:action|personal_bet)>(\d+)</(?:action|personal_bet)>",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, model_response, re.DOTALL | re.IGNORECASE)
            for match in matches:
                value = match.group(1).strip()
                # If we find a valid number, return it immediately
                if value.isdigit() and 0 <= int(value) < NUM_ACTIONS:
                    return value

        # 2. Try string-based pattern matching if regex fails
        try:
            # Common tag formats including variations
            tag_starts = [
                f"<{xml_tag}>", 
                f"[{xml_tag}>",
                f"{xml_tag}>",
                "<action>",  # Also look for alternate tag
                "<personal_bet>",  # Also look for alternate tag
            ]
            tag_ends = [
                f"</{xml_tag}>", 
                f"]",
                "\n",
                "</action>",
                "</personal_bet>",
            ]
            
            # Try each combination of start and end tags
            for start_tag in tag_starts:
                if start_tag in model_response:
                    start_idx = model_response.find(start_tag) + len(start_tag)
                    
                    # Find the closest end tag after the start tag
                    end_idx = len(model_response)
                    for end_tag in tag_ends:
                        pos = model_response.find(end_tag, start_idx)
                        if pos != -1 and pos < end_idx:
                            end_idx = pos
                    
                    value = model_response[start_idx:end_idx].strip()
                    
                    # Try to extract a number from the value
                    if value.isdigit() and 0 <= int(value) < NUM_ACTIONS:
                        return value

            # 3. Last resort: scan for any valid number in the entire response
            numbers = re.findall(r'\b(\d+)\b', model_response)
            for num in numbers:
                if 0 <= int(num) < NUM_ACTIONS:
                    return num

        except Exception as e:
            if VERBOSE:
                print(f"String parsing failed: {e}")

        if VERBOSE:
            print(f"Warning: {xml_tag} not found in response: {model_response}")
        return None

    async def generate_and_extract(self, content: str, extract_tag: str) -> int:
        self.messages.append({"role": "user", "content": content})
        response = await chat_with_model_async(messages=self.messages, model_name=self.model_name)
        
        # Handle error responses from the model
        if response.startswith("Error:"):
            print(f"Model error: {response}")
            return random.randint(0, NUM_ACTIONS - 1)
        
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