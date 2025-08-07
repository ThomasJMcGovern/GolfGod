# GolfGod- Golf Betting Intelligence System

## 🎯 Project Overview

GolfGod is a data-driven golf betting intelligence system designed to identify and exploit market inefficiencies in PGA Tour betting markets. Our goal is to achieve a consistent 3-5% ROI through systematic analysis of weather conditions, player form, and course fit.

## 📊 Current Phase: Phase 0 - Proof of Concept

**Objective**: Prove that a profitable edge exists before building complex infrastructure.

**Success Criteria**:

- ✅ 3-5% ROI in backtesting
- ✅ Statistical significance (p < 0.05)
- ✅ Minimum 50 tournaments analyzed

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git
- 2GB free disk space

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/GolfGpt.git
cd GolfGpt
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run initial setup:

```bash
python -m src.database.models  # Create database tables
```

### Testing the Setup

1. Test data collectors:

```bash
python -m src.collectors.pga_scraper
python -m src.collectors.weather_collector
python -m src.collectors.odds_importer
```

2. Test backtesting framework:

```bash
python -m src.backtesting.strategy
python -m src.backtesting.roi_calculator
```

## 📁 Project Structure

```
GolfGpt/
├── docs/                    # Documentation
│   ├── Phase_0_Claude_Code_Plan.md
│   ├── Phased_Implementation_Plan.md
│   └── Context_Management_Template.md
├── src/                     # Source code
│   ├── collectors/          # Data collection modules
│   ├── database/           # Database models and management
│   ├── backtesting/        # Strategy backtesting framework
│   └── analysis/           # Edge analysis tools
├── data/                   # Data storage
│   ├── raw/               # Raw scraped data
│   ├── processed/         # Cleaned data
│   └── golfpredict.db     # SQLite database
├── notebooks/             # Jupyter notebooks for exploration
├── tests/                 # Test suite
└── requirements.txt       # Python dependencies
```

## 🔧 Core Components

### Data Collection

- **PGA Tour Scraper**: Tournament results and player statistics
- **Weather Collector**: Historical weather data from Open-Meteo API
- **Odds Importer**: Manual CSV import (Phase 0) → API integration (Phase 1)

### Betting Strategies

1. **Weather Edge**: Exploit market's undervaluation of wind impact
2. **Form Momentum**: Recent performance prediction
3. **Course Fit**: Historical course performance analysis

### Analysis Tools

- **ROI Calculator**: Comprehensive performance metrics with statistical validation
- **Backtesting Engine**: Historical strategy testing
- **Edge Analyzer**: Identify profitable betting opportunities

## 📈 Strategy Performance Targets

| Metric       | Minimum | Target | Current |
| ------------ | ------- | ------ | ------- |
| ROI          | 3%      | 5-7%   | TBD     |
| Win Rate     | 10%     | 12-15% | TBD     |
| Sharpe Ratio | 0.5     | 1.0+   | TBD     |
| P-value      | <0.05   | <0.01  | TBD     |

## 🤝 Team Collaboration

### Roles

- **Developer (You)**: Project management, infrastructure, React visualizations
- **Co-founder**: Betting strategy validation, bankroll management
- **Claude Code (Me)**: Python implementation, data analysis, ML models

### Working Together

1. Daily standups to review progress
2. Co-founder validates all betting logic
3. You handle project direction and infrastructure
4. I implement technical solutions and analysis

## 📅 Phase 0 Timeline (Week 1)

- [x] Day 1: Environment setup and project structure
- [ ] Day 2: PGA Tour scraper implementation
- [ ] Day 3: Weather and odds collection
- [ ] Day 4: Database and models
- [ ] Day 5: Backtesting engine
- [ ] Day 6: Analysis and visualization
- [ ] Day 7: Go/No-Go decision

## 🎯 Next Steps

1. **Immediate**: Set up GitHub repository and share with team
2. **Tomorrow**: Start collecting 2024 PGA Tour data
3. **This Week**: Complete Phase 0 and make go/no-go decision
4. **If GO**: Move to Phase 1 with automated data pipeline

## 💰 Budget

**Phase 0**: $0-50 (free data sources)
**Phase 1+**: ~$200/month (APIs and hosting)

## 📝 Notes

- Keep it simple - we're proving the concept, not building for scale yet
- Document all decisions for future reference
- Your co-founder should review all betting logic
- We'll move fast but validate everything

## 🤔 Questions?

Contact the team:

- Technical: Work with Claude Code in this session
- Strategy: Consult with your co-founder
- Project: You're the project lead!

---

_Built with Claude Code assistance - Phase 0 in progress_# GolfGod
