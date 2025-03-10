from dataclasses import dataclass
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

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
    agents_per_model: int = None  # New field for enforcing equal agents per model

    def __post_init__(self):
        if self.models is None:
            raise ValueError("Models must be provided, in format: ModelConfig(name='model_name', api_name='api_name', num_agents=num_agents)")
        if self.num_turns is None:
            raise ValueError("num_turns must be provided")
        if self.num_actions is None:
            raise ValueError("num_actions must be provided")
            
        # Check if we need to enforce equal agents per model
        if self.agents_per_model is not None:
            # Override num_agents in each ModelConfig to ensure equal distribution
            for model in self.models:
                if model.num_agents != self.agents_per_model:
                    logger.warning(f"Overriding num_agents for {model.name} from {model.num_agents} to {self.agents_per_model}")
                    model.num_agents = self.agents_per_model
        else:
            # Check if all models have the same number of agents
            if len(self.models) > 1:
                agent_counts = [model.num_agents for model in self.models]
                if len(set(agent_counts)) > 1:
                    # Models have different agent counts
                    logger.warning(f"Models have different agent counts: {agent_counts}. This may affect rating comparisons.")
    
    @property
    def num_players(self) -> int:
        return sum(model.num_agents for model in self.models)
    
    @property
    def models_dict(self) -> Dict[str, str]:
        """Returns mapping of short names to API names"""
        return {model.name: model.api_name for model in self.models} 