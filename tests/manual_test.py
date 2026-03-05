"""
Manual test script for the deterministic decision engine.
Run with: python -m tests.manual_test
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decision_engine.niche_profiles import NICHES
from decision_engine.weight_adjuster import adjust_weights
from decision_engine.scorer import calculate_scores, rank_niches
from decision_engine.risk_analysis import calculate_risk
from decision_engine.explanation import generate_explanation
from decision_engine.sensitivity import analyze_sensitivity
from decision_engine.validator import validate_weights, validate_goal


def print_section(title):
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)


def main():
    print_section("NicheNavigator Manual Engine Test")
    print(f"Loaded {len(NICHES)} predefined niches")

    base_weights = {
        "skill": 7,
        "time": 6,
        "monetization": 8,
        "competition": 5,
        "growth": 7,
        "investment": 4,
    }
    goal = "side_income"

    print("\nInput")
    print(f"Base weights: {base_weights}")
    print(f"Goal: {goal}")

    print_section("Validation")
    validate_weights(base_weights)
    validate_goal(goal)
    print("Validation passed")

    print_section("Weight Adjustment")
    adjusted_weights = adjust_weights(base_weights, goal)
    for criterion, value in adjusted_weights.items():
        print(f"{criterion:14}: {value:.3f}")

    print_section("Scoring")
    scores = calculate_scores(NICHES, adjusted_weights)
    ranked = rank_niches(scores)
    print(f"{'Rank':<6}{'Niche':<34}{'Score':<8}{'Risk':<10}")
    print("-" * 72)
    for rank, (name, score_data) in enumerate(ranked[:5], 1):
        risk_score, risk_level = calculate_risk(NICHES[name]["attributes"])
        print(f"{rank:<6}{name:<34}{score_data['final_score']:<8.4f}{risk_level:<10}")

    print_section("Explanations (Top 3)")
    all_niche_data = {
        name: {"attributes": NICHES[name]["attributes"], "score": score_data["final_score"]}
        for name, score_data in scores.items()
    }

    for rank, (name, score_data) in enumerate(ranked[:3], 1):
        attrs = NICHES[name]["attributes"]
        risk_score, risk_level = calculate_risk(attrs)
        explanation = generate_explanation(
            name,
            attrs,
            score_data["contributions"],
            risk_score,
            risk_level,
            adjusted_weights,
            all_niche_data,
            ranked,
        )

        print("\n" + "-" * 72)
        print(f"#{rank} {name}")
        print(f"Score: {score_data['final_score']:.4f} | Risk: {risk_level} ({risk_score})")
        print(f"Summary: {explanation['summary']}")
        print(f"Why not top: {explanation['why_not_top']}")
        print(f"Trade-off: {explanation['trade_offs']['message']}")

        if explanation["comparisons"]:
            print("Comparisons:")
            for comp in explanation["comparisons"]:
                mark = "ADV" if comp["advantage"] else "TRADEOFF"
                print(f"  [{mark}] {comp['message']}")

    print_section("Sensitivity")
    sensitivity = analyze_sensitivity(NICHES, base_weights, goal)
    winner = ranked[0][0]
    winner_stability = sensitivity["stability_analysis"][winner]
    confidence = sensitivity["confidence"]

    print(f"Winner: {winner}")
    print(f"Confidence: {confidence['level']}")
    print(f"Confidence note: {confidence['description']}")
    print(f"Winner stability score: {winner_stability['stability_score']:.2f}")
    print(f"Winner flip ratio: {sensitivity['test_parameters']['winner_flip_ratio']:.2f}")

    if sensitivity["alternative_scenarios"]:
        print("\nAlternative scenarios:")
        for alt in sensitivity["alternative_scenarios"]:
            print(f"- {alt['scenario']}: winner changes to {alt['winner']}")

    print_section("Completed")
    print("Deterministic engine checks completed.")


if __name__ == "__main__":
    main()
