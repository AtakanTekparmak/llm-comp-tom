# llm-comp-tom

## Introduction

The competitive game for this experiment is a **Mod Game (N=16) with Public Betting**.

## Game Overview
- The game consists of 64 players and 16 possible numbers/actions.
- The game is played for 100 turns.

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

## Usage
To run the program, run the following command:
```bash
make run
```
