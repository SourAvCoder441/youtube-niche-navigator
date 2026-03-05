"""
Sensitivity analysis for recommendation stability.
"""

import copy
from decision_engine.scorer import calculate_scores, rank_niches
from decision_engine.weight_adjuster import normalize_weights, adjust_weights


def _apply_goal(weights, goal):
    return adjust_weights(weights, goal) if goal else normalize_weights(weights)


def analyze_sensitivity(niches, base_weights, goal=None, perturbation=0.15, iterations=3):
    adjusted_weights = _apply_goal(base_weights, goal)
    base_results = calculate_scores(niches, adjusted_weights)
    base_ranked = rank_niches(base_results)
    base_ranking = [name for name, _ in base_ranked]
    base_scores = {name: data["final_score"] for name, data in base_results.items()}

    position_counts = {name: {i: 0 for i in range(len(niches))} for name in niches}
    winner_changes = 0
    total_tests = 0

    criteria = list(base_weights.keys())
    for criterion in criteria:
        for direction in (-1, 1):
            for step in range(1, iterations + 1):
                delta = direction * (perturbation * step) * 10
                test_weights = copy.deepcopy(base_weights)
                test_weights[criterion] = max(1, min(10, test_weights[criterion] + delta))
                test_adjusted = _apply_goal(test_weights, goal)
                test_results = calculate_scores(niches, test_adjusted)
                test_ranking = [name for name, _ in rank_niches(test_results)]

                for pos, niche in enumerate(test_ranking):
                    position_counts[niche][pos] += 1

                if test_ranking[0] != base_ranking[0]:
                    winner_changes += 1
                total_tests += 1

    stability_analysis = {}
    for niche in niches:
        positions = []
        for pos, count in position_counts[niche].items():
            positions.extend([pos] * count)

        avg_position = sum(positions) / len(positions) if positions else 0
        variance = sum((p - avg_position) ** 2 for p in positions) / len(positions) if positions else 0
        most_common_pos = max(position_counts[niche].items(), key=lambda x: x[1])
        stability_score = (most_common_pos[1] / total_tests) if total_tests else 0

        stability_analysis[niche] = {
            "most_common_rank": most_common_pos[0] + 1,
            "stability_score": round(stability_score, 2),
            "position_variance": round(variance, 2),
            "is_stable": stability_score >= 0.7,
            "base_score": base_scores[niche],
        }

    alternatives = find_alternative_scenarios(niches, base_weights, goal, base_ranking)
    winner_flip_ratio = (winner_changes / total_tests) if total_tests else 0
    confidence = assess_confidence(stability_analysis, winner_flip_ratio, alternatives)

    return {
        "base_ranking": base_ranking,
        "stability_analysis": stability_analysis,
        "alternative_scenarios": alternatives,
        "confidence": confidence,
        "test_parameters": {
            "perturbation": perturbation,
            "iterations": iterations,
            "total_tests": total_tests,
            "winner_flip_ratio": round(winner_flip_ratio, 2),
        },
    }


def find_alternative_scenarios(niches, base_weights, goal, base_ranking):
    scenarios = []
    tests = [
        ("monetization_priority", {"monetization": 10, "competition": 1, "growth": 10}),
        ("risk_averse", {"competition": 10, "investment": 10, "skill": 10}),
        ("beginner_friendly", {"skill": 1, "time": 1, "investment": 1}),
        ("growth_focused", {"growth": 10, "competition": 5, "monetization": 5}),
    ]

    for scenario_name, override in tests:
        test_weights = copy.deepcopy(base_weights)
        test_weights.update(override)
        adjusted = _apply_goal(test_weights, goal)
        ranking = [name for name, _ in rank_niches(calculate_scores(niches, adjusted))]

        if ranking and ranking[0] != base_ranking[0]:
            scenarios.append(
                {
                    "scenario": scenario_name,
                    "description": get_scenario_description(scenario_name),
                    "winner": ranking[0],
                    "ranking": ranking,
                    "implication": f"If priorities shift to {scenario_name.replace('_', ' ')}, {ranking[0]} becomes #1.",
                }
            )
    return scenarios


def get_scenario_description(scenario_name):
    descriptions = {
        "monetization_priority": "Maximum focus on revenue and growth",
        "risk_averse": "Strong preference for lower competition and lower investment",
        "beginner_friendly": "Low skill, low time, low investment constraints",
        "growth_focused": "Higher focus on audience growth potential",
    }
    return descriptions.get(scenario_name, scenario_name)


def assess_confidence(stability_analysis, winner_flip_ratio, alternatives):
    stable_count = sum(1 for v in stability_analysis.values() if v["is_stable"])
    stability_ratio = stable_count / len(stability_analysis) if stability_analysis else 0

    if stability_ratio >= 0.8 and winner_flip_ratio <= 0.15 and not alternatives:
        level = "High"
        description = "Winner remains stable across most weight perturbations."
        action = "Proceed with confidence and start execution planning."
    elif stability_ratio >= 0.5 and winner_flip_ratio <= 0.35:
        level = "Moderate"
        description = "Winner is generally stable but can change under specific priority shifts."
        action = "Review alternative scenarios before committing."
    else:
        level = "Low"
        description = "Winner is sensitive to weight changes."
        action = "Refine priorities and rerun evaluation."

    return {
        "level": level,
        "description": description,
        "action": action,
        "stability_ratio": round(stability_ratio, 2),
        "winner_flip_ratio": round(winner_flip_ratio, 2),
    }
