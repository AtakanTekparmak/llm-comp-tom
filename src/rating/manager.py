"""
Rating manager for integrating the Elo rating system with the game.

This module provides a RatingManager class that integrates the Elo rating
system with the game, tracking model performances and updating ratings
based on game outcomes.
"""

import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import logging

from src.rating.core import EloRating, EloConfig

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class GameResult:
    """Data class to store the result of a game."""
    models: List[str]  # List of model names that participated
    scores: Dict[str, float]  # Dictionary mapping model name to final score
    timestamp: datetime = None  # When the game was played
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class RatingManager:
    """
    Manager for tracking and updating Elo ratings based on game results.
    
    This class provides methods for converting game results to Elo updates,
    managing the rating system, and generating reports.
    """
    
    def __init__(self, 
                 data_dir: str = "data/ratings", 
                 elo_config: Optional[EloConfig] = None,
                 ratings_file: str = "ratings.json"):
        """
        Initialize the rating manager.
        
        Args:
            data_dir: Directory to store rating data.
            elo_config: Configuration for the Elo rating system.
            ratings_file: Filename for the ratings data.
        """
        self.data_dir = data_dir
        self.ratings_file = os.path.join(data_dir, ratings_file)
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load or initialize the rating system
        self._initialize_elo_system(elo_config)
    
    def _initialize_elo_system(self, elo_config: Optional[EloConfig] = None) -> None:
        """
        Initialize the Elo rating system, either by loading from file or creating a new one.
        
        Args:
            elo_config: Optional configuration for the Elo rating system.
        """
        if os.path.exists(self.ratings_file):
            self.elo = EloRating.load_from_file(self.ratings_file)
            logger.info(f"Loaded existing ratings from {self.ratings_file}")
        else:
            self.elo = EloRating(elo_config)
            logger.info("Initialized new rating system")
    
    def process_game_result(self, result: GameResult) -> None:
        """
        Process the result of a game and update ratings accordingly.
        
        For each pair of models in the game, this calculates the outcome
        and updates the Elo ratings based on the relative performance.
        
        Args:
            result: Result of the game.
        """
        logger.info(f"Processing game result with {len(result.models)} models")
        
        # Ensure all models exist in the rating system
        self._ensure_models_exist(result.models)
        
        # Create all possible model pairs
        self._process_model_pairs(result)
        
        # Save updated ratings
        self.save()
    
    def _ensure_models_exist(self, models: List[str]) -> None:
        """
        Ensure all models exist in the rating system.
        
        Args:
            models: List of model names.
        """
        for model in models:
            if model not in self.elo.ratings:
                self.elo.add_model(model)
                logger.info(f"Added new model: {model}")
    
    def _process_model_pairs(self, result: GameResult) -> None:
        """
        Process all possible pairs of models and update their ratings.
        
        Args:
            result: Game result containing models and scores.
        """
        # Get all possible pairs of models (combinations)
        model_pairs = [(i, j) for i in range(len(result.models)) 
                       for j in range(i+1, len(result.models))]
        
        for i, j in model_pairs:
            model_a = result.models[i]
            model_b = result.models[j]
            
            score_a = result.scores[model_a]
            score_b = result.scores[model_b]
            
            # Convert raw scores to a relative outcome (0-1)
            outcome_a = self._calculate_relative_outcome(score_a, score_b)
            
            # Update ratings
            self.elo.update_ratings(model_a, model_b, outcome_a)
            logger.info(f"Updated ratings for {model_a} vs {model_b}: outcome {outcome_a:.2f}")
    
    def _calculate_relative_outcome(self, score_a: float, score_b: float) -> float:
        """
        Calculate the relative outcome between two scores.
        
        Args:
            score_a: Score of model A.
            score_b: Score of model B.
            
        Returns:
            Relative outcome for model A (between 0 and 1).
        """
        if score_a == score_b:
            return 0.5  # Draw
            
        # Normalize the outcome to be between 0 and 1
        total = score_a + score_b
        if total > 0:
            return score_a / total
        else:
            return 0.5  # If both scores are 0, it's a draw
    
    def get_ratings(self) -> Dict[str, int]:
        """
        Get the current ratings for all models.
        
        Returns:
            Dictionary mapping model names to ratings.
        """
        return self.elo.ratings
    
    def get_model_rankings(self) -> List[Tuple[str, int]]:
        """
        Get all models sorted by rating.
        
        Returns:
            List of (model_name, rating) tuples, sorted by rating in descending order.
        """
        return self.elo.get_model_rankings()
    
    def save(self) -> None:
        """Save the current state of the rating system to a file."""
        self.elo.save_to_file(self.ratings_file)
        logger.info(f"Saved ratings to {self.ratings_file}")
    
    def load(self) -> None:
        """Load the rating system from a file."""
        self.elo = EloRating.load_from_file(self.ratings_file)
        logger.info(f"Loaded ratings from {self.ratings_file}")
    
    def generate_rating_report(self, output_dir: Optional[str] = None) -> pd.DataFrame:
        """
        Generate a report of the current ratings.
        
        Args:
            output_dir: Directory to save the report to.
            
        Returns:
            DataFrame with model names and ratings.
        """
        if output_dir is None:
            output_dir = self.data_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get rankings and convert to DataFrame
        rankings = self.get_model_rankings()
        df = pd.DataFrame(rankings, columns=["Model", "Rating"])
        
        # Add rank column
        df.insert(0, "Rank", range(1, len(rankings) + 1))
        
        # Save to CSV
        csv_path = os.path.join(output_dir, "ratings_report.csv")
        df.to_csv(csv_path, index=False)
        logger.info(f"Generated ratings report at {csv_path}")
        
        # Generate plots
        self.plot_ratings(output_dir)
        
        return df
    
    def plot_ratings(self, output_dir: Optional[str] = None) -> None:
        """
        Plot current ratings and rating history.
        
        Args:
            output_dir: Directory to save the plots to.
        """
        if output_dir is None:
            output_dir = self.data_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate bar plot of current ratings
        self._plot_current_ratings(output_dir)
        
        # Generate rating history plot with turn numbers
        history_plot_path = os.path.join(output_dir, "rating_history.png")
        self.elo.plot_rating_history(output_path=history_plot_path)
        logger.info(f"Saved rating history plot to {history_plot_path}")
        
        # Generate win probability matrix
        matrix_plot_path = os.path.join(output_dir, "win_probability_matrix.png")
        self.elo.plot_win_probability_matrix(output_path=matrix_plot_path)
        logger.info(f"Saved win probability matrix to {matrix_plot_path}")
    
    def _plot_current_ratings(self, output_dir: str) -> None:
        """
        Plot the current ratings as a horizontal bar chart.
        
        Args:
            output_dir: Directory to save the plot to.
        """
        # Get rankings
        rankings = self.get_model_rankings()
        models = [r[0] for r in rankings]
        ratings = [r[1] for r in rankings]
        
        plt.figure(figsize=(10, 6))
        bars = plt.barh(models, ratings, color='skyblue')
        
        # Add rating values at the end of each bar
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 10, bar.get_y() + bar.get_height()/2, 
                     f'{width:.0f}', ha='left', va='center')
        
        plt.title('Current Model Ratings')
        plt.xlabel('Elo Rating')
        plt.tight_layout()
        
        bar_plot_path = os.path.join(output_dir, "current_ratings.png")
        plt.savefig(bar_plot_path)
        plt.close()  # Close the figure to free memory
        logger.info(f"Saved current ratings plot to {bar_plot_path}")
    
    def export_to_csv(self, filepath: str) -> None:
        """
        Export the match history to a CSV file.
        
        Args:
            filepath: Path to save the CSV file to.
        """
        if not self.elo.match_history:
            logger.warning("No match history to export")
            return
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Convert match history to DataFrame
        df = pd.DataFrame(self.elo.match_history)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        logger.info(f"Exported match history to {filepath}")
    
    def import_from_csv(self, filepath: str) -> None:
        """
        Import match history from a CSV file.
        
        This is useful for rebuilding the rating system from scratch
        or migrating data between different rating systems.
        
        Args:
            filepath: Path to the CSV file to import.
        """
        if not os.path.exists(filepath):
            logger.error(f"CSV file not found: {filepath}")
            return
        
        # Read CSV file
        df = pd.read_csv(filepath)
        
        # Reset the rating system
        self.elo = EloRating(self.elo.config)
        
        # Process each match
        for _, row in df.iterrows():
            model_a = row["model_a"]
            model_b = row["model_b"]
            score_a = row["score_a"]
            
            # Add models if needed
            for model in [model_a, model_b]:
                if model not in self.elo.ratings:
                    self.elo.add_model(model)
            
            # Update ratings
            self.elo.update_ratings(model_a, model_b, score_a)
        
        # Save the rebuilt rating system
        self.save()
        logger.info(f"Imported {len(df)} matches from {filepath}") 