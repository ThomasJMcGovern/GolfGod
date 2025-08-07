# GolfPredict Context Management Template

## How to Use This Template

When working with Claude Code, paste relevant sections at the start of each session. Update after each major decision or implementation.

---

## 🎯 Current Project State

**Current Phase**: Phase 0 - Proof of Concept
**Sprint Goal**: Prove 3-5% edge exists in historical data
**Blocking Issues**: None
**Last Updated**: 2024-12-07

### Progress Today:
- ✅ Environment setup complete (Python 3.13 compatibility resolved)
- ✅ All modules tested and working
- ✅ PGA Tour scraper enhanced with 34 tournaments for 2024
- ✅ GitHub repository created and code pushed
- ✅ Jupyter notebook created for data exploration
- ⏳ Need historical odds data from co-founder

---

## 🏗️ Architecture Decisions

### Tech Stack (Locked for MVP)

```
Language: Python 3.11
Database: PostgreSQL 15 + TimescaleDB
API: FastAPI
Cache: Redis
Deploy: Docker Compose → DigitalOcean
```

### Why These Choices

- PostgreSQL: Powerful analytics with materialized views
- FastAPI: Type safety + automatic docs
- Redis: Simple caching without complexity
- Docker: Reproducible environments

---

## 📊 Data Schema

### Core Tables

```sql
-- Players
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    pga_tour_id VARCHAR(50) UNIQUE
);

-- Tournaments
CREATE TABLE tournaments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    course_id INTEGER,
    start_date DATE,
    purse DECIMAL(10,2)
);

-- Rounds
CREATE TABLE rounds (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id),
    player_id INTEGER REFERENCES players(id),
    round_num INTEGER,
    score INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Weather
CREATE TABLE weather_observations (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id),
    observation_time TIMESTAMPTZ,
    temp_f DECIMAL(5,2),
    wind_mph DECIMAL(5,2),
    wind_direction INTEGER,
    conditions VARCHAR(50)
);
```

---

## 🔧 Key Algorithms

### Monte Carlo Simulation

```
1. Get player skill distributions (mean, std dev)
2. Add course/weather adjustments
3. Run 10,000 tournaments:
   - Sample each player's score from distribution
   - Rank players
   - Track finishing positions
4. Calculate probabilities from frequencies
```

### Feature Engineering Priority

1. **Strokes Gained** (vs field last 20 rounds)
2. **Course Fit** (performance at similar courses)
3. **Current Form** (weighted recent results)
4. **Weather Performance** (scoring in wind/cold)

---

## 📈 Model Performance Targets

### Minimum Viable Model

- ROI: >3% after vig
- Top-10 Accuracy: >65%
- Winner Accuracy: >8%
- Calibration: Within 5% of predicted probs

### Stretch Goals

- ROI: >7%
- Live betting edge: >2%
- Head-to-head accuracy: >55%

---

## 🚀 Current Sprint Tasks

### Phase 0 Checklist

- [x] Set up development environment
- [x] Create project structure
- [x] Build data collectors (PGA, weather, odds)
- [x] Implement backtesting framework
- [x] Create ROI calculator with statistical validation
- [x] Load 2024 PGA Tour tournament list (34 tournaments)
- [ ] Scrape actual tournament results (currently using sample data)
- [ ] Get historical weather for tournaments
- [ ] **CRITICAL: Find closing odds data from co-founder**
- [ ] Run full backtest on 50+ tournaments
- [ ] Calculate actual ROI
- [ ] Document edge sources

### Next Sprint Planning

If Phase 0 shows edge > 3%:

- Set up PostgreSQL + TimescaleDB
- Build automated scrapers
- Design feature tables

---

## 🐛 Known Issues & Solutions

### Data Quality

- **Problem**: PGA Tour site changes HTML frequently
- **Solution**: Use multiple selectors, add monitoring

### Rate Limiting

- **Problem**: Weather API has 1000 calls/day limit
- **Solution**: Cache aggressively, batch requests

### Model Overfitting

- **Problem**: Too many features, not enough data
- **Solution**: Start with 5-10 features max

---

## 📝 Code Patterns

### Async Data Collection

```python
async def collect_data():
    async with httpx.AsyncClient() as client:
        # Always add timeout and retry logic
        response = await client.get(url, timeout=30)
        return response.json()
```

### Database Best Practices

```python
# Always use connection pools
# Always use parameterized queries
# Always handle connection errors
async with db_pool.acquire() as conn:
    await conn.execute(query, *params)
```

### Feature Calculation

```sql
-- Always use materialized views for expensive calcs
-- Always add indexes on join columns
-- Always timestamp when refreshed
```

---

## 🔗 External Resources

### Data Sources

- **PGA Tour**: https://www.pgatour.com/stats
- **Weather**: https://www.tomorrow.io/weather-api/
- **Odds**: https://the-odds-api.com/

### Documentation

- **FastAPI**: https://fastapi.tiangolo.com/
- **TimescaleDB**: https://docs.timescale.com/
- **LightGBM**: https://lightgbm.readthedocs.io/

### Competition Research

- **DataGolf**: How they model
- **DraftKings**: Pricing strategy
- **BetMGM**: Market making

---

## 💭 Design Philosophy

### Core Principles

1. **Ship beats perfect** - Get to paper trading ASAP
2. **Measure everything** - Data wins arguments
3. **Simple scales** - Complexity kills projects
4. **Edge first** - Without edge, nothing matters

### What We're NOT Building (Yet)

- Mobile app
- Social features
- Multiple sports
- Real-time shot tracking
- AI commentary

---

## 🎪 Session Prompts for Claude Code

### Starting a Session

```
I'm working on GolfPredict Phase [X].
Current goal: [specific task]
Here's my current [relevant context section]
Help me implement [specific feature]
```

### Debugging

```
Expected: [what should happen]
Actual: [what's happening]
Here's the relevant code and error:
[paste code and stack trace]
```

### Architecture Decisions

```
I need to choose between:
Option A: [description]
Option B: [description]
Context: [current scale, constraints]
What are the tradeoffs?
```

---

## 📅 Progress Log

### Day 1 (2024-12-07)

- ✅ Set up development environment (resolved Python 3.13 compatibility)
- ✅ Created complete project structure
- ✅ Built all core modules (scrapers, database, backtesting)
- ✅ Set up GitHub repository (https://github.com/ThomasJMcGovern/GolfGod)
- ✅ Loaded 34 PGA Tour tournaments for 2024
- ✅ Created Jupyter notebook for data exploration
- ✅ Tested all modules successfully

**Key Decisions Made:**
- Using SQLite for Phase 0 (easy migration to Supabase later)
- Starting with 3 strategies: Weather Edge, Form Momentum, Course Fit
- Conservative Kelly fraction (25%) for bet sizing
- 5% minimum edge threshold

**Tomorrow's Priority:**
- Connect with co-founder for historical odds data
- Start collecting real tournament results
- Begin weather data collection for tournaments

### Day 2 (Planned)

- [ ] Morning: Co-founder sync on betting strategies
- [ ] Collect real PGA Tour results (10+ tournaments)
- [ ] Match weather data to tournaments
- [ ] Evening: First backtest attempt

### Day 3-7

- [ ] To be planned based on Day 2 results
