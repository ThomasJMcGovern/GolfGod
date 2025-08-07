"""
Odds data importer for manual CSV files and future API integration.
Handles historical odds data from various sources.
"""

import csv
import json
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from pathlib import Path


class OddsImporter:
    """Import and process betting odds data."""
    
    def __init__(self, data_dir: str = "data/raw"):
        """
        Initialize odds importer.
        
        Args:
            data_dir: Directory containing odds CSV files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def import_csv(self, filepath: str) -> pd.DataFrame:
        """
        Import odds from CSV file.
        
        Expected CSV format:
        tournament,date,player,outright_odds,top5_odds,top10_odds,bookmaker
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with odds data
        """
        try:
            df = pd.read_csv(filepath)
            
            # Validate required columns
            required_cols = ['tournament', 'date', 'player', 'outright_odds']
            missing_cols = set(required_cols) - set(df.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Convert American odds to decimal if needed
            df['outright_decimal'] = df['outright_odds'].apply(self._american_to_decimal)
            
            # Calculate implied probability
            df['implied_prob'] = df['outright_decimal'].apply(self._decimal_to_probability)
            
            return df
            
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return pd.DataFrame()
    
    def _american_to_decimal(self, odds: float) -> float:
        """
        Convert American odds to decimal odds.
        
        Args:
            odds: American odds (e.g., +150, -200)
            
        Returns:
            Decimal odds
        """
        if pd.isna(odds):
            return None
            
        if odds > 0:
            # Positive American odds
            return (odds / 100) + 1
        else:
            # Negative American odds
            return (100 / abs(odds)) + 1
    
    def _decimal_to_probability(self, decimal_odds: float) -> float:
        """
        Convert decimal odds to implied probability.
        
        Args:
            decimal_odds: Decimal odds (e.g., 2.5)
            
        Returns:
            Implied probability (0-1)
        """
        if pd.isna(decimal_odds) or decimal_odds <= 1:
            return None
        return 1 / decimal_odds
    
    def calculate_vig(self, odds_df: pd.DataFrame, tournament: str) -> float:
        """
        Calculate bookmaker vig/juice for a tournament.
        
        Args:
            odds_df: DataFrame with odds data
            tournament: Tournament name
            
        Returns:
            Vig percentage
        """
        tournament_odds = odds_df[odds_df['tournament'] == tournament]
        
        if tournament_odds.empty:
            return 0.0
        
        # Sum of implied probabilities - 1 = vig
        total_prob = tournament_odds['implied_prob'].sum()
        vig = (total_prob - 1) * 100  # Convert to percentage
        
        return round(vig, 2)
    
    def find_value_bets(
        self,
        odds_df: pd.DataFrame,
        our_probabilities: Dict[str, float],
        min_edge: float = 0.05
    ) -> List[Dict]:
        """
        Identify value betting opportunities.
        
        Args:
            odds_df: DataFrame with market odds
            our_probabilities: Our model's probabilities {player: prob}
            min_edge: Minimum edge required (default 5%)
            
        Returns:
            List of value bet dictionaries
        """
        value_bets = []
        
        for player, our_prob in our_probabilities.items():
            player_odds = odds_df[odds_df['player'] == player]
            
            if player_odds.empty:
                continue
            
            market_prob = player_odds['implied_prob'].iloc[0]
            
            # Calculate edge
            if market_prob and market_prob > 0:
                edge = (our_prob - market_prob) / market_prob
                
                if edge >= min_edge:
                    value_bets.append({
                        'player': player,
                        'our_prob': round(our_prob, 3),
                        'market_prob': round(market_prob, 3),
                        'edge': round(edge * 100, 1),  # As percentage
                        'decimal_odds': player_odds['outright_decimal'].iloc[0],
                        'expected_value': round((our_prob * player_odds['outright_decimal'].iloc[0]) - 1, 3)
                    })
        
        # Sort by edge
        value_bets.sort(key=lambda x: x['edge'], reverse=True)
        
        return value_bets
    
    def create_sample_csv(self, filepath: str = "data/raw/sample_odds.csv"):
        """
        Create a sample CSV file for testing.
        
        Args:
            filepath: Where to save the sample CSV
        """
        sample_data = [
            ['tournament', 'date', 'player', 'outright_odds', 'bookmaker'],
            ['Masters 2024', '2024-04-11', 'Scottie Scheffler', '+400', 'DraftKings'],
            ['Masters 2024', '2024-04-11', 'Jon Rahm', '+900', 'DraftKings'],
            ['Masters 2024', '2024-04-11', 'Rory McIlroy', '+1000', 'DraftKings'],
            ['Masters 2024', '2024-04-11', 'Viktor Hovland', '+1400', 'DraftKings'],
            ['Masters 2024', '2024-04-11', 'Patrick Cantlay', '+1600', 'DraftKings'],
            ['Masters 2024', '2024-04-11', 'Xander Schauffele', '+1800', 'DraftKings'],
            ['Masters 2024', '2024-04-11', 'Jordan Spieth', '+2000', 'DraftKings'],
            ['Masters 2024', '2024-04-11', 'Justin Thomas', '+2200', 'DraftKings'],
            ['Masters 2024', '2024-04-11', 'Brooks Koepka', '+2500', 'DraftKings'],
            ['Masters 2024', '2024-04-11', 'Collin Morikawa', '+2800', 'DraftKings'],
        ]
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(sample_data)
        
        print(f"Sample CSV created at: {filepath}")
        return filepath


def main():
    """Test odds importer functionality."""
    importer = OddsImporter()
    
    # Create and import sample data
    print("Creating sample odds CSV...")
    sample_file = importer.create_sample_csv()
    
    print("Importing odds data...")
    odds_df = importer.import_csv(str(sample_file))
    
    if not odds_df.empty:
        print(f"Imported {len(odds_df)} odds records")
        print(f"Players: {odds_df['player'].nunique()}")
        
        # Calculate vig
        vig = importer.calculate_vig(odds_df, 'Masters 2024')
        print(f"Bookmaker vig: {vig}%")
        
        # Test value bet finder
        sample_probs = {
            'Scottie Scheffler': 0.25,  # We think 25% chance
            'Jon Rahm': 0.12,  # We think 12% chance
            'Rory McIlroy': 0.08  # We think 8% chance
        }
        
        value_bets = importer.find_value_bets(odds_df, sample_probs)
        if value_bets:
            print(f"\nFound {len(value_bets)} value bets:")
            for bet in value_bets:
                print(f"  {bet['player']}: {bet['edge']}% edge (EV: {bet['expected_value']})")


if __name__ == "__main__":
    main()