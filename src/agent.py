class Agent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.chat_history = []
        self.model = self.get_model_by_name(name)

    def get_model_by_name(self, model_name: str):
        return None
    
    def start_playing(self):
        raise NotImplementedError("start_playing method not implemented")
    
    def add_round(self, round_data: dict):
        raise NotImplementedError("add_round method not implemented")