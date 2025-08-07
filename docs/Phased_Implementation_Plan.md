# GolfPredict Simplified - Phased Implementation Plan

## Project Overview

**Goal**: Build a golf betting intelligence system that proves we can beat market odds by 3-5% ROI
**Timeline**: 6-8 weeks to profitable paper trading
**Team Size**: 1-2 developers
**Budget**: ~$200/month for data and hosting

---

## Phase 0: Foundation & Proof of Concept (Week 1)

**Objective**: Prove the edge exists before building anything complex

### What to Build

- Historical odds scraper
- Simple backtesting framework
- ROI calculator

### Tech Stack

- **Language**: Python 3.11
- **Database**: SQLite (yes, really - for proof of concept)
- **Notebook**: Jupyter for exploration
- **Version Control**: Git + GitHub

### Key Deliverables

- [ ] 2 years of historical tournament results
- [ ] Closing odds for top 20 players each tournament
- [ ] Simple strategy backtest showing potential edge
- [ ] Go/No-Go decision based on results

### Context to Maintain

```
project_context/
├── data_sources.md          # Where to scrape, API endpoints
├── betting_strategy.md      # Core hypothesis and edge sources
├── terminology.md           # Golf/betting terms glossary
└── backtest_results.md      # Proof of concept findings
```

---

## Phase 1: Data Pipeline MVP (Week 2-3)

**Objective**: Automate data collection for core edge factors

### What to Build

- PGA Tour results scraper
- Weather data collector
- Basic odds tracker
- Database schema

### Tech Stack

- **Database**: PostgreSQL 15 + TimescaleDB extension
- **Task Queue**: APScheduler (simpler than Celery)
- **HTTP Client**: httpx (async support)
- **Data Validation**: Pydantic v2
- **Environment**: Docker Compose

### Key Deliverables

- [ ] Automated daily data collection
- [ ] 3 core data sources integrated
- [ ] Database with proper indexes
- [ ] Data quality monitoring

### Context to Maintain

```
project_context/
├── database/
│   ├── schema.sql           # Current database structure
│   ├── sample_queries.sql   # Common queries for reference
│   └── data_dictionary.md   # What each field means
├── apis/
│   ├── weather_api.md       # Endpoints, rate limits, auth
│   ├── odds_api.md          # Which bookmakers, update frequency
│   └── scraping_notes.md    # CSS selectors, anti-bot strategies
└── data_pipeline.md         # How data flows through system
```

---

## Phase 2: Feature Engineering (Week 3-4)

**Objective**: Transform raw data into predictive features

### What to Build

- Player performance aggregations
- Weather-adjusted scoring metrics
- Course fit calculations
- Form/momentum indicators

### Tech Stack

- **SQL Views**: PostgreSQL materialized views
- **Python**: pandas + numpy for complex calcs
- **Caching**: Redis for computed features
- **Monitoring**: Simple logging + alerts

### Key Deliverables

- [ ] 20-30 core features per player
- [ ] Automated feature refresh
- [ ] Feature importance analysis
- [ ] Performance baselines

### Context to Maintain

```
project_context/
├── features/
│   ├── feature_definitions.md   # How each feature is calculated
│   ├── feature_importance.md    # Which features matter most
│   └── sql_views.sql           # Materialized view definitions
├── analysis/
│   ├── eda_findings.md         # Exploratory data analysis
│   └── correlation_matrix.png   # Feature relationships
└── performance_metrics.md       # Baseline model results
```

---

## Phase 3: Prediction Engine (Week 4-5)

**Objective**: Build model that beats market odds

### What to Build

- Tournament outcome predictor
- Monte Carlo simulator
- Probability calculator
- Model versioning system

### Tech Stack

- **ML Framework**: scikit-learn + LightGBM
- **Experimentation**: MLflow (local mode)
- **Serving**: FastAPI
- **Testing**: pytest + hypothesis

### Key Deliverables

- [ ] Trained model beating baseline
- [ ] 10k simulation Monte Carlo
- [ ] API endpoint for predictions
- [ ] Model performance tracking

### Context to Maintain

```
project_context/
├── models/
│   ├── model_architecture.md    # Why LightGBM, hyperparameters
│   ├── training_pipeline.md     # How to retrain models
│   ├── evaluation_metrics.md    # What success looks like
│   └── experiment_log.md        # What we've tried, results
├── api/
│   ├── endpoint_docs.md         # API design decisions
│   └── response_schemas.json    # API contracts
└── monte_carlo_logic.md         # Simulation methodology
```

---

## Phase 4: Betting Intelligence (Week 5-6)

**Objective**: Convert predictions into actionable bets

### What to Build

- Market odds comparison
- Edge calculator
- Kelly criterion optimizer
- Bet tracking system

### Tech Stack

- **Queue**: Python asyncio (no Redis needed yet)
- **Alerts**: Email/Discord webhooks
- **Dashboard**: Streamlit (for MVP)
- **Deployment**: Docker on DigitalOcean

### Key Deliverables

- [ ] Live edge detection
- [ ] Optimal bet sizing
- [ ] Performance tracking
- [ ] Simple web interface

### Context to Maintain

```
project_context/
├── betting/
│   ├── kelly_criterion.md       # Bet sizing math
│   ├── bankroll_management.md   # Risk parameters
│   ├── edge_thresholds.md       # When to bet
│   └── booking_tracking.md      # How we track bets
├── deployment/
│   ├── infrastructure.md        # Server setup, DNS
│   ├── monitoring.md            # What to watch
│   └── rollback_plan.md         # When things go wrong
└── results_tracking.md          # Paper trading performance
```

---

## Phase 5: Validation & Scale Prep (Week 6-8)

**Objective**: Prove consistent profitability before real money

### What to Build

- A/B testing framework
- Advanced features (news sentiment)
- Performance analytics
- Scale planning

### Tech Stack Upgrades (Only if Profitable)

- **Message Queue**: Redpanda (if >1k events/sec)
- **Feature Store**: Feast (if >50 features)
- **GPU**: For faster Monte Carlo
- **CDN**: For API responses

### Key Deliverables

- [ ] 3 months paper trading results
- [ ] Statistical significance tests
- [ ] Scaling roadmap
- [ ] Investor pitch deck

### Context to Maintain

```
project_context/
├── validation/
│   ├── paper_trading_log.csv    # Every bet made
│   ├── roi_analysis.md          # Profitability breakdown
│   ├── statistical_tests.md     # Significance calculations
│   └── edge_sources.md          # Where edge comes from
├── scaling/
│   ├── bottleneck_analysis.md   # Current limitations
│   ├── cost_projections.md      # At 10x, 100x scale
│   └── tech_debt.md             # What to refactor
└── business_plan.md             # Go-to-market strategy
```

---

## Working with Claude Code

### Project Structure

```
golfpredict/
├── src/
│   ├── collectors/      # Data collection scripts
│   ├── features/        # Feature engineering
│   ├── models/          # ML models
│   ├── api/            # FastAPI application
│   └── betting/        # Betting logic
├── tests/              # Test suite
├── notebooks/          # Jupyter explorations
├── project_context/    # All documentation
├── docker-compose.yml  # Local dev environment
└── pyproject.toml     # Poetry dependencies
```

### Context Management Strategy

1. **Before Each Session**: Share the relevant context files

   ```
   "I'm working on Phase 2 of GolfPredict. Here's my current
   database schema and feature definitions..."
   ```

2. **Document Decisions**: After each session, update context

   ```
   "We decided to use materialized views because..."
   ```

3. **Maintain Examples**: Keep working code snippets
   ```
   project_context/code_snippets/
   ├── scraping_example.py
   ├── feature_calc.sql
   └── model_training.py
   ```

### Phase Transition Checklist

Before moving to next phase:

- [ ] Current phase deliverables complete
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Performance benchmarked
- [ ] Next phase requirements clear

---

## Critical Success Factors

### Technical

- Keep it simple - resist over-engineering
- Measure everything - latency, accuracy, ROI
- Fail fast - if no edge by Phase 1, pivot

### Business

- Start with paper trading only
- Focus on proven edges (weather + form)
- Build for one sport first

### When to Add Complexity

Only upgrade when you hit these limits:

- SQLite → PostgreSQL: >1GB data or >10 writes/sec
- APScheduler → Celery: >100 tasks/minute
- Streamlit → React: >50 daily users
- Single server → Kubernetes: >$1k/month revenue

---

## Cost Management

### Phase 0-2: ~$50/month

- Development on local machine
- Free tier APIs where possible

### Phase 3-4: ~$200/month

- Small VPS ($40)
- Weather API ($50)
- Odds API ($99)

### Phase 5+: Scale with revenue

- Only add paid services when ROI proven
- Each $100 in costs should drive $300+ in value

---

## Red Flags to Watch

1. **No edge in backtesting** → Stop immediately
2. **API costs > projected revenue** → Find alternatives
3. **Predictions no better than market** → Refocus on features
4. **Too complex to maintain solo** → Simplify architecture
5. **Legal concerns in target market** → Pivot geography/model
