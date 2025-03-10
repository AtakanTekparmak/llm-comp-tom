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
from src.rating.manager import RatingManager
import asyncio
import os

async def main():
    # Create data directory for ratings
    os.makedirs("data/ratings", exist_ok=True)
    
    # Create rating manager
    rating_manager = RatingManager(data_dir="data/ratings")
    
    # Create game configuration with equal agents per model
    config = GameConfig(
        num_actions=16,  # Number of possible actions
        num_turns=4,     # Number of turns
        agents_per_model=8,  # Ensure equal distribution of agents per model
        models=[
            ModelConfig("deepseek-r1-32b", "deepseek/deepseek-r1-distill-qwen-32b", 8),
            ModelConfig("deepseek-r1-1.5b", "deepseek/deepseek-r1-distill-qwen-1.5b", 8)
        ]
    )

    # Create and play game with rating manager
    game = Game.create_game(config, rating_manager)
    await game.play()
    game.display_final_results()
    
    # Generate a rating report
    rating_manager.generate_rating_report()

if __name__ == "__main__":
    asyncio.run(main())
```

## Usage
To run the program, run the following command:
```bash
make run
```

## Elo Rating System for LLM Benchmarking

The framework includes an Elo rating system for benchmarking LLMs. This system tracks and compares the relative performance of different models over time.

### How It Works

The Elo rating system calculates the relative skill levels of models based on game outcomes:

1. Each model has a rating (initially set to a default value, typically 1000).
2. When two models compete, their ratings are updated based on:
   - The expected outcome (calculated from their pre-match ratings)
   - The actual outcome of the match (derived from average scores of all agents for each model)
3. Models that perform better than expected gain rating points, while models that perform worse lose points.
4. The amount of points gained or lost depends on the K-factor (determines how quickly ratings can change).

The key advantage is that ratings are relative and only depend on match outcomes, not absolute scores. This makes it possible to add new models at any time without recalculating all previous ratings.

### Usage

To use the rating system:

```python
from src.game import Game
from src.config import GameConfig, ModelConfig
from src.rating.manager import RatingManager

# Create rating manager
rating_manager = RatingManager(data_dir="data/ratings")

# Create game configuration 
# Always use the same number of agents per model for fair comparisons
config = GameConfig(
    num_actions=16,
    num_turns=10,
    agents_per_model=4,  # Ensure equal number of agents per model
    models=[
        ModelConfig("model_a", "api_path_a", 4),
        ModelConfig("model_b", "api_path_b", 4)
    ]
)

# Create and play game with rating manager
game = Game.create_game(config, rating_manager)
await game.play()
game.display_final_results()

# Generate rating report
rating_manager.generate_rating_report()
```

To run the rating system example:
```bash
make run-ratings
```

### Features

- **Model-level Ratings**: Ratings are calculated based on the average performance of all agents for a model
- **Equal Agent Distribution**: The system supports enforcing equal numbers of agents per model
- **Persistence**: Saves ratings to disk to maintain historical data
- **Visualization**: Generates visualizations including:
  - Rating history over turns (showing how ratings evolve with each game turn)
  - Current ratings bar chart
  - Win probability matrix between models
- **Reporting**: Generates reports of model rankings and performance

### Configuration Options

The Elo rating system can be configured with these parameters:

```python
from src.rating.core import EloConfig
from src.rating.manager import RatingManager

# Custom Elo configuration
elo_config = EloConfig(
    initial_rating=1200,  # Starting rating for new models
    k_factor=24,          # How quickly ratings change
    scale_factor=400      # Scale factor in the Elo formula
)

# Create rating manager with custom config
rating_manager = RatingManager(
    data_dir="data/ratings",
    elo_config=elo_config
)
```

### Project Structure

The rating system is organized in a dedicated submodule:

```
src/
├── rating/              # Rating system submodule
│   ├── __init__.py      # Exports public API
│   ├── core.py          # Core Elo rating implementation
│   └── manager.py       # Rating manager for game integration
├── game.py              # Game implementation
└── ...
```

This modular structure makes the code more maintainable and extensible, allowing for future enhancements to the rating system without affecting the rest of the codebase.
