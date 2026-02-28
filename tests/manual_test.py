"""
Manual test script for decision engine with 10 niches.
Run with: python -m tests.manual_test
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decision_engine.niche_profiles import NICHES
from decision_engine.weight_adjuster import adjust_weights
from decision_engine.scorer import calculate_scores, rank_niches
from decision_engine.risk_analysis import calculate_risk
from decision_engine.explanation import generate_explanation
from decision_engine.sensitivity import analyze_sensitivity
from decision_engine.validator import validate_weights, validate_goal


def print_section(title):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def main():
    """Run comprehensive manual test with 10 niches."""
    
    print_section("NicheNavigator - Day 3: 10 Niches Test")
    
    print(f"\nLoaded {len(NICHES)} niches:")
    for name in NICHES:
        print(f"  • {name}")
    
    # Test inputs
    base_weights = {
        "skill": 7,
        "time": 6,
        "monetization": 8,
        "competition": 5,
        "growth": 7,
        "investment": 4
    }
    goal = "side_income"
    
    print(f"\nBase Weights: {base_weights}")
    print(f"Selected Goal: {goal}")
    
    # Validation
    print_section("Input Validation")
    try:
        validate_weights(base_weights)
        validate_goal(goal)
        print("✓ All inputs valid")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return
    
    # Weight adjustment
    print_section("Weight Adjustment")
    weights = adjust_weights(base_weights, goal)
    print(f"Adjusted Weights (normalized to 1.0):")
    for criterion, weight in weights.items():
        base = base_weights[criterion]
        change = "↑" if weight > base/10 else "↓" if weight < base/10 else "="
        print(f"  {criterion:15} {base:2} → {weight:.3f} {change}")
    
    # Scoring
    print_section("Scoring Results (Top 5 of 10)")
    scores = calculate_scores(NICHES, weights)
    ranked = rank_niches(scores)
    
    print(f"{'Rank':<6} {'Niche':<30} {'Score':<8} {'Risk':<10} {'Key Driver'}")
    print("-" * 75)
    
    for rank, (niche_name, data) in enumerate(ranked[:5], 1):
        attrs = NICHES[niche_name]["attributes"]
        risk_score, risk_level = calculate_risk(attrs)
        top_criterion = max(data["contributions"].items(), key=lambda x: x[1])
        print(f"{rank:<6} {niche_name:<30} {data['final_score']:.4f}   {risk_level:<10} {top_criterion[0]}")
    
    # Detailed Analysis for Top 3
    print_section("Top 3 Detailed Explanations")
    
    # Prepare all niche data for comparisons
    all_niche_data = {name: {"attributes": NICHES[name]["attributes"], "score": data["final_score"]} 
                      for name, data in scores.items()}
    
    for rank, (niche_name, data) in enumerate(ranked[:3], 1):
        attributes = NICHES[niche_name]["attributes"]
        risk_score, risk_level = calculate_risk(attributes)
        
        explanation = generate_explanation(
            niche_name, 
            attributes, 
            data["contributions"],
            risk_score,
            risk_level,
            weights,
            all_niche_data,
            ranked
        )
        
        print(f"\n{'─'*70}")
        print(f"#{rank} {niche_name}")
        print(f"{'─'*70}")
        print(f"Score: {data['final_score']:.4f} | Risk: {risk_level} ({risk_score})")
        print(f"\nSummary: {explanation['summary']}")
        
        if explanation['strengths']:
            print(f"\nStrengths:")
            for s in explanation['strengths']:
                print(f"  ✓ {s['criterion_label']} ({s['raw_score']}/10, {s['percentile']}th percentile)")
                print(f"    {s['context']}")
        
        if explanation['comparisons']:
            print(f"\nComparisons:")
            for c in explanation['comparisons']:
                icon = "↑" if c['advantage'] else "→"
                print(f"  {icon} {c['message']}")
        
        if explanation['trade_offs'] and not explanation['trade_offs']['is_winner']:
            print(f"\nTrade-offs: {explanation['trade_offs']['message']}")
        
        print(f"\nRecommendation: {explanation['recommendation']}")
    
    # Sensitivity Analysis for Top Recommendation
    print_section("Sensitivity Analysis (Winner Stability)")
    sensitivity = analyze_sensitivity(NICHES, base_weights, goal)
    
    winner = ranked[0][0]
    winner_stability = sensitivity['stability_analysis'][winner]
    
    print(f"Winner: {winner}")
    print(f"Confidence: {sensitivity['confidence']['level']}")
    print(f"Assessment: {sensitivity['confidence']['description']}")
    print(f"\nWinner Stability: {winner_stability['stability_score']:.0%} "
          f"(ranked #{winner_stability['most_common_rank']} in {winner_stability['stability_score']:.0%} of scenarios)")
    
    if sensitivity['alternative_scenarios']:
        print(f"\nAlternative Winners:")
        for alt in sensitivity['alternative_scenarios'][:3]:
            print(f"  • {alt['scenario']}: {alt['winner']}")
            print(f"    {alt['implication']}")
    
    print_section("Test Complete")
    print(f"✓ All {len(NICHES)} niches evaluated successfully")
    print("Ready for web interface integration (Day 4).")


if __name__ == "__main__":
    main()