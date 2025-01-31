import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter settings
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MAX_TOKENS = 32768

# General settings
VERBOSE = False

# System prompt
SYSTEM_PROMPT_PATH = "src/system_prompt.txt"
try:
    with open(SYSTEM_PROMPT_PATH, "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    raise FileNotFoundError(f"System prompt file not found at {SYSTEM_PROMPT_PATH}")

