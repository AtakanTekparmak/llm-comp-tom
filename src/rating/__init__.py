"""
Rating system for benchmarking LLMs.

This submodule provides an implementation of the Elo rating system for tracking
and comparing the performance of different language models over time.
"""

from src.rating.core import EloRating, EloConfig
from src.rating.manager import RatingManager, GameResult

__all__ = [
    'EloRating', 
    'EloConfig',
    'RatingManager',
    'GameResult'
] 