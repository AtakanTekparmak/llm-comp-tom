from src.model import Model, OllamaModel

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

# Define constants
MODELS = {
    "qwen2-0.5": "Qwen/Qwen2-0.5B-Instruct-MLX",
    "qwen2-1.5": "Qwen/Qwen2-1.5B-Instruct-MLX",
    "qwen2-7":   "qwen2:7b-instruct-fp16"
}

class Agent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.messages = [
            {"role": "system", "content": system_prompt},
        ] 
        self.model = self.get_model_by_name(name)

    def get_model_by_name(self, model_name: str):
        """Returns the model based on the name."""
        #return Model(model_name=MODELS[model_name])
        return OllamaModel(model_name=MODELS[model_name])
    
    def extract_data(self, model_response: str, xml_tag: str):
        """Extracts data from the model response using the specified XML tag."""
        # Parse the XML response
        try:
            print("Model Response: \n", model_response)
            # Get the model response after the specified XML tag
            start_tag = "<" + xml_tag + ">"
            end_tag = "</" + xml_tag + ">"
            data = model_response[model_response.index(start_tag) + len(start_tag):model_response.index(end_tag)]
            return data
        except ParseError:
            print("Parse Error for model response: \n", model_response)
            return None
    
    def start_playing(self) -> int:
        """
        Starts the game by sending the system prompt. 
        Returns the personal bet from the agent.
        """
        # Add game start prompt to messages
        self.messages.append({"role": "user", "content": "<game_start>"})

        # Generate the first response
        #response = self.model.generate(messages=self.messages, verbose=False)
        response = self.model.generate(messages=self.messages)

        # Extract the personal_bet from the response
        personal_bet = self.extract_data(response, "personal_bet")
        print("Personal Bet: ", personal_bet)

        # Add the personal bet to the messages
        self.messages.append({"role": "assistant", "content": personal_bet})
        
        return personal_bet
    
    def reveal_bets(self, round_number: int, public_bets: list[int]) -> int:
        """
        Reveals the public bets to the agent.
        Returns the action from the agent.
        """
        # Construct the bets data
        bets_data = "<round_number>" + str(round_number) + "</round_number>\n<bets>\n"
        for bet in public_bets:
            bets_data += "Player " + str(public_bets.index(bet)) + " : " + str(bet) + "\n"
        bets_data += "</bets>"

        # Add the public bets to the messages
        self.messages.append({"role": "user", "content": bets_data})

        # Generate the response
        #response = self.model.generate(messages=self.messages, verbose=False)
        response = self.model.generate(messages=self.messages)

        # Extract the action from the response
        action = self.extract_data(response, "action")

        # Add the action to the messages
        self.messages.append({"role": "assistant", "content": action})

        return action

    def reveal_score_and_actions(self, agent_score: float, opponent_actions: list[int]) -> int:
        """
        Reveals the agent's score and opponent actions to the agent.
        Returns the personal bet from the agent.
        """
        # Construct the score and actions data
        score_actions_data = "<score>" + str(agent_score) + "</score>\n<opponent_choices>\n"
        for action in opponent_actions:
            score_actions_data += "Player " + str(opponent_actions.index(action) + " : " + str(action) + "\n")
        score_actions_data += "</opponent_choices>"

        # Add the score and actions data to the messages
        self.messages.append({"role": "user", "content": score_actions_data})

        # Generate the response
        response = self.model.generate(messages=self.messages, verbose=False)

        # Extract the personal bet from the response
        personal_bet = self.extract_data(response, "personal_bet")

        # Add the feedback to the messages
        self.messages.append({"role": "assistant", "content": personal_bet})

        return personal_bet