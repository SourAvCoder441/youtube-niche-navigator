"""
Explanation generation module for decision transparency.
Generates human-readable justifications with comparison context.
"""

from decision_engine.criteria import CRITERIA


def calculate_percentile(criterion, value, all_niche_data):
    """
    Calculate percentile rank of this value compared to all other niches.
    Safely accesses only the 'attributes' sub-dictionary.
    """
    if not all_niche_data:
        return 50.0

    values = []
    for niche_info in all_niche_data.values():
        # Only look at 'attributes' — ignore 'score', 'domain_match_boost', etc.
        attrs = niche_info.get("attributes", {})
        if criterion in attrs:
            values.append(attrs[criterion])

    if not values:
        return 50.0

    # Sort ascending
    sorted_values = sorted(values)

    # Number of values strictly less than ours
    lt_count = sum(1 for v in sorted_values if v < value)
    # Number of values equal to ours
    eq_count = sum(1 for v in sorted_values if v == value)

    # Rank = number below + half of ties
    rank = lt_count + (eq_count / 2)
    percentile = (rank / len(sorted_values)) * 100

    return round(percentile, 1)


def get_criterion_label(criterion):
    labels = {
        "skill": "Skill Alignment",
        "time": "Time Efficiency",
        "monetization": "Monetization Potential",
        "competition": "Competition Level",
        "growth": "Growth Potential",
        "investment": "Investment Required"
    }
    return labels.get(criterion, criterion.replace("_", " ").title())


def generate_summary(niche_name, rank, top_contributors, attributes):
    if not top_contributors:
        return f"{niche_name} ranks #{rank} with balanced performance across all criteria."
    
    top_crits = ", ".join(get_criterion_label(c[0]) for c in top_contributors)
    return f"{niche_name} ranks #{rank}, strongest in {top_crits}."


def generate_comparisons(niche_name, attributes, all_niche_data, runner_up, top_positive):
    comparisons = []

    if not runner_up:
        return comparisons

    runner_name, runner_data = runner_up
    runner_attrs = runner_data.get("attributes", {})

    # Direct head-to-head vs runner-up
    for crit, goal_type in CRITERIA.items():
        my_val = attributes.get(crit, 0)
        their_val = runner_attrs.get(crit, 0)

        diff = my_val - their_val
        if goal_type == "maximize" and diff > 1.5:
            comparisons.append({
                "criterion": crit,
                "message": f"Strong advantage in {get_criterion_label(crit)} ({my_val} vs {their_val})"
            })
        elif goal_type == "minimize" and diff < -1.5:
            comparisons.append({
                "criterion": crit,
                "message": f"Lower {get_criterion_label(crit)} requirement ({my_val} vs {their_val})"
            })

    # Percentile context for top strengths
    for crit, contrib in top_positive:
        if contrib > 0.08:
            perc = calculate_percentile(crit, attributes.get(crit, 0), all_niche_data)
            comparisons.append({
                "criterion": crit,
                "message": f"Top {perc}% in {get_criterion_label(crit)} among all niches"
            })

    return comparisons[:4]  # keep the most meaningful ones


def get_strength_context(criterion, value):
    contexts = {
        "skill": {
            "high": "Strong existing expertise — quick path to quality content",
            "medium": "Solid foundation, some learning still needed",
            "low": "Requires significant upskilling or outsourcing"
        },
        "time": {
            "high": "Very time-efficient — fits busy schedules well",
            "medium": "Moderate time commitment",
            "low": "Time-intensive format"
        },
        "monetization": {
            "high": "High revenue potential (strong CPM or affiliate opportunities)",
            "medium": "Solid monetization path",
            "low": "Longer ramp-up or lower ceiling"
        },
        "competition": {
            "high": "Crowded space — needs strong differentiation",
            "medium": "Moderate competition",
            "low": "Easier to stand out"
        },
        "growth": {
            "high": "Strong tailwinds — fast audience potential",
            "medium": "Steady, consistent growth",
            "low": "Mature / saturated market"
        },
        "investment": {
            "high": "Professional setup possible → premium quality",
            "medium": "Balanced equipment needs",
            "low": "Start with phone/laptop — very low barrier"
        }
    }
    level = "high" if value >= 7 else "medium" if value >= 4 else "low"
    return contexts.get(criterion, {}).get(level, "")


def get_concern_context(criterion, value):
    concerns = {
        "skill": "May require significant upskilling or outsourcing",
        "time": "Risk of burnout or inconsistent posting schedule",
        "monetization": "Longer path to revenue or lower income ceiling",
        "competition": "Harder to stand out without unique positioning",
        "growth": "Slower audience building, requires patience",
        "investment": "Quality limitations may affect competitiveness"
    }
    return concerns.get(criterion, "Area requiring attention")


def identify_risk_factors(attributes):
    factors = []
    if attributes.get("competition", 0) >= 8:
        factors.append("High competition saturation")
    if attributes.get("investment", 0) >= 7:
        factors.append("Significant upfront investment required")
    if attributes.get("skill", 0) <= 4:
        factors.append("Steep learning curve for required skills")
    if attributes.get("time", 0) >= 8:
        factors.append("High time commitment increases burnout risk")
    return factors if factors else ["Balanced risk profile"]


def generate_mitigation_advice(risk_level, attributes):
    if risk_level == "High":
        advice = ["Consider sub-niche specialization to reduce competition exposure"]
        if attributes.get("investment", 0) >= 7:
            advice.append("Phase equipment purchases to spread costs")
        if attributes.get("skill", 0) <= 4:
            advice.append("Invest 3-6 months in skill building before launch")
        return advice
    elif risk_level == "Moderate":
        return ["Monitor key metrics monthly", "Maintain emergency content buffer"]
    else:
        return ["Focus on consistency to capitalize on favorable conditions"]


def generate_final_recommendation(niche_name, rank, risk_level, strength_count, concern_count, runner_up):
    runner_text = f" over {runner_up[0]}" if runner_up and rank == 1 else ""
    
    if rank == 1:
        if risk_level == "Low" and strength_count >= 2:
            return f"Strong candidate{runner_text}: Clear alignment with your priorities and favorable risk profile. Proceed with confidence."
        elif risk_level == "High" and strength_count >= 2:
            return f"Viable but challenging{runner_text}: Rewards execution excellence. Address identified concerns proactively."
        elif concern_count == 0:
            return f"Solid option{runner_text}: Consistent performance with no major red flags."
        else:
            return f"Conditional fit{runner_text}: Works if you can mitigate the identified concern areas."
    else:
        if risk_level == "Low":
            return f"Strong alternative: Consider if priorities shift toward {strength_count} identified strengths."
        else:
            return f"Alternative option: Viable if top recommendation constraints don't fit your situation."


def generate_explanation(niche_name, attributes, contributions, risk_score, risk_level, 
                         weights, all_niche_data, ranked_list):
    """
    Main explanation generator.
    """
    # Find this niche's rank (1-based)
    rank = next((i + 1 for i, (name, _) in enumerate(ranked_list) if name == niche_name), 1)
    
    # Sort contributions by impact (descending)
    sorted_contrib = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    top_positive = [c for c in sorted_contrib if c[1] > 0.08][:2]
    bottom = sorted_contrib[-1] if sorted_contrib else (None, 0)
    
    # Runner-up logic
    runner_up = None
    if len(ranked_list) > 1:
        if rank == 1 and len(ranked_list) > 1:
            runner_up = ranked_list[1]
        elif rank > 1:
            runner_up = ranked_list[0]

    explanation = {
        "rank": rank,
        "summary": generate_summary(niche_name, rank, top_positive, attributes),
        "strengths": [],
        "concerns": [],
        "comparisons": generate_comparisons(niche_name, attributes, all_niche_data, runner_up, top_positive),
        "risk_assessment": {},
        "trade_offs": [],
        "recommendation": ""
    }
    
    # Strengths
    for crit, contrib in top_positive:
        explanation["strengths"].append({
            "criterion": crit,
            "criterion_label": get_criterion_label(crit),
            "contribution": round(contrib, 3),
            "raw_score": attributes.get(crit, 0),
            "percentile": calculate_percentile(crit, attributes.get(crit, 0), all_niche_data),
            "context": get_strength_context(crit, attributes.get(crit, 0))
        })
    
    # Concerns (only if weakest is really weak)
    if bottom[1] < 0.06 and bottom[0]:
        crit = bottom[0]
        explanation["concerns"].append({
            "criterion": crit,
            "criterion_label": get_criterion_label(crit),
            "raw_score": attributes.get(crit, 0),
            "percentile": calculate_percentile(crit, attributes.get(crit, 0), all_niche_data),
            "context": get_concern_context(crit, attributes.get(crit, 0))
        })
    
    # Risk block
    explanation["risk_assessment"] = {
        "level": risk_level,
        "score": risk_score,
        "factors": identify_risk_factors(attributes),
        "mitigation": generate_mitigation_advice(risk_level, attributes)
    }
    
    # Recommendation
    explanation["recommendation"] = generate_final_recommendation(
        niche_name, rank, risk_level,
        len(explanation["strengths"]),
        len(explanation["concerns"]),
        runner_up
    )
    
    return explanation