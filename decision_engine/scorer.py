"""
Scoring engine for multi-criteria decision analysis.
Implements weighted scoring with min-max normalization.
"""

from decision_engine.criteria import CRITERIA


def normalize_value(value, min_value, max_value, goal_type):
    """
    Normalize value to 0-1 scale based on goal type.
    
    Args:
        value: Raw score (1-10)
        min_value: Minimum across all options
        max_value: Maximum across all options  
        goal_type: 'maximize' or 'minimize'
    
    Returns:
        Normalized value between 0 and 1
    """
    if max_value == min_value:
        return 0.5  # Neutral if all values identical

    if goal_type == "maximize":
        return (value - min_value) / (max_value - min_value)
    else:
        return (max_value - value) / (max_value - min_value)


def calculate_scores(niches, weights):
    """
    Calculate weighted scores for all niches.
    
    Args:
        niches: Dict with structure {name: {attributes: {...}, metadata: {...}}}
        weights: Dict of criterion weights (sum to 1)
    
    Returns:
        Dict with scores and contribution breakdowns
    """
    results = {}

    # Determine min and max for normalization from attributes
    min_max = {}
    for criterion in CRITERIA:
        values = [niches[n]["attributes"][criterion] for n in niches]
        min_max[criterion] = (min(values), max(values))

    for niche_name, data in niches.items():
        attributes = data["attributes"]
        total_score = 0
        contribution_breakdown = {}

        for criterion, goal_type in CRITERIA.items():
            min_val, max_val = min_max[criterion]

            normalized = normalize_value(
                attributes[criterion],
                min_val,
                max_val,
                goal_type
            )

            contribution = normalized * weights[criterion]
            contribution_breakdown[criterion] = round(contribution, 4)

            total_score += contribution

        results[niche_name] = {
            "final_score": round(total_score, 4),
            "contributions": contribution_breakdown,
            "attributes": attributes  # Include for explanation generation
        }

    return results


def rank_niches(results):
    """
    Sort niches by final score descending.
    
    Args:
        results: Output from calculate_scores
    
    Returns:
        List of tuples: [(niche_name, data), ...] sorted by score
    """
    return sorted(
        results.items(),
        key=lambda x: x[1]["final_score"],
        reverse=True
    )