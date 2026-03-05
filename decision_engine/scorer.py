"""
Scoring engine for multi-criteria decision analysis.
Implements weighted scoring with min-max normalization and optional domain boosts.
"""

from decision_engine.criteria import CRITERIA
from decision_engine.prompt_parser import DOMAIN_TO_NICHE


def normalize_value(value, min_value, max_value, goal_type):
    if max_value == min_value:
        return 0.5

    if goal_type == "maximize":
        return (value - min_value) / (max_value - min_value)
    return (max_value - value) / (max_value - min_value)


def get_alt_niche_for_preferred(preferred_niche):
    """Return alternate niche only for preferred niche's domain mapping."""
    if not preferred_niche:
        return None

    for domain_info in DOMAIN_TO_NICHE.values():
        if domain_info.get("niche") == preferred_niche:
            return domain_info.get("alt")
    return None


def calculate_scores(
    niches,
    weights,
    preferred_niche=None,
    domain_boost=0.50,
    alt_domain_boost=0.18,
):
    """
    Calculate weighted scores for all niches.

    Optional deterministic boosts:
    - primary boost: preferred niche
    - secondary boost: alternate niche in same domain as preferred niche
    """
    results = {}
    alt_niche = get_alt_niche_for_preferred(preferred_niche)

    min_max = {}
    for criterion in CRITERIA:
        values = [niches[n]["attributes"][criterion] for n in niches]
        min_max[criterion] = (min(values), max(values))

    for niche_name, data in niches.items():
        attributes = data["attributes"]
        total_score = 0.0
        contribution_breakdown = {}

        for criterion, goal_type in CRITERIA.items():
            min_val, max_val = min_max[criterion]
            normalized = normalize_value(attributes[criterion], min_val, max_val, goal_type)
            contribution = normalized * weights[criterion]
            contribution_breakdown[criterion] = round(contribution, 4)
            total_score += contribution

        boost_applied = False
        boost_amount = 0.0
        if preferred_niche and niche_name == preferred_niche:
            boost_amount = total_score * domain_boost
            total_score += boost_amount
            contribution_breakdown["domain_match_boost"] = round(boost_amount, 4)
            boost_applied = True

        alt_boost_applied = False
        alt_boost_amount = 0.0
        if alt_niche and niche_name == alt_niche:
            alt_boost_amount = total_score * alt_domain_boost
            total_score += alt_boost_amount
            contribution_breakdown["alt_domain_boost"] = round(alt_boost_amount, 4)
            alt_boost_applied = True

        results[niche_name] = {
            "final_score": round(total_score, 4),
            "contributions": contribution_breakdown,
            "attributes": attributes,
            "domain_boost_applied": boost_applied,
            "alt_boost_applied": alt_boost_applied,
        }

    return results


def rank_niches(results):
    return sorted(results.items(), key=lambda x: x[1]["final_score"], reverse=True)
