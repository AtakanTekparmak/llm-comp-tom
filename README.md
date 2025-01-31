# llm-comp-tom

## Introduction

The competitive game for this experiment is a **Mod Game with Public Betting**.

## Game Overview
- The game consists of `NUM_PLAYERS` players and `NUM_ACTIONS` possible actions.
- The game is played for `NUM_TURNS` turns.

## Game Rules
1. Each turn:
   - Each player publicly bets on the number they think will come up the most.
   - Each player then privately chooses a number/action.
   - After private votes are revealed, players receive points based on the scoring rubric.

2. The game ends after 100 turns.

## Scoring Rubric
- Players receive one point per other player that chose their selected number/action minus one.
- Players receive 0.5 points per player that chose the number they bet on.

## Installation
To install the required packages, run the following command:
```bash
make install
```

## Environment Setup
To set up the environment, run the following command:
```bash
make copy-env
```
This will create a `.env` file in the root directory. Then, add your OpenRouter API key to the `.env` file.

## Quickstart

An example experiment setup is shown below (and provided in `main.py`). [OpenRouter](https://openrouter.ai/) is used as inference provider.

```python
from src.game import Game
from src.config import GameConfig, ModelConfig
import asyncio

async def main():
    # Create game configuration
    config = GameConfig(
        num_actions=16, # Number of possible actions
        num_turns=4, # Number of turns
        models=[
            ModelConfig("deepseek-r1-32b", "deepseek/deepseek-r1-distill-qwen-32b", 8), # Model name, model API name, number of agents
            ModelConfig("deepseek-r1-1.5b", "deepseek/deepseek-r1-distill-qwen-1.5b", 8)
        ]
    )

    # Create and play game
    game = Game.create_game(config)
    await game.play()
    game.display_final_results()

if __name__ == "__main__":
    asyncio.run(main())
```

## Usage
To run the program, run the following command:
```bash
make run
```
