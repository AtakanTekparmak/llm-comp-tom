from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ModelConfig:
    name: str  # Short name for the model
    api_name: str  # Full API name/path
    num_agents: int  # Number of agents to create with this model

@dataclass
class GameConfig:
    num_actions: int
    num_turns: int
    models: List[ModelConfig] = None

    def __post_init__(self):
        if self.models is None:
            raise ValueError("Models must be provided, in format: ModelConfig(name='model_name', api_name='api_name', num_agents=num_agents)")
        if self.num_turns is None:
            raise ValueError("num_turns must be provided")
        if self.num_actions is None:
            raise ValueError("num_actions must be provided")
    
    @property
    def num_players(self) -> int:
        return sum(model.num_agents for model in self.models)
    
    @property
    def models_dict(self) -> Dict[str, str]:
        """Returns mapping of short names to API names"""
        return {model.name: model.api_name for model in self.models} 