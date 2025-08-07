"""
Database management utilities for GolfPredict.
Handles data insertion, queries, and maintenance.
"""

from typing import List, Dict, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import pandas as pd

from .models import (
    DatabaseManager, Player, Tournament, Course, 
    Round, Weather, Odds, BacktestResult
)


class GolfDatabase:
    """High-level database operations for GolfPredict."""
    
    def __init__(self, db_url: str = None):
        """
        Initialize database interface.
        
        Args:
            db_url: Database URL. Defaults to SQLite.
        """
        self.db_manager = DatabaseManager(db_url)
        self.db_manager.create_tables()
    
    def add_player(self, session: Session, name: str, pga_id: str = None, country: str = None) -> Player:
        """
        Add or get a player.
        
        Args:
            session: Database session
            name: Player name
            pga_id: PGA Tour ID
            country: Player's country
            
        Returns:
            Player object
        """
        # Check if player exists
        player = session.query(Player).filter_by(name=name).first()
        
        if not player:
            player = Player(name=name, pga_tour_id=pga_id, country=country)
            session.add(player)
            session.commit()
        
        return player
    
    def add_tournament(
        self,
        session: Session,
        name: str,
        start_date: date,
        course_name: str = None,
        purse: float = None
    ) -> Tournament:
        """
        Add or get a tournament.
        
        Args:
            session: Database session
            name: Tournament name
            start_date: Tournament start date
            course_name: Course name
            purse: Prize money
            
        Returns:
            Tournament object
        """
        # Check if tournament exists
        tournament = session.query(Tournament).filter_by(
            name=name,
            start_date=start_date
        ).first()
        
        if not tournament:
            # Get or create course if provided
            course = None
            if course_name:
                course = session.query(Course).filter_by(name=course_name).first()
                if not course:
                    course = Course(name=course_name)
                    session.add(course)
            
            tournament = Tournament(
                name=name,
                start_date=start_date,
                course=course,
                purse=purse
            )
            session.add(tournament)
            session.commit()
        
        return tournament
    
    def add_round_score(
        self,
        session: Session,
        tournament_id: int,
        player_id: int,
        round_num: int,
        score: int
    ) -> Round:
        """
        Add a round score.
        
        Args:
            session: Database session
            tournament_id: Tournament ID
            player_id: Player ID
            round_num: Round number (1-4)
            score: Round score
            
        Returns:
            Round object
        """
        round_score = Round(
            tournament_id=tournament_id,
            player_id=player_id,
            round_num=round_num,
            score=score
        )
        session.add(round_score)
        session.commit()
        
        return round_score
    
    def add_weather_observation(
        self,
        session: Session,
        tournament_id: int,
        date: date,
        weather_data: Dict
    ) -> Weather:
        """
        Add weather observation.
        
        Args:
            session: Database session
            tournament_id: Tournament ID
            date: Observation date
            weather_data: Dictionary with weather metrics
            
        Returns:
            Weather object
        """
        weather = Weather(
            tournament_id=tournament_id,
            observation_date=date,
            temp_high_f=weather_data.get('temp_high_f'),
            temp_low_f=weather_data.get('temp_low_f'),
            wind_speed_mph=weather_data.get('wind_speed_mph'),
            wind_direction=weather_data.get('wind_direction'),
            precipitation_mm=weather_data.get('precipitation_mm'),
            conditions=weather_data.get('conditions')
        )
        session.add(weather)
        session.commit()
        
        return weather
    
    def add_odds(
        self,
        session: Session,
        tournament_id: int,
        player_id: int,
        american_odds: int,
        bookmaker: str = 'DraftKings',
        market_type: str = 'outright'
    ) -> Odds:
        """
        Add betting odds.
        
        Args:
            session: Database session
            tournament_id: Tournament ID
            player_id: Player ID
            american_odds: American format odds
            bookmaker: Bookmaker name
            market_type: Type of bet
            
        Returns:
            Odds object
        """
        # Calculate decimal odds and implied probability
        if american_odds > 0:
            decimal_odds = (american_odds / 100) + 1
        else:
            decimal_odds = (100 / abs(american_odds)) + 1
        
        implied_prob = 1 / decimal_odds
        
        odds = Odds(
            tournament_id=tournament_id,
            player_id=player_id,
            bookmaker=bookmaker,
            market_type=market_type,
            american_odds=american_odds,
            decimal_odds=decimal_odds,
            implied_probability=implied_prob,
            recorded_at=datetime.utcnow()
        )
        session.add(odds)
        session.commit()
        
        return odds
    
    def get_tournament_leaderboard(self, session: Session, tournament_id: int) -> pd.DataFrame:
        """
        Get tournament leaderboard.
        
        Args:
            session: Database session
            tournament_id: Tournament ID
            
        Returns:
            DataFrame with leaderboard
        """
        # Query rounds with player names
        query = session.query(
            Player.name,
            func.sum(Round.score).label('total_score'),
            func.count(Round.id).label('rounds_played')
        ).join(
            Round
        ).filter(
            Round.tournament_id == tournament_id
        ).group_by(
            Player.id
        ).order_by(
            func.sum(Round.score)
        )
        
        df = pd.DataFrame(query.all())
        if not df.empty:
            df['position'] = df['total_score'].rank(method='min').astype(int)
        
        return df
    
    def get_player_history(
        self,
        session: Session,
        player_id: int,
        limit: int = 20
    ) -> pd.DataFrame:
        """
        Get player's recent tournament history.
        
        Args:
            session: Database session
            player_id: Player ID
            limit: Number of tournaments to return
            
        Returns:
            DataFrame with player history
        """
        query = session.query(
            Tournament.name,
            Tournament.start_date,
            func.sum(Round.score).label('total_score')
        ).join(
            Round
        ).filter(
            Round.player_id == player_id
        ).group_by(
            Tournament.id
        ).order_by(
            Tournament.start_date.desc()
        ).limit(limit)
        
        return pd.DataFrame(query.all())
    
    def get_weather_impact_stats(self, session: Session) -> Dict:
        """
        Analyze weather impact on scoring.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary with weather impact analysis
        """
        # Get tournaments with weather data
        query = session.query(
            Weather.wind_speed_mph,
            func.avg(Round.score).label('avg_score')
        ).join(
            Tournament, Weather.tournament_id == Tournament.id
        ).join(
            Round, Tournament.id == Round.tournament_id
        ).group_by(
            Weather.id
        )
        
        df = pd.DataFrame(query.all())
        
        if df.empty:
            return {}
        
        # Categorize wind conditions
        df['wind_category'] = pd.cut(
            df['wind_speed_mph'],
            bins=[0, 10, 15, 20, 100],
            labels=['calm', 'light', 'moderate', 'strong']
        )
        
        # Calculate average scores by wind category
        wind_impact = df.groupby('wind_category')['avg_score'].mean().to_dict()
        
        return {
            'wind_impact': wind_impact,
            'correlation': df[['wind_speed_mph', 'avg_score']].corr().iloc[0, 1]
        }
    
    def save_backtest_result(
        self,
        session: Session,
        strategy_name: str,
        results: Dict
    ) -> BacktestResult:
        """
        Save backtest results.
        
        Args:
            session: Database session
            strategy_name: Name of strategy
            results: Dictionary with backtest metrics
            
        Returns:
            BacktestResult object
        """
        backtest = BacktestResult(
            strategy_name=strategy_name,
            start_date=results.get('start_date'),
            end_date=results.get('end_date'),
            initial_bankroll=results.get('initial_bankroll', 1000),
            final_bankroll=results.get('final_bankroll'),
            total_bets=results.get('total_bets'),
            winning_bets=results.get('winning_bets'),
            roi=results.get('roi'),
            sharpe_ratio=results.get('sharpe_ratio'),
            max_drawdown=results.get('max_drawdown'),
            parameters=str(results.get('parameters', {}))
        )
        session.add(backtest)
        session.commit()
        
        return backtest


def main():
    """Test database operations."""
    db = GolfDatabase()
    session = db.db_manager.get_session()
    
    try:
        # Add test data
        player = db.add_player(session, "Tiger Woods", "08793", "USA")
        print(f"Added player: {player}")
        
        tournament = db.add_tournament(
            session,
            "Masters Tournament",
            date(2024, 4, 11),
            "Augusta National",
            20000000
        )
        print(f"Added tournament: {tournament}")
        
        # Add a round score
        round_score = db.add_round_score(session, tournament.id, player.id, 1, 72)
        print(f"Added round: {round_score}")
        
    finally:
        session.close()


if __name__ == "__main__":
    main()