from decision_engine.niche_profiles import NICHES
from decision_engine.weight_adjuster import adjust_weights
from decision_engine.scorer import calculate_scores
from decision_engine.risk_analysis import calculate_risk

base_weights = {
    "skill": 7,
    "time": 6,
    "monetization": 8,
    "competition": 5,
    "growth": 7,
    "investment": 4
}

goal = "side_income"

weights = adjust_weights(base_weights, goal)

scores = calculate_scores(NICHES, weights)

print("Adjusted Weights:", weights)
print("Scores:", scores)

for niche in NICHES:
    risk = calculate_risk(NICHES[niche])
    print(niche, "Risk:", risk)