"""
Manual test script for decision engine with new features.
Run with: python -m tests.manual_test
"""

import sys
import os

# Ensure proper import path
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
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def main():
    """Run comprehensive manual test."""
    
    print_section("NicheNavigator - Day 2 Enhanced Test")
    
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
    print(f"Adjusted Weights (normalized):")
    for criterion, weight in weights.items():
        base = base_weights[criterion]
        change = "↑" if weight > base/10 else "↓" if weight < base/10 else "="
        print(f"  {criterion:15} {base:2} → {weight:.3f} {change}")
    
    # Scoring
    print_section("Scoring Results")
    scores = calculate_scores(NICHES, weights)
    ranked = rank_niches(scores)
    
    print(f"{'Rank':<6} {'Niche':<30} {'Score':<8} {'Key Driver'}")
    print("-" * 70)
    
    for rank, (niche_name, data) in enumerate(ranked, 1):
        # Find top contributor
        top_criterion = max(data["contributions"].items(), key=lambda x: x[1])
        print(f"{rank:<6} {niche_name:<30} {data['final_score']:.4f}   {top_criterion[0]}")
    
    # Risk Analysis & Explanations
    print_section("Detailed Analysis with Explanations")
    
    for rank, (niche_name, data) in enumerate(ranked, 1):
        attributes = NICHES[niche_name]["attributes"]
        risk_score, risk_level = calculate_risk(attributes)
        
        explanation = generate_explanation(
            niche_name, attributes, data["contributions"], 
            risk_score, risk_level, weights
        )
        
        print(f"\n#{rank} {niche_name}")
        print(f"   Score: {data['final_score']:.4f} | Risk: {risk_level} ({risk_score})")
        print(f"   Summary: {explanation['summary']}")
        
        if explanation['strengths']:
            print(f"   Strengths:")
            for s in explanation['strengths']:
                print(f"      • {s['criterion_label']}: {s['context']}")
        
        if explanation['concerns']:
            print(f"   Concerns:")
            for c in explanation['concerns']:
                print(f"      • {c['criterion_label']}: {c['context']}")
        
        print(f"   Recommendation: {explanation['recommendation'][:80]}...")
    
    # Sensitivity Analysis
    print_section("Sensitivity Analysis")
    sensitivity = analyze_sensitivity(NICHES, base_weights, goal)
    
    print(f"Confidence Level: {sensitivity['confidence']['level']}")
    print(f"Assessment: {sensitivity['confidence']['description']}")
    print(f"\nStability by Niche:")
    
    for niche, analysis in sensitivity['stability_analysis'].items():
        stable_icon = "✓" if analysis['is_stable'] else "⚠"
        print(f"  {stable_icon} {niche:<30} "
              f"Rank: {analysis['most_common_rank']} "
              f"(stability: {analysis['stability_score']:.0%})")
    
    if sensitivity['alternative_scenarios']:
        print(f"\nAlternative Scenarios:")
        for alt in sensitivity['alternative_scenarios']:
            print(f"  • {alt['scenario']}: {alt['implication']}")
    
    print_section("Test Complete")
    print("All modules integrated successfully.")
    print("Ready for web interface integration (Day 3).")


if __name__ == "__main__":
    main()