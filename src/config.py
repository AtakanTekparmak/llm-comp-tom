import tomllib

# Define constants
NUM_ACTIONS = 16
NUM_PLAYERS = 32
NUM_TURNS = 100

def load_config(config_path: str = "config.toml") -> dict:
    """Loads the configuration file."""
    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

def get_system_prompt():
    """Retrieves the system prompt."""
    return load_config()["SYSTEM_PROMPT"]