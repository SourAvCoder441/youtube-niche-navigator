---

## System Design Diagram

                     ┌──────────────────────────┐
                     │        User Input        │
                     │  (Goal + Weight Sliders) │
                     └─────────────┬────────────┘
                                   ↓
                     ┌──────────────────────────┐
                     │ Goal-Based Weight Adjust │
                     │  (Auto-modifier logic)   │
                     └─────────────┬────────────┘
                                   ↓
                     ┌──────────────────────────┐
                     │      Decision Engine     │
                     │  - Normalization         │
                     │  - Weighted Scoring      │
                     └─────────────┬────────────┘
                                   ↓
                     ┌──────────────────────────┐
                     │      Risk Analysis       │
                     │  - Risk Score Formula    │
                     │  - Risk Classification   │
                     └─────────────┬────────────┘
                                   ↓
                     ┌──────────────────────────┐
                     │      Ranking Engine      │
                     │  - Sort by Final Score   │
                     │  - Select Top 3          │
                     └─────────────┬────────────┘
                                   ↓
                     ┌──────────────────────────┐
                     │    Explanation Module    │
                     │  - Key Contributors      │
                     │  - Risk Summary          │
                     └─────────────┬────────────┘
                                   ↓
                     ┌──────────────────────────┐
                     │        Output Layer      │
                     │  (Ranked Recommendation) │
                     └──────────────────────────┘