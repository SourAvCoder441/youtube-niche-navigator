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

The system is deterministic and does not rely on black-box AI for final decision-making.

---

## 3. Architecture

The system is divided into modular components:

1. Web Layer (Flask Interface – upcoming)
2. Decision Engine (Scoring Logic)
3. Weight Adjustment Module
4. Risk Analysis Module
5. Explanation Module

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
- < 4 → Low

---

## 7. Modeled Niches

The system currently evaluates:

1. Coding Tutorials
2. AI Tools & Tech Explainers
3. Gaming Content

These niches were selected to represent varying trade-offs in competition, monetization, and effort.

---

## 8. Assumptions & Justification

The scoring values assigned to each niche are structured estimates based on:

- Observed YouTube ecosystem patterns
- Creator economy trends
- General market behavior
- Category saturation characteristics

The system prioritizes relative comparison rather than exact prediction.

---

## 9. Limitations

- Scores are relative and simplified.
- Real-world outcomes depend heavily on execution quality.
- Market dynamics evolve rapidly.
- Personal differentiation strategies are not modeled.

---

## 10. How to Run

1. Activate virtual environment
2. Install dependencies:
   pip install -r requirements.txt
3. Run tests:
   python -m tests.manual_test

(Flask web interface integration coming next.)

---

## 11. Future Improvements

- Sensitivity analysis visualization
- Dynamic niche expansion
- Structured AI-assisted explanation generation
- Data-driven niche modeling using public datasets