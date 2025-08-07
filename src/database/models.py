"""
SQLAlchemy models for GolfPredict database.
Compatible with both SQLite (Phase 0) and PostgreSQL (Phase 1+).
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()


class Player(Base):
    """PGA Tour player information."""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    pga_tour_id = Column(String(50), unique=True)
    country = Column(String(100))
    turned_pro = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rounds = relationship('Round', back_populates='player')
    odds = relationship('Odds', back_populates='player')
    
    def __repr__(self):
        return f"<Player(name='{self.name}', id={self.id})>"


class Tournament(Base):
    """Golf tournament information."""
    __tablename__ = 'tournaments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    purse = Column(Float)
    season = Column(Integer)
    pga_tour_id = Column(String(50), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship('Course', back_populates='tournaments')
    rounds = relationship('Round', back_populates='tournament')
    weather = relationship('Weather', back_populates='tournament')
    odds = relationship('Odds', back_populates='tournament')
    
    def __repr__(self):
        return f"<Tournament(name='{self.name}', date={self.start_date})>"


class Course(Base):
    """Golf course information."""
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    par = Column(Integer)
    yardage = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tournaments = relationship('Tournament', back_populates='course')
    
    def __repr__(self):
        return f"<Course(name='{self.name}', par={self.par})>"


class Round(Base):
    """Individual round scores."""
    __tablename__ = 'rounds'
    
    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    round_num = Column(Integer, nullable=False)
    score = Column(Integer)
    strokes_gained_total = Column(Float)
    strokes_gained_tee = Column(Float)
    strokes_gained_approach = Column(Float)
    strokes_gained_putting = Column(Float)
    fairways_hit = Column(Integer)
    greens_in_regulation = Column(Integer)
    putts = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tournament = relationship('Tournament', back_populates='rounds')
    player = relationship('Player', back_populates='rounds')
    
    def __repr__(self):
        return f"<Round(player_id={self.player_id}, tournament_id={self.tournament_id}, round={self.round_num})>"


class Weather(Base):
    """Weather observations for tournaments."""
    __tablename__ = 'weather'
    
    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    observation_date = Column(Date, nullable=False)
    temp_high_f = Column(Float)
    temp_low_f = Column(Float)
    wind_speed_mph = Column(Float)
    wind_direction = Column(Integer)
    precipitation_mm = Column(Float)
    conditions = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tournament = relationship('Tournament', back_populates='weather')
    
    def __repr__(self):
        return f"<Weather(tournament_id={self.tournament_id}, date={self.observation_date})>"


class Odds(Base):
    """Betting odds data."""
    __tablename__ = 'odds'
    
    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    bookmaker = Column(String(100))
    market_type = Column(String(50))  # outright, top5, top10, etc.
    american_odds = Column(Integer)
    decimal_odds = Column(Float)
    implied_probability = Column(Float)
    recorded_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tournament = relationship('Tournament', back_populates='odds')
    player = relationship('Player', back_populates='odds')
    
    def __repr__(self):
        return f"<Odds(player_id={self.player_id}, tournament_id={self.tournament_id}, odds={self.american_odds})>"


class BacktestResult(Base):
    """Store backtest results for analysis."""
    __tablename__ = 'backtest_results'
    
    id = Column(Integer, primary_key=True)
    strategy_name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_bankroll = Column(Float)
    final_bankroll = Column(Float)
    total_bets = Column(Integer)
    winning_bets = Column(Integer)
    roi = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    parameters = Column(Text)  # JSON string of strategy parameters
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<BacktestResult(strategy='{self.strategy_name}', roi={self.roi})>"


# Database connection and session management
class DatabaseManager:
    """Manage database connections and sessions."""
    
    def __init__(self, db_url: str = None):
        """
        Initialize database manager.
        
        Args:
            db_url: Database URL. Defaults to SQLite for Phase 0.
        """
        if db_url is None:
            # Default to SQLite for Phase 0
            db_url = 'sqlite:///data/golfpredict.db'
        
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)
        print("Database tables created successfully.")
    
    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()
    
    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(self.engine)
        print("Database tables dropped.")


def main():
    """Test database setup."""
    # Create database manager
    db_manager = DatabaseManager()
    
    # Create tables
    db_manager.create_tables()
    
    # Test with a sample player
    session = db_manager.get_session()
    
    try:
        # Create a test player
        test_player = Player(
            name="Scottie Scheffler",
            pga_tour_id="46046",
            country="USA"
        )
        session.add(test_player)
        session.commit()
        
        # Query the player
        player = session.query(Player).filter_by(name="Scottie Scheffler").first()
        print(f"Created player: {player}")
        
    finally:
        session.close()


if __name__ == "__main__":
    main()