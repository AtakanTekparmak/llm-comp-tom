"""
Core Elo rating system implementation.

This module implements the core Elo rating system for tracking relative performance
of different models. It provides the mathematical foundation and basic operations
for the rating system.
"""

import math
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


@dataclass
class EloConfig:
    """Configuration for the Elo rating system."""
    initial_rating: int = 1000  # Starting rating for new models
    k_factor: int = 32          # K-factor determines how much ratings change after each game
    scale_factor: int = 400     # Scale factor in the Elo formula (standard is 400)


class EloRating:
    """
    Implementation of the Elo rating system for LLM benchmarking.
    
    The Elo rating system calculates relative skill levels between models
    based on game outcomes. When a model performs better than expected, its
    rating increases, and vice versa.
    """
    
    def __init__(self, config: Optional[EloConfig] = None):
        """
        Initialize the Elo rating system.
        
        Args:
            config: Configuration for the Elo rating system.
        """
        self.config = config or EloConfig()
        self.ratings: Dict[str, int] = {}  # Model name -> current rating
        self.rating_history: Dict[str, List[Tuple[datetime, int]]] = {}  # Model name -> [(timestamp, rating), ...]
        self.match_history: List[dict] = []  # List of match results
    
    def get_rating(self, model_name: str) -> int:
        """
        Get the current rating for a model.
        
        Args:
            model_name: Name of the model.
            
        Returns:
            Current rating of the model.
        """
        if model_name not in self.ratings:
            self.add_model(model_name)
        return self.ratings[model_name]
    
    def add_model(self, model_name: str, initial_rating: Optional[int] = None) -> None:
        """
        Add a new model to the rating system.
        
        Args:
            model_name: Name of the model to add.
            initial_rating: Optional initial rating for the model.
        """
        if model_name in self.ratings:
            return  # Model already exists
            
        rating = initial_rating if initial_rating is not None else self.config.initial_rating
        self.ratings[model_name] = rating
        
        # Initialize rating history with the current timestamp
        now = datetime.now()
        self.rating_history[model_name] = [(now, rating)]
    
    def expected_score(self, rating_a: int, rating_b: int) -> float:
        """
        Calculate the expected score for model A when playing against model B.
        
        Args:
            rating_a: Rating of model A.
            rating_b: Rating of model B.
            
        Returns:
            Expected score for model A (between 0 and 1).
        """
        return 1.0 / (1.0 + math.pow(10, (rating_b - rating_a) / self.config.scale_factor))
    
    def update_ratings(self, model_a: str, model_b: str, score_a: float) -> Tuple[int, int]:
        """
        Update ratings after a match between two models.
        
        Args:
            model_a: Name of model A.
            model_b: Name of model B.
            score_a: Actual score for model A (between 0 and 1).
            
        Returns:
            Tuple of (new_rating_a, new_rating_b).
        """
        # Ensure models exist in the system
        for model in [model_a, model_b]:
            if model not in self.ratings:
                self.add_model(model)
        
        # Get current ratings
        rating_a = self.ratings[model_a]
        rating_b = self.ratings[model_b]
        
        # Calculate expected scores
        expected_a = self.expected_score(rating_a, rating_b)
        
        # Calculate actual score for model B
        score_b = 1 - score_a
        
        # Update ratings
        new_rating_a = int(round(rating_a + self.config.k_factor * (score_a - expected_a)))
        new_rating_b = int(round(rating_b + self.config.k_factor * (score_b - (1 - expected_a))))
        
        # Store new ratings
        self.ratings[model_a] = new_rating_a
        self.ratings[model_b] = new_rating_b
        
        # Update rating history
        now = datetime.now()
        self.rating_history[model_a].append((now, new_rating_a))
        self.rating_history[model_b].append((now, new_rating_b))
        
        # Store match result
        match_result = {
            "timestamp": now.isoformat(),
            "model_a": model_a,
            "model_b": model_b,
            "rating_a_before": rating_a,
            "rating_b_before": rating_b,
            "rating_a_after": new_rating_a,
            "rating_b_after": new_rating_b,
            "score_a": score_a,
            "score_b": score_b
        }
        self.match_history.append(match_result)
        
        return new_rating_a, new_rating_b
    
    def get_model_rankings(self) -> List[Tuple[str, int]]:
        """
        Get all models sorted by rating.
        
        Returns:
            List of (model_name, rating) tuples, sorted by rating in descending order.
        """
        return sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)
    
    def get_rating_history(self, model_name: str) -> List[Tuple[datetime, int]]:
        """
        Get the rating history for a model.
        
        Args:
            model_name: Name of the model.
            
        Returns:
            List of (timestamp, rating) tuples.
        """
        return self.rating_history.get(model_name, [])
    
    def _prepare_serializable_data(self) -> dict:
        """
        Prepare data for serialization.
        
        Returns:
            Dictionary with serializable data.
        """
        # Convert datetime objects to strings for serialization
        serializable_history = {}
        for model, history in self.rating_history.items():
            serializable_history[model] = [(dt.isoformat(), rating) for dt, rating in history]
        
        return {
            "ratings": self.ratings,
            "rating_history": serializable_history,
            "match_history": self.match_history,
            "config": {
                "initial_rating": self.config.initial_rating,
                "k_factor": self.config.k_factor,
                "scale_factor": self.config.scale_factor
            }
        }
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save the current state of the rating system to a file.
        
        Args:
            filepath: Path to the file to save to.
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Get serializable data
        data = self._prepare_serializable_data()
        
        # Write to file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'EloRating':
        """
        Load a rating system from a file.
        
        Args:
            filepath: Path to the file to load from.
            
        Returns:
            EloRating instance loaded from the file.
        """
        if not os.path.exists(filepath):
            return cls()  # Return a new instance if file doesn't exist
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Create a new instance with the loaded config
        config = EloConfig(
            initial_rating=data["config"]["initial_rating"],
            k_factor=data["config"]["k_factor"],
            scale_factor=data["config"]["scale_factor"]
        )
        elo = cls(config)
        
        # Load ratings
        elo.ratings = data["ratings"]
        
        # Load match history
        elo.match_history = data["match_history"]
        
        # Convert string timestamps back to datetime objects
        elo.rating_history = {}
        for model, history in data["rating_history"].items():
            elo.rating_history[model] = [(datetime.fromisoformat(dt), rating) for dt, rating in history]
        
        return elo
    
    def generate_win_probability_matrix(self, models: Optional[List[str]] = None) -> Tuple[np.ndarray, List[str]]:
        """
        Generate a win probability matrix for the given models.
        
        Args:
            models: List of model names to include. If None, all models are included.
            
        Returns:
            Tuple of (probability_matrix, model_names).
            probability_matrix[i, j] is the probability of model_names[i] winning against model_names[j].
        """
        if models is None:
            models = list(self.ratings.keys())
        
        n = len(models)
        matrix = np.zeros((n, n))
        
        for i, model_a in enumerate(models):
            for j, model_b in enumerate(models):
                if i == j:
                    matrix[i, j] = 0.5  # Draw against itself
                else:
                    rating_a = self.ratings[model_a]
                    rating_b = self.ratings[model_b]
                    matrix[i, j] = self.expected_score(rating_a, rating_b)
        
        return matrix, models
    
    def plot_rating_history(self, output_path: Optional[str] = None, figsize: Tuple[int, int] = (12, 8)) -> None:
        """
        Plot the rating history for all models.
        
        Args:
            output_path: Optional path to save the plot to.
            figsize: Size of the figure (width, height) in inches.
        """
        self._create_plot(
            title='Model Rating History',
            xlabel='Turn Number',
            ylabel='Elo Rating',
            output_path=output_path,
            figsize=figsize,
            plot_func=self._plot_history
        )
    
    def _plot_history(self) -> None:
        """Plot rating history for all models."""
        # Skip if no history data
        if not self.rating_history:
            plt.text(0.5, 0.5, "No rating history data available", 
                    ha='center', va='center', transform=plt.gca().transAxes)
            return
            
        # Find the maximum number of turns (for x-axis range)
        max_turns = max(len(history) for history in self.rating_history.values())
        if max_turns == 0:
            plt.text(0.5, 0.5, "Empty rating history", 
                    ha='center', va='center', transform=plt.gca().transAxes)
            return
            
        # Set up the turn numbers for the x-axis
        turn_range = range(max_turns)
            
        # Plot each model's history
        for model, history in self.rating_history.items():
            if not history:
                continue
                
            # Extract ratings
            ratings = [entry[1] for entry in history]
            
            # Use sequential indices (turns) for x-axis
            turns = range(len(ratings))
            
            # Plot the ratings over turns
            plt.plot(turns, ratings, label=model, marker='o', markersize=6)
        
        # Set more readable x-axis with appropriate tick spacing
        if max_turns > 20:
            # For many turns, show fewer ticks
            tick_spacing = max(1, max_turns // 10)
            ticks = range(0, max_turns, tick_spacing)
        else:
            # For fewer turns, show all ticks
            ticks = range(max_turns)
            
        plt.xticks(ticks)
        
        # Set reasonable limits
        plt.xlim(-0.5, max_turns - 0.5)
        
        # Add a grid for better readability
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        plt.legend(loc='best')
        
        # Add labels
        plt.xlabel("Turn Number")
        plt.ylabel("Elo Rating")
    
    def plot_win_probability_matrix(self, 
                                    models: Optional[List[str]] = None, 
                                    output_path: Optional[str] = None, 
                                    figsize: Tuple[int, int] = (10, 8)) -> None:
        """
        Plot the win probability matrix as a heatmap.
        
        Args:
            models: List of model names to include. If None, all models are included.
            output_path: Optional path to save the plot to.
            figsize: Size of the figure (width, height) in inches.
        """
        matrix, model_names = self.generate_win_probability_matrix(models)
        
        self._create_plot(
            title='Win Probability Matrix',
            xlabel='Opponent Model',
            ylabel='Model',
            output_path=output_path,
            figsize=figsize,
            plot_func=lambda: self._plot_matrix(matrix, model_names)
        )
    
    def _plot_matrix(self, matrix: np.ndarray, model_names: List[str]) -> None:
        """Plot the win probability matrix."""
        plt.imshow(matrix, cmap="YlGnBu", vmin=0, vmax=1)
        
        # Add text annotations
        for i in range(len(model_names)):
            for j in range(len(model_names)):
                plt.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", 
                        color="black" if matrix[i, j] > 0.7 else "white")
        
        plt.colorbar(label="Win Probability")
        
        # Set tick labels to model names
        plt.xticks(range(len(model_names)), model_names, rotation=45, ha="right")
        plt.yticks(range(len(model_names)), model_names)
        
        plt.tight_layout()
    
    def _create_plot(self, 
                    title: str, 
                    xlabel: str, 
                    ylabel: str, 
                    output_path: Optional[str] = None,
                    figsize: Tuple[int, int] = (10, 8),
                    plot_func: callable = None) -> None:
        """
        Create a plot with common formatting.
        
        Args:
            title: Title of the plot.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            output_path: Path to save the plot to.
            figsize: Size of the figure.
            plot_func: Function to call to create the plot content.
        """
        plt.figure(figsize=figsize)
        
        if plot_func:
            plot_func()
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        if output_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path)
        else:
            plt.show() 