import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter settings
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MAX_TOKENS = 32768

# General settings
VERBOSE = False
BET_REWARD = 0.5
ACTION_REWARD = 4.0

# System prompt
SYSTEM_PROMPT_PATH = "src/system_prompt.txt"
SYSTEM_PROMPT = None  # Will be set dynamically

def load_system_prompt(num_actions: int) -> str:
    try:
        with open(SYSTEM_PROMPT_PATH, "r") as f:
            prompt = f.read()
            max_num = num_actions - 1
            # Replace hardcoded numbers with dynamic values
            prompt = prompt.replace("0 to 15", f"0 to {max_num}")
            prompt = prompt.replace("(0-15)", f"(0-{max_num})")
            prompt = prompt.replace("+1 point per player choosing your action", f"+{ACTION_REWARD} points per player choosing your action")
            prompt = prompt.replace("+0.5 points per player choosing your bet", f"+{BET_REWARD} points per player choosing your bet")
            return prompt
    except FileNotFoundError:
        raise FileNotFoundError(f"System prompt file not found at {SYSTEM_PROMPT_PATH}")

