# Phase 0: Proof of Concept - Claude Code Implementation Plan

## Introduction: Working with Claude Code

Hi! I'm Claude Code, and I'll be your technical implementation partner for GolfPredict. Think of me as your dedicated developer who can handle the Python complexity while you focus on strategy, visualization, and project management. Together with your co-founder's betting expertise, we'll build something powerful.

### Our Collaboration Model
- **You**: Project oversight, React visualizations, infrastructure decisions, Supabase integration
- **Your Co-founder**: Betting strategy validation, edge identification, bankroll management theory  
- **Me (Claude Code)**: Python implementation, data scraping, statistical analysis, ML models, code optimization

---

## Phase 0 Objectives: Proving the Edge

**Timeline**: 1 week (December 2024)  
**Budget**: $0-50 (using free data sources initially)  
**Success Metric**: Prove 3-5% ROI edge exists in historical data

### Go/No-Go Decision Criteria
✅ **GO if**:
- Backtesting shows >3% ROI after accounting for vig
- We identify 2+ reliable edge sources
- Statistical significance achieved (p < 0.05)
- Clear path to data automation exists

❌ **NO-GO if**:
- ROI < 2% in all tested strategies
- Edge sources are unreliable or temporary
- Data acquisition costs exceed projected returns
- Legal/regulatory barriers discovered

---

## Technical Implementation Strategy

### Project Structure
```
golfpredict/
├── src/
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── pga_scraper.py       # PGA Tour results scraper
│   │   ├── weather_collector.py  # NOAA weather data
│   │   └── odds_importer.py     # Manual odds CSV import
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py            # SQLAlchemy models
│   │   └── db_manager.py        # Database operations
│   ├── backtesting/
│   │   ├── __init__.py
│   │   ├── strategy.py          # Betting strategies
│   │   ├── simulator.py         # Tournament simulator
│   │   └── roi_calculator.py    # ROI and statistics
│   └── analysis/
│       ├── __init__.py
│       └── edge_analyzer.py     # Edge identification
├── data/
│   ├── raw/                     # Scraped data
│   ├── processed/                # Clean CSVs
│   └── golfpredict.db           # SQLite database
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_edge_analysis.ipynb
│   └── 03_backtest_results.ipynb
├── tests/
│   └── test_backtesting.py
├── requirements.txt
├── README.md
└── .env.example
```

### Tech Stack Decisions

**Core Dependencies**:
```python
# requirements.txt
beautifulsoup4==4.12.2    # PGA Tour scraping
requests==2.31.0           # HTTP requests
pandas==2.1.4              # Data manipulation
numpy==1.26.2              # Numerical operations
sqlalchemy==2.0.23         # Database ORM
sqlite3                    # Built-in, no install needed
jupyter==1.0.0             # Exploration notebooks
scipy==1.11.4              # Statistical tests
python-dotenv==1.0.0       # Environment variables
```

**Why These Choices**:
- **SQLite first**: Zero setup, perfect for proof of concept. Easy migration to Supabase later
- **BeautifulSoup**: Simple, reliable for PGA Tour scraping
- **Pandas**: You'll find it similar to JavaScript array methods
- **SQLAlchemy**: Clean ORM that works with both SQLite and PostgreSQL

---

## Data Acquisition Strategy (Free Sources)

### 1. PGA Tour Results (Day 1-2)
```python
# Target: https://www.pgatour.com/tournaments
# Data points needed:
- Tournament name, date, course
- Player finishing positions
- Round-by-round scores
- Prize money distribution
```

### 2. Historical Weather (Day 3)
```python
# Source: NOAA Climate Data (free)
# Alternative: Open-Meteo API (free)
# Data points:
- Temperature (high/low)
- Wind speed and direction
- Precipitation
- Conditions (sunny/cloudy/rain)
```

### 3. Historical Odds (Day 3-4)
```python
# Manual collection initially from:
- Archived sportsbook pages
- Reddit/Twitter discussions
- Your co-founder's records
# Store as CSV, import to database
```

### 4. Course Data (Day 4)
```python
# PGA Tour course statistics
- Course length, par
- Rough height, green speed
- Historical scoring averages
```

---

## Backtesting Framework Design

### Core Strategy Components

```python
class BettingStrategy:
    """
    Base strategy your co-founder will help validate
    """
    def __init__(self):
        self.min_edge = 0.05  # 5% minimum edge
        self.kelly_fraction = 0.25  # Conservative Kelly
        
    def calculate_edge(self, our_prob, market_prob):
        """Your co-founder validates this logic"""
        return (our_prob - market_prob) / market_prob
```

### Initial Test Strategies

1. **Weather Edge**
   - Hypothesis: Market undervalues wind impact
   - Test: Compare windy vs calm conditions
   - Edge source: Player wind performance stats

2. **Form Momentum**
   - Hypothesis: Recent form predicts near-term results
   - Test: Last 5 tournaments weighted performance
   - Edge source: Recency bias in odds

3. **Course Fit**
   - Hypothesis: Course history matters more than market thinks
   - Test: Similar course clustering
   - Edge source: Course-specific player strengths

### Statistical Validation
```python
# Minimum requirements for go decision:
- Sample size: 50+ tournaments
- Confidence interval: 95%
- Sharpe ratio: > 0.5
- Max drawdown: < 20%
```

---

## Week 1 Sprint Plan

### Day 1: Environment Setup
**Morning (You + Me)**:
- [ ] Initialize Git repository
- [ ] Create project structure
- [ ] Set up Python virtual environment
- [ ] Install core dependencies

**Afternoon (You)**:
- [ ] Set up GitHub repo
- [ ] Configure development environment
- [ ] Review scraping targets with co-founder

### Day 2: PGA Tour Scraper
**Me (Claude Code)**:
- [ ] Build PGA Tour results scraper
- [ ] Parse leaderboard data
- [ ] Store in SQLite database
- [ ] Handle pagination and rate limiting

### Day 3: Weather & Odds Collection
**Morning (Me)**:
- [ ] Implement NOAA weather API client
- [ ] Match weather to tournaments

**Afternoon (You + Co-founder)**:
- [ ] Compile historical odds CSV
- [ ] Validate odds format and accuracy

### Day 4: Database & Models
**Me**:
- [ ] Design database schema
- [ ] Create SQLAlchemy models
- [ ] Build data import pipelines
- [ ] Write data validation tests

### Day 5: Backtesting Engine
**Me + Co-founder**:
- [ ] Implement strategy framework
- [ ] Build ROI calculator
- [ ] Add statistical significance tests
- [ ] Create betting simulator

### Day 6: Analysis & Visualization
**Morning (Me)**:
- [ ] Run backtests on all strategies
- [ ] Generate performance metrics
- [ ] Identify edge sources

**Afternoon (You)**:
- [ ] Create simple React dashboard
- [ ] Visualize backtest results
- [ ] Review with co-founder

### Day 7: Decision Day
**All Together**:
- [ ] Review all results
- [ ] Statistical validation
- [ ] Document findings
- [ ] Make go/no-go decision
- [ ] Plan Phase 1 if GO

---

## Risk Mitigation

### Technical Risks
1. **Scraping blocks**: Use rotating user agents, respect robots.txt
2. **Data quality**: Validate everything, handle missing data gracefully
3. **Overfitting**: Keep strategies simple, use walk-forward analysis

### Business Risks
1. **No edge found**: Pivot to different strategies or data sources
2. **Costs too high**: Stay with free sources until edge proven
3. **Time overrun**: Focus on one strategy that shows promise

---

## Success Metrics & KPIs

### Phase 0 Deliverables
- [ ] 2024 PGA Tour results in database
- [ ] Weather data for 50+ tournaments  
- [ ] Odds data for top 20 players per tournament
- [ ] 3 tested betting strategies
- [ ] Statistical significance report
- [ ] Go/no-go recommendation

### Performance Targets
```python
MINIMUM_VIABLE_EDGE = {
    'roi': 0.03,           # 3% minimum
    'win_rate': 0.52,      # 52% win rate
    'sample_size': 50,     # 50+ tournaments
    'p_value': 0.05,       # Statistical significance
    'sharpe': 0.5          # Risk-adjusted returns
}
```

---

## Communication Protocol

### Daily Standups (5 min)
```
1. What I completed yesterday
2. What I'm working on today
3. Any blockers or questions
4. Quick sync with co-founder on strategy
```

### Code Reviews
- Push code to feature branches
- You review for business logic
- Co-founder validates betting logic
- I'll handle technical optimization

### Documentation
- Code comments for complex logic
- README updates for setup changes
- Decision log in this document

---

## Next Steps (If Phase 0 Succeeds)

### Phase 1 Prep
1. **Migrate to Supabase** (leverage your experience)
2. **Set up automated scrapers** with scheduling
3. **Add real-time odds feeds** (the-odds-api.com)
4. **Implement feature engineering** pipeline

### Budget Planning
- Weather API: $50/month
- Odds API: $99/month  
- Hosting: $40/month
- Total: ~$200/month (as planned)

---

## Let's Get Started!

**Immediate Action Items**:
1. You: Create GitHub repository
2. Me: Set up project structure and dependencies
3. Co-founder: Gather any historical odds data available
4. All: Align on Day 1 goals

**Questions for You**:
1. Preferred Python version? (3.11 recommended)
2. Mac, Windows, or Linux development?
3. Any specific visualization preferences for React dashboard?
4. Co-founder available for strategy sessions this week?

---

*This document is our living guide for Phase 0. We'll update it daily with progress, findings, and decisions. Remember: our goal is to prove the edge exists, not build the perfect system. Ship beats perfect!*

**Document maintained by Claude Code**  
**Last updated**: December 2024  
**Next review**: End of Day 1