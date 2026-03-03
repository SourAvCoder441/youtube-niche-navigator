"""
Scoring engine for multi-criteria decision analysis.
Implements weighted scoring with min-max normalization and domain preference boost.
"""

from decision_engine.criteria import CRITERIA
from decision_engine.prompt_parser import DOMAIN_TO_NICHE   # NEW import


def normalize_value(value, min_value, max_value, goal_type):
    if max_value == min_value:
        return 0.5

    if goal_type == "maximize":
        return (value - min_value) / (max_value - min_value)
    else:
        return (max_value - value) / (max_value - min_value)


def calculate_scores(niches, weights, preferred_niche=None, domain_boost=0.50):
    """
    Calculate weighted scores for all niches with domain + alt-niche boost.
    """
    results = {}

    # Determine min/max for normalization
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

        # Primary profession boost
        boost_applied = False
        boost_amount = 0
        if preferred_niche and niche_name == preferred_niche:
            boost_amount = total_score * domain_boost
            total_score += boost_amount
            contribution_breakdown["domain_match_boost"] = round(boost_amount, 4)
            boost_applied = True

        # NEW: Secondary boost for the "alt" niche in the same domain (e.g. AI when primary is Coding)
        alt_boost_applied = False
        alt_boost_amount = 0
        # We would need domain here — but since we don't pass domain, we check if this niche is someone's alt
        for dom, info in DOMAIN_TO_NICHE.items():
            if info.get("alt") == niche_name:
                alt_boost_amount = total_score * 0.18  # 18% secondary boost
                total_score += alt_boost_amount
                contribution_breakdown["alt_domain_boost"] = round(alt_boost_amount, 4)
                alt_boost_applied = True
                break

        results[niche_name] = {
            "final_score": round(total_score, 4),
            "contributions": contribution_breakdown,
            "attributes": attributes,
            "domain_boost_applied": boost_applied,
            "alt_boost_applied": alt_boost_applied
        }

    return results


def rank_niches(results):
    return sorted(
        results.items(),
        key=lambda x: x[1]["final_score"],
        reverse=True
    )