"""
ROI calculator and statistical analysis for betting strategies.
Includes proper vig accounting and statistical significance testing.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional


class ROICalculator:
    """Calculate and analyze betting ROI with statistical validation."""
    
    def __init__(self, initial_bankroll: float = 1000):
        """
        Initialize ROI calculator.
        
        Args:
            initial_bankroll: Starting bankroll amount
        """
        self.initial_bankroll = initial_bankroll
        self.bets = []
    
    def add_bet(
        self,
        stake: float,
        odds: float,
        won: bool,
        american_odds: Optional[int] = None
    ):
        """
        Add a bet to the tracking.
        
        Args:
            stake: Amount wagered
            odds: Decimal odds
            won: Whether bet won
            american_odds: Original American odds (for vig calculation)
        """
        profit = (stake * odds - stake) if won else -stake
        
        self.bets.append({
            'stake': stake,
            'odds': odds,
            'american_odds': american_odds,
            'won': won,
            'profit': profit,
            'return': stake + profit
        })
    
    def calculate_roi(self) -> float:
        """
        Calculate overall ROI.
        
        Returns:
            ROI as percentage
        """
        if not self.bets:
            return 0.0
        
        total_staked = sum(bet['stake'] for bet in self.bets)
        total_profit = sum(bet['profit'] for bet in self.bets)
        
        if total_staked == 0:
            return 0.0
        
        return (total_profit / total_staked) * 100
    
    def calculate_vig_adjusted_roi(self) -> float:
        """
        Calculate ROI accounting for bookmaker vig.
        
        Returns:
            Vig-adjusted ROI as percentage
        """
        if not self.bets:
            return 0.0
        
        # Estimate average vig (typically 4-8% for golf outrights)
        avg_vig = self.estimate_vig()
        
        roi = self.calculate_roi()
        
        # Adjust for vig impact
        # This is simplified - actual impact depends on bet distribution
        adjusted_roi = roi - avg_vig
        
        return adjusted_roi
    
    def estimate_vig(self) -> float:
        """
        Estimate bookmaker vig from odds.
        
        Returns:
            Estimated vig as percentage
        """
        if not self.bets or not any(bet['american_odds'] for bet in self.bets):
            return 5.0  # Default estimate
        
        # Group bets by tournament (simplified - assumes sequential bets are same tournament)
        # In production, would group by actual tournament ID
        
        # For American odds, calculate implied probabilities
        implied_probs = []
        for bet in self.bets:
            if bet['american_odds']:
                if bet['american_odds'] > 0:
                    implied_prob = 100 / (bet['american_odds'] + 100)
                else:
                    implied_prob = abs(bet['american_odds']) / (abs(bet['american_odds']) + 100)
                implied_probs.append(implied_prob)
        
        # Vig is approximately the excess over 100% in total probability
        # This is simplified - actual calculation would need all odds from same market
        if implied_probs:
            avg_implied = np.mean(implied_probs)
            # Rough estimate: if average implied is 0.05 (5%), and there are ~20 players
            # Total would be 100%, so vig is proportional to number of outcomes
            estimated_total = avg_implied * 20  # Assuming 20 main contenders
            vig = (estimated_total - 1) * 100 if estimated_total > 1 else 5.0
            return min(vig, 10.0)  # Cap at reasonable maximum
        
        return 5.0  # Default
    
    def calculate_metrics(self) -> Dict:
        """
        Calculate comprehensive betting metrics.
        
        Returns:
            Dictionary with all metrics
        """
        if not self.bets:
            return {
                'roi': 0,
                'total_bets': 0,
                'win_rate': 0,
                'message': 'No bets placed'
            }
        
        df = pd.DataFrame(self.bets)
        
        metrics = {
            'total_bets': len(df),
            'winning_bets': df['won'].sum(),
            'win_rate': (df['won'].sum() / len(df)) * 100,
            'total_staked': df['stake'].sum(),
            'total_profit': df['profit'].sum(),
            'roi': self.calculate_roi(),
            'vig_adjusted_roi': self.calculate_vig_adjusted_roi(),
            'avg_odds': df['odds'].mean(),
            'avg_stake': df['stake'].mean(),
            'biggest_win': df[df['won']]['profit'].max() if any(df['won']) else 0,
            'biggest_loss': df[~df['won']]['profit'].min() if any(~df['won']) else 0,
        }
        
        # Calculate Sharpe ratio
        if len(df) > 1:
            returns = df['profit'] / df['stake']
            metrics['sharpe_ratio'] = self.calculate_sharpe(returns)
        else:
            metrics['sharpe_ratio'] = 0
        
        # Calculate maximum drawdown
        metrics['max_drawdown'] = self.calculate_max_drawdown(df['profit'].values)
        
        # Statistical significance
        metrics['p_value'] = self.calculate_significance(df['profit'].values)
        metrics['is_significant'] = metrics['p_value'] < 0.05
        
        # Confidence interval for ROI
        metrics['roi_confidence_interval'] = self.calculate_roi_confidence_interval(
            df['profit'].values,
            df['stake'].values
        )
        
        return metrics
    
    def calculate_sharpe(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate (default 2%)
            
        Returns:
            Sharpe ratio
        """
        if len(returns) < 2:
            return 0
        
        # Adjust risk-free rate to match betting frequency
        # Assuming weekly betting
        weekly_rf = risk_free_rate / 52
        
        excess_returns = returns - weekly_rf
        
        if excess_returns.std() == 0:
            return 0
        
        return np.sqrt(52) * (excess_returns.mean() / excess_returns.std())
    
    def calculate_max_drawdown(self, profits: np.ndarray) -> float:
        """
        Calculate maximum drawdown.
        
        Args:
            profits: Array of profit/loss for each bet
            
        Returns:
            Maximum drawdown as percentage
        """
        if len(profits) == 0:
            return 0
        
        cumulative = np.cumsum(profits)
        running_max = np.maximum.accumulate(cumulative + self.initial_bankroll)
        drawdown = (cumulative + self.initial_bankroll - running_max) / running_max
        
        return abs(np.min(drawdown)) * 100 if len(drawdown) > 0 else 0
    
    def calculate_significance(self, profits: np.ndarray) -> float:
        """
        Calculate statistical significance of profits.
        
        Uses t-test to determine if mean profit is significantly different from 0.
        
        Args:
            profits: Array of profits
            
        Returns:
            P-value
        """
        if len(profits) < 2:
            return 1.0
        
        # One-sample t-test against 0 (null hypothesis: no edge)
        t_stat, p_value = stats.ttest_1samp(profits, 0)
        
        # We want positive returns, so use one-tailed test
        if t_stat > 0:
            p_value = p_value / 2
        else:
            p_value = 1 - (p_value / 2)
        
        return p_value
    
    def calculate_roi_confidence_interval(
        self,
        profits: np.ndarray,
        stakes: np.ndarray,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for ROI.
        
        Args:
            profits: Array of profits
            stakes: Array of stakes
            confidence: Confidence level (default 95%)
            
        Returns:
            Tuple of (lower_bound, upper_bound) as percentages
        """
        if len(profits) < 2:
            roi = self.calculate_roi()
            return (roi, roi)
        
        # Bootstrap confidence interval
        n_bootstrap = 1000
        bootstrap_rois = []
        
        for _ in range(n_bootstrap):
            # Resample with replacement
            indices = np.random.choice(len(profits), len(profits), replace=True)
            boot_profits = profits[indices]
            boot_stakes = stakes[indices]
            
            if boot_stakes.sum() > 0:
                boot_roi = (boot_profits.sum() / boot_stakes.sum()) * 100
                bootstrap_rois.append(boot_roi)
        
        if bootstrap_rois:
            lower = np.percentile(bootstrap_rois, (1 - confidence) * 100 / 2)
            upper = np.percentile(bootstrap_rois, (1 + confidence) * 100 / 2)
            return (lower, upper)
        
        roi = self.calculate_roi()
        return (roi, roi)
    
    def minimum_bets_for_significance(
        self,
        target_roi: float = 3.0,
        win_rate: float = 0.10,
        avg_odds: float = 15.0,
        confidence: float = 0.95,
        power: float = 0.80
    ) -> int:
        """
        Calculate minimum number of bets needed for statistical significance.
        
        Args:
            target_roi: Target ROI percentage
            win_rate: Expected win rate
            avg_odds: Average decimal odds
            confidence: Confidence level
            power: Statistical power
            
        Returns:
            Minimum number of bets needed
        """
        # Effect size calculation
        expected_profit_per_bet = (win_rate * (avg_odds - 1)) - (1 - win_rate)
        variance = win_rate * (avg_odds - 1) ** 2 + (1 - win_rate)
        
        if variance == 0:
            return 100  # Default
        
        effect_size = expected_profit_per_bet / np.sqrt(variance)
        
        # Sample size calculation using power analysis
        alpha = 1 - confidence
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        n = ((z_alpha + z_beta) / effect_size) ** 2
        
        return max(int(np.ceil(n)), 30)  # Minimum 30 for statistical validity
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive ROI report.
        
        Returns:
            Formatted report string
        """
        metrics = self.calculate_metrics()
        
        if metrics.get('total_bets', 0) == 0:
            return "No bets to analyze."
        
        report = f"""
=== ROI Analysis Report ===

Performance Metrics:
- Total Bets: {metrics['total_bets']}
- Win Rate: {metrics['win_rate']:.1f}%
- ROI: {metrics['roi']:.2f}%
- Vig-Adjusted ROI: {metrics['vig_adjusted_roi']:.2f}%
- ROI 95% CI: ({metrics['roi_confidence_interval'][0]:.2f}%, {metrics['roi_confidence_interval'][1]:.2f}%)

Financial Summary:
- Total Staked: ${metrics['total_staked']:.2f}
- Total Profit: ${metrics['total_profit']:.2f}
- Average Stake: ${metrics['avg_stake']:.2f}
- Average Odds: {metrics['avg_odds']:.2f}

Risk Metrics:
- Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
- Max Drawdown: {metrics['max_drawdown']:.1f}%
- Biggest Win: ${metrics['biggest_win']:.2f}
- Biggest Loss: ${metrics['biggest_loss']:.2f}

Statistical Validation:
- P-value: {metrics['p_value']:.4f}
- Statistically Significant: {'Yes ✓' if metrics['is_significant'] else 'No ✗'}
- Minimum Bets Needed: {self.minimum_bets_for_significance()}

Conclusion:
"""
        
        if metrics['is_significant'] and metrics['vig_adjusted_roi'] > 3:
            report += "✓ Strategy shows statistically significant positive edge"
        elif metrics['vig_adjusted_roi'] > 3 and not metrics['is_significant']:
            report += "⚠ Positive ROI but needs more data for significance"
        else:
            report += "✗ No significant edge detected - review strategy"
        
        return report


def main():
    """Test ROI calculator."""
    calc = ROICalculator(initial_bankroll=1000)
    
    # Simulate some bets
    test_bets = [
        (50, 15.0, False, 1400),  # $50 at +1400, lost
        (30, 8.0, False, 700),     # $30 at +700, lost
        (40, 12.0, True, 1100),    # $40 at +1100, won!
        (50, 10.0, False, 900),    # $50 at +900, lost
        (25, 20.0, False, 1900),   # $25 at +1900, lost
        (35, 6.0, True, 500),      # $35 at +500, won!
    ]
    
    for stake, odds, won, american in test_bets:
        calc.add_bet(stake, odds, won, american)
    
    # Generate report
    print(calc.generate_report())
    
    # Check minimum bets needed
    min_bets = calc.minimum_bets_for_significance(
        target_roi=5.0,
        win_rate=0.12,
        avg_odds=12.0
    )
    print(f"\nMinimum bets for significance: {min_bets}")


if __name__ == "__main__":
    main()