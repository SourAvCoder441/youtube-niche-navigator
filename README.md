# NicheNavigator  
### A Structured Decision Companion for Aspiring YouTube Creators

---

## 1. Problem Understanding

Starting a YouTube channel is a complex decision involving multiple trade-offs.  
An aspiring creator must balance:

- Skill alignment
- Time availability
- Monetization potential
- Competition intensity
- Growth opportunities
- Initial investment requirements

These factors are often evaluated intuitively, leading to poor alignment and burnout.

This system models the decision as a **multi-criteria weighted evaluation problem** and provides structured, explainable recommendations.

The goal is not to predict success, but to support rational decision-making.

---

## 2. System Overview

NicheNavigator evaluates predefined YouTube niches using:

- User-defined weight preferences
- Goal-based automatic weight adjustments
- Normalized scoring
- Risk modeling
- Ranked recommendations (Top 3)
- **Comparative explanations** with percentile rankings

The system is deterministic and does not rely on black-box AI for final decision-making.

---

## 3. Architecture

The system is divided into modular components:

1. Web Layer (Flask Interface – Day 4)
2. Decision Engine (Scoring Logic)
3. Weight Adjustment Module
4. Risk Analysis Module
5. Explanation Module (with comparison context)
6. Sensitivity Analysis Module

The decision engine is fully independent of the web layer for testability and modularity.

---

## 4. Decision Criteria

Each niche is evaluated across six criteria:

- Skill Alignment (maximize)
- Time Compatibility (maximize)
- Monetization Potential (maximize)
- Competition Level (minimize)
- Growth Potential (maximize)
- Initial Investment (minimize)

---

## 5. Scoring Methodology

### Normalization

For maximize criteria:
(value - min) / (max - min)

For minimize criteria:
(max - value) / (max - min)

### Final Score

Final Score = Σ(weight × normalized_value)

Weights are:

- Provided by the user (1–10 scale)
- Adjusted based on user goal
- Normalized to sum = 1

---

## 6. Risk Model

Risk Index is calculated as:

0.4 × Competition  
+ 0.3 × Investment  
+ 0.3 × (10 - Skill Alignment)

Risk Levels:

- ≥ 7 → High
- 4–7 → Moderate
- &lt; 4 → Low

---

## 7. Modeled Niches

The system evaluates 10 niches across the risk/reward spectrum:

| Niche | Skill | Competition | Key Characteristic |
|-------|-------|-------------|-------------------|
| Coding Tutorials | 9 | 8 | Technical expertise required |
| AI Tools & Tech Explainers | 8 | 6 | Trending, fast monetization |
| Gaming Content | 5 | 9 | High competition, entertainment-driven |
| Personal Finance | 7 | 7 | High trust barrier, strong CPM |
| Creative Design | 8 | 6 | Portfolio-based, visual skill |
| Health & Fitness | 6 | 8 | YMYL category, results-based credibility |
| Productivity & Lifestyle | 4 | 9 | Low barrier, "beginner trap" |
| Book Reviews & Literature | 5 | 5 | Minimal investment, slow growth |
| Business & Entrepreneurship | 7 | 7 | Credibility-dependent, high monetization |
| Science & Education | 9 | 5 | High accuracy, expertise barrier |

These niches were selected to represent varying trade-offs in competition, monetization, effort, and risk profiles.

---

## 8. Assumptions & Justification

The scoring values assigned to each niche are structured estimates based on:

- Observed YouTube ecosystem patterns (2024-2025)
- Creator economy trends and CPM data
- General market behavior
- Category saturation characteristics

The system prioritizes **relative comparison** rather than exact prediction.

---

## 9. Limitations

- Scores are relative and simplified.
- Real-world outcomes depend heavily on execution quality.
- Market dynamics evolve rapidly.
- Personal differentiation strategies are not modeled.
- 10 niches provide coverage but not exhaustive options.

---

## 10. How to Run

1. Activate virtual environment
2. Install dependencies:
   pip install -r requirements.txt
3. Run tests:
   python -m tests.manual_test

(Day 4: Web interface with prompt-based input coming next.)

---

## 11. Future Improvements

- [x] Sensitivity analysis
- [x] Dynamic niche expansion (10 niches)
- [x] Enhanced explanations with comparison context
- [ ] Natural language prompt input
- [ ] Web interface with interactive visualizations
- [ ] Growth advisor module (post-selection guidance)
- [ ] Data-driven niche modeling using public datasets

---

## 12. Decision Transparency

### Why deterministic scoring over AI?

We explicitly chose weighted multi-criteria decision analysis (MCDA) because:
- **Explainability**: Every score can be traced to specific criteria weights
- **User control**: Users can adjust weights and immediately see impact
- **No data dependency**: Works without training data or API calls
- **Predictable behavior**: Same inputs always produce same outputs

### Scoring Formula
For each niche N: