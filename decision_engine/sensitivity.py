"""
Sensitivity analysis module for recommendation stability testing.
Analyzes how robust rankings are to weight perturbations.
"""

import copy
from decision_engine.scorer import calculate_scores, rank_niches
from decision_engine.weight_adjuster import normalize_weights


def analyze_sensitivity(niches, base_weights, goal=None, perturbation=0.15, iterations=3):
    """
    Analyze stability of recommendations under weight variations.
    
    Tests how rankings change when individual weights are perturbed by ±15%.
    Returns stability metrics and alternative scenarios.
    
    Args:
        niches: Niche profiles dict
        base_weights: User's base weights before goal adjustment
        goal: Optional goal that was applied
        perturbation: Percentage to perturb weights (default 0.15 = 15%)
        iterations: Number of perturbation levels to test
    
    Returns:
        Dict with stability analysis and confidence assessment
    """
    # Calculate base ranking
    from decision_engine.weight_adjuster import adjust_weights
    adjusted_weights = adjust_weights(base_weights, goal) if goal else normalize_weights(base_weights)
    
    base_results = calculate_scores(niches, adjusted_weights)
    base_ranking = [name for name, _ in rank_niches(base_results)]
    base_scores = {name: data["final_score"] for name, data in base_results.items()}
    
    # Track position stability for each niche
    position_counts = {name: {i: 0 for i in range(len(niches))} for name in niches}
    total_tests = 0
    
    # Test perturbations on each criterion
    criteria = list(base_weights.keys())
    
    for criterion in criteria:
        for direction in [-1, 1]:
            for i in range(1, iterations + 1):
                # Calculate perturbation amount (scaled 1-10 range)
                delta = direction * (perturbation * i) * 10
                
                test_weights = copy.deepcopy(base_weights)
                new_value = test_weights[criterion] + delta
                test_weights[criterion] = max(1, min(10, new_value))
                
                # Apply goal adjustment and normalize
                test_adjusted = adjust_weights(test_weights, goal) if goal else normalize_weights(test_weights)
                
                # Calculate new ranking
                test_results = calculate_scores(niches, test_adjusted)
                test_ranking = [name for name, _ in rank_niches(test_results)]
                
                # Record positions
                for pos, niche in enumerate(test_ranking):
                    position_counts[niche][pos] += 1
                
                total_tests += 1
    
    # Calculate stability metrics
    stability_analysis = {}
    alternative_scenarios = []
    
    for niche in niches:
        # Calculate position variance (lower is more stable)
        positions = []
        for pos, count in position_counts[niche].items():
            positions.extend([pos] * count)
        
        avg_position = sum(positions) / len(positions) if positions else 0
        variance = sum((p - avg_position) ** 2 for p in positions) / len(positions) if positions else 0
        
        # Most common position
        most_common_pos = max(position_counts[niche].items(), key=lambda x: x[1])
        
        stability_score = most_common_pos[1] / total_tests  # % of time in most common position
        
        stability_analysis[niche] = {
            "most_common_rank": most_common_pos[0] + 1,  # 1-indexed
            "stability_score": round(stability_score, 2),
            "position_variance": round(variance, 2),
            "is_stable": stability_score >= 0.7,  # Stable if in same position 70%+ of time
            "base_score": base_scores[niche]
        }
    
    # Identify alternative scenarios (where ranking flips)
    alternative_scenarios = find_alternative_scenarios(niches, base_weights, goal, base_ranking)
    
    # Overall confidence assessment
    stable_count = sum(1 for s in stability_analysis.values() if s["is_stable"])
    confidence = assess_confidence(stable_count, len(niches), alternative_scenarios)
    
    return {
        "base_ranking": base_ranking,
        "stability_analysis": stability_analysis,
        "alternative_scenarios": alternative_scenarios,
        "confidence": confidence,
        "test_parameters": {
            "perturbation": perturbation,
            "total_tests": total_tests
        }
    }


def find_alternative_scenarios(niches, base_weights, goal, base_ranking, threshold=0.05):
    """
    Find specific weight combinations that produce different winners.
    """
    scenarios = []
    
    # Test extreme weight combinations
    extreme_tests = [
        ("monetization_priority", {"monetization": 10, "competition": 1, "growth": 10}),
        ("risk_averse", {"competition": 10, "investment": 10, "skill": 10}),
        ("beginner_friendly", {"skill": 1, "time": 1, "investment": 1}),
        ("growth_focused", {"growth": 10, "competition": 5, "monetization": 5}),
    ]
    
    from decision_engine.weight_adjuster import adjust_weights, normalize_weights
    
    for scenario_name, weight_override in extreme_tests:
        test_weights = copy.deepcopy(base_weights)
        test_weights.update(weight_override)
        
        adjusted = adjust_weights(test_weights, goal) if goal else normalize_weights(test_weights)
        results = calculate_scores(niches, adjusted)
        ranking = [name for name, _ in rank_niches(results)]
        
        if ranking[0] != base_ranking[0]:
            scenarios.append({
                "scenario": scenario_name,
                "description": get_scenario_description(scenario_name),
                "winner": ranking[0],
                "ranking": ranking,
                "implication": f"If you prioritize {scenario_name.replace('_', ' ')}, {ranking[0]} becomes the better choice."
            })
    
    return scenarios


def get_scenario_description(scenario_name):
    """Human readable description of test scenario."""
    descriptions = {
        "monetization_priority": "Maximum focus on revenue and growth potential",
        "risk_averse": "Minimizing competition and investment requirements",
        "beginner_friendly": "Low barriers to entry, minimal requirements",
        "growth_focused": "Prioritizing market growth and opportunity size"
    }
    return descriptions.get(scenario_name, scenario_name)


def assess_confidence(stable_count, total_niches, alternatives):
    """Assess overall confidence in recommendation."""
    stability_ratio = stable_count / total_niches
    
    if stability_ratio >= 0.8 and not alternatives:
        return {
            "level": "High",
            "description": "Recommendation is robust across weight variations. The top choice consistently outperforms alternatives.",
            "action": "Proceed with confidence in the recommended niche."
        }
    elif stability_ratio >= 0.5:
        return {
            "level": "Moderate", 
            "description": "Recommendation is generally stable but sensitive to priority shifts. Review alternative scenarios.",
            "action": "Consider the alternative scenarios below before finalizing."
        }
    else:
        return {
            "level": "Low",
            "description": "Rankings are highly sensitive to weight changes. Decision requires careful consideration of priorities.",
            "action": "Spend more time clarifying your true priorities before deciding."
        }