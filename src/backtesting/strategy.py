"""
Betting strategy definitions and base classes.
Your co-founder should review and validate these strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


class BettingStrategy(ABC):
    """Base class for all betting strategies."""
    
    def __init__(
        self,
        bankroll: float = 1000,
        kelly_fraction: float = 0.25,
        min_edge: float = 0.05,
        max_bet_pct: float = 0.05
    ):
        """
        Initialize betting strategy.
        
        Args:
            bankroll: Starting bankroll
            kelly_fraction: Fraction of Kelly criterion to use (conservative)
            min_edge: Minimum edge required to place bet
            max_bet_pct: Maximum bet as percentage of bankroll
        """
        self.initial_bankroll = bankroll
        self.bankroll = bankroll
        self.kelly_fraction = kelly_fraction
        self.min_edge = min_edge
        self.max_bet_pct = max_bet_pct
        self.bet_history = []
    
    @abstractmethod
    def calculate_probabilities(self, tournament_data: Dict) -> Dict[str, float]:
        """
        Calculate win probabilities for players.
        
        Args:
            tournament_data: Tournament information including players, conditions
            
        Returns:
            Dictionary mapping player names to win probabilities
        """
        pass
    
    def calculate_edge(self, our_prob: float, market_prob: float) -> float:
        """
        Calculate betting edge.
        
        Args:
            our_prob: Our calculated probability
            market_prob: Market implied probability
            
        Returns:
            Edge as a decimal (0.05 = 5% edge)
        """
        if market_prob <= 0:
            return 0
        return (our_prob - market_prob) / market_prob
    
    def kelly_bet_size(self, edge: float, odds: float) -> float:
        """
        Calculate bet size using Kelly criterion.
        
        Args:
            edge: Our edge (as decimal)
            odds: Decimal odds
            
        Returns:
            Fraction of bankroll to bet
        """
        if edge <= 0 or odds <= 1:
            return 0
        
        # Kelly formula: f = (p*b - q) / b
        # where p = win probability, q = lose probability, b = odds-1
        b = odds - 1
        p = (edge + 1) / (b + 1)  # Convert edge to win probability
        q = 1 - p
        
        kelly = (p * b - q) / b
        
        # Apply Kelly fraction for conservative betting
        kelly *= self.kelly_fraction
        
        # Cap at maximum bet percentage
        return min(kelly, self.max_bet_pct)
    
    def place_bet(
        self,
        player: str,
        amount: float,
        odds: float,
        tournament: str,
        actual_winner: str = None
    ) -> Dict:
        """
        Place a bet and track it.
        
        Args:
            player: Player to bet on
            amount: Bet amount
            odds: Decimal odds
            tournament: Tournament name
            actual_winner: Actual tournament winner (for backtesting)
            
        Returns:
            Bet result dictionary
        """
        bet = {
            'tournament': tournament,
            'player': player,
            'amount': amount,
            'odds': odds,
            'potential_return': amount * odds,
            'actual_winner': actual_winner,
            'won': False,
            'profit': -amount  # Default to loss
        }
        
        # Check if bet won
        if actual_winner and player == actual_winner:
            bet['won'] = True
            bet['profit'] = (amount * odds) - amount
            self.bankroll += bet['profit']
        else:
            self.bankroll -= amount
        
        self.bet_history.append(bet)
        return bet
    
    def get_performance_metrics(self) -> Dict:
        """
        Calculate strategy performance metrics.
        
        Returns:
            Dictionary with performance statistics
        """
        if not self.bet_history:
            return {}
        
        df = pd.DataFrame(self.bet_history)
        
        total_bets = len(df)
        winning_bets = df['won'].sum()
        total_staked = df['amount'].sum()
        total_profit = df['profit'].sum()
        
        metrics = {
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'win_rate': winning_bets / total_bets if total_bets > 0 else 0,
            'total_staked': total_staked,
            'total_profit': total_profit,
            'roi': (total_profit / total_staked * 100) if total_staked > 0 else 0,
            'final_bankroll': self.bankroll,
            'bankroll_growth': ((self.bankroll - self.initial_bankroll) / self.initial_bankroll * 100)
        }
        
        # Calculate Sharpe ratio (simplified)
        if len(df) > 1:
            returns = df['profit'] / df['amount']
            metrics['sharpe_ratio'] = returns.mean() / returns.std() if returns.std() > 0 else 0
        
        # Calculate max drawdown
        cumulative = df['profit'].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / self.initial_bankroll
        metrics['max_drawdown'] = abs(drawdown.min()) * 100 if len(drawdown) > 0 else 0
        
        return metrics


class WeatherEdgeStrategy(BettingStrategy):
    """
    Strategy based on weather conditions impact.
    Hypothesis: Market undervalues wind impact on certain players.
    """
    
    def __init__(self, **kwargs):
        """Initialize weather strategy."""
        super().__init__(**kwargs)
        self.wind_threshold = 15  # mph
        
    def calculate_probabilities(self, tournament_data: Dict) -> Dict[str, float]:
        """
        Calculate probabilities based on weather conditions.
        
        Wind specialists get probability boost in windy conditions.
        """
        players = tournament_data.get('players', [])
        weather = tournament_data.get('weather', {})
        wind_speed = weather.get('avg_wind_mph', 0)
        
        probabilities = {}
        
        # Simple model: adjust base probabilities by wind performance
        for player in players:
            base_prob = player.get('base_probability', 0.02)  # Default 2%
            
            # Wind adjustment
            if wind_speed > self.wind_threshold:
                # Players with good wind stats get a boost
                wind_performance = player.get('wind_performance', 0)
                adjustment = wind_performance * 0.1  # Up to 10% boost
                probabilities[player['name']] = base_prob * (1 + adjustment)
            else:
                probabilities[player['name']] = base_prob
        
        # Normalize probabilities to sum to 1
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: v/total for k, v in probabilities.items()}
        
        return probabilities


class FormMomentumStrategy(BettingStrategy):
    """
    Strategy based on recent form and momentum.
    Hypothesis: Recent performance predicts near-term results.
    """
    
    def __init__(self, **kwargs):
        """Initialize form strategy."""
        super().__init__(**kwargs)
        self.lookback_tournaments = 5
        self.recency_weights = [0.35, 0.25, 0.20, 0.15, 0.05]  # Most recent weighted highest
    
    def calculate_probabilities(self, tournament_data: Dict) -> Dict[str, float]:
        """
        Calculate probabilities based on recent form.
        """
        players = tournament_data.get('players', [])
        probabilities = {}
        
        for player in players:
            recent_finishes = player.get('recent_finishes', [])[:self.lookback_tournaments]
            
            if not recent_finishes:
                probabilities[player['name']] = 0.01  # Minimal probability
                continue
            
            # Calculate weighted average finish position
            weighted_sum = 0
            weight_total = 0
            
            for i, finish in enumerate(recent_finishes):
                if i < len(self.recency_weights):
                    weight = self.recency_weights[i]
                    # Convert finish position to score (lower is better)
                    score = 1 / (finish + 1)  # Avoid division by zero
                    weighted_sum += score * weight
                    weight_total += weight
            
            # Convert to probability
            form_score = weighted_sum / weight_total if weight_total > 0 else 0
            probabilities[player['name']] = form_score
        
        # Normalize
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: v/total for k, v in probabilities.items()}
        
        return probabilities


class CourseFitStrategy(BettingStrategy):
    """
    Strategy based on course history and fit.
    Hypothesis: Course specialists outperform at similar venues.
    """
    
    def __init__(self, **kwargs):
        """Initialize course fit strategy."""
        super().__init__(**kwargs)
    
    def calculate_probabilities(self, tournament_data: Dict) -> Dict[str, float]:
        """
        Calculate probabilities based on course history.
        """
        players = tournament_data.get('players', [])
        course_type = tournament_data.get('course_type', 'standard')
        
        probabilities = {}
        
        for player in players:
            # Get player's performance at this course
            course_history = player.get('course_history', [])
            similar_course_performance = player.get(f'{course_type}_performance', 0.5)
            
            if course_history:
                # Average finish at this course
                avg_finish = sum(course_history) / len(course_history)
                course_score = 1 / (avg_finish + 1)
            else:
                course_score = 0.02  # Default
            
            # Combine with similar course performance
            combined_score = (course_score * 0.7) + (similar_course_performance * 0.3)
            probabilities[player['name']] = combined_score
        
        # Normalize
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: v/total for k, v in probabilities.items()}
        
        return probabilities


class CombinedStrategy(BettingStrategy):
    """
    Combine multiple strategies with weighted approach.
    """
    
    def __init__(self, strategies: List[BettingStrategy], weights: List[float] = None, **kwargs):
        """
        Initialize combined strategy.
        
        Args:
            strategies: List of strategies to combine
            weights: Weights for each strategy (must sum to 1)
        """
        super().__init__(**kwargs)
        self.strategies = strategies
        
        if weights is None:
            # Equal weights by default
            weights = [1/len(strategies)] * len(strategies)
        self.weights = weights
    
    def calculate_probabilities(self, tournament_data: Dict) -> Dict[str, float]:
        """
        Calculate combined probabilities from all strategies.
        """
        all_probs = []
        
        # Get probabilities from each strategy
        for strategy in self.strategies:
            probs = strategy.calculate_probabilities(tournament_data)
            all_probs.append(probs)
        
        # Combine with weights
        combined = {}
        all_players = set()
        for probs in all_probs:
            all_players.update(probs.keys())
        
        for player in all_players:
            weighted_prob = 0
            for i, probs in enumerate(all_probs):
                weighted_prob += probs.get(player, 0) * self.weights[i]
            combined[player] = weighted_prob
        
        # Normalize
        total = sum(combined.values())
        if total > 0:
            combined = {k: v/total for k, v in combined.items()}
        
        return combined


def main():
    """Test strategies."""
    # Create sample tournament data
    tournament_data = {
        'players': [
            {'name': 'Player A', 'base_probability': 0.1, 'wind_performance': 0.8},
            {'name': 'Player B', 'base_probability': 0.08, 'wind_performance': 0.3},
            {'name': 'Player C', 'base_probability': 0.06, 'recent_finishes': [2, 5, 1, 10, 15]},
        ],
        'weather': {'avg_wind_mph': 18}
    }
    
    # Test weather strategy
    weather_strategy = WeatherEdgeStrategy()
    probs = weather_strategy.calculate_probabilities(tournament_data)
    print("Weather Strategy Probabilities:", probs)
    
    # Test form strategy
    form_strategy = FormMomentumStrategy()
    probs = form_strategy.calculate_probabilities(tournament_data)
    print("Form Strategy Probabilities:", probs)


if __name__ == "__main__":
    main()