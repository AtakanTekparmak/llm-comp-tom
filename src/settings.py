import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter settings
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MAX_TOKENS = 16384

# Game settings
NUM_ACTIONS = 16
NUM_PLAYERS = 8
NUM_TURNS = 2

# Model settings
MODELS = {
    "deepseek-r1-70b": "deepseek/deepseek-r1-distill-llama-70b",
    "deepseek-r1-32b": "deepseek/deepseek-r1-distill-qwen-32b",
    "deepseek-r1-14b": "deepseek/deepseek-r1-distill-qwen-14b"
}

# General settings
VERBOSE = True

# System prompt
SYSTEM_PROMPT_PATH = "src/system_prompt.txt"
try:
    with open(SYSTEM_PROMPT_PATH, "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    raise FileNotFoundError(f"System prompt file not found at {SYSTEM_PROMPT_PATH}")

