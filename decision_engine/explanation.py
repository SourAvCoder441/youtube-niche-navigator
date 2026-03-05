"""
Explanation generation module for decision transparency.
"""

from decision_engine.criteria import CRITERIA


def calculate_percentile(criterion, value, all_niche_data):
    if not all_niche_data:
        return 50.0

    values = []
    for niche_info in all_niche_data.values():
        attrs = niche_info.get("attributes", {})
        if criterion in attrs:
            values.append(attrs[criterion])

    if not values:
        return 50.0

    sorted_values = sorted(values)
    lt_count = sum(1 for v in sorted_values if v < value)
    eq_count = sum(1 for v in sorted_values if v == value)
    rank = lt_count + (eq_count / 2.0)
    return round((rank / len(sorted_values)) * 100, 1)


def get_criterion_label(criterion):
    labels = {
        "skill": "Skill Alignment",
        "time": "Time Efficiency",
        "monetization": "Monetization Potential",
        "competition": "Competition Level",
        "growth": "Growth Potential",
        "investment": "Investment Required",
    }
    return labels.get(criterion, criterion.replace("_", " ").title())


def generate_summary(niche_name, rank, top_contributors):
    if not top_contributors:
        return f"{niche_name} ranks #{rank} with balanced performance across criteria."
    top_crits = ", ".join(get_criterion_label(c[0]) for c in top_contributors[:2])
    return f"{niche_name} ranks #{rank}, strongest in {top_crits}."


def get_strength_context(criterion, value):
    contexts = {
        "skill": {
            "high": "Strong existing expertise supports faster content quality.",
            "medium": "Usable base skill with room to improve.",
            "low": "May require upskilling before consistency.",
        },
        "time": {
            "high": "Format fits limited weekly time better.",
            "medium": "Moderate production effort.",
            "low": "Can be time intensive to sustain.",
        },
        "monetization": {
            "high": "Higher monetization ceiling.",
            "medium": "Reasonable path to revenue.",
            "low": "Slower or lower revenue profile.",
        },
        "competition": {
            "high": "Crowded category requiring differentiation.",
            "medium": "Manageable competition level.",
            "low": "Lower saturation can help discoverability.",
        },
        "growth": {
            "high": "Stronger audience expansion potential.",
            "medium": "Steady growth profile.",
            "low": "Growth may be slower.",
        },
        "investment": {
            "high": "Higher setup demands.",
            "medium": "Moderate initial setup.",
            "low": "Low barrier to start.",
        },
    }
    level = "high" if value >= 7 else "medium" if value >= 4 else "low"
    return contexts.get(criterion, {}).get(level, "")


def get_concern_context(criterion):
    concerns = {
        "skill": "Skill gap can reduce consistency early on.",
        "time": "Time pressure can cause publishing inconsistency.",
        "monetization": "Revenue ramp can be slower.",
        "competition": "Standing out will be harder without clear positioning.",
        "growth": "Audience growth may require more patience.",
        "investment": "Budget requirements can delay start.",
    }
    return concerns.get(criterion, "This area needs attention.")


def identify_risk_factors(attributes):
    factors = []
    if attributes.get("competition", 0) >= 8:
        factors.append("High competition saturation")
    if attributes.get("investment", 0) >= 7:
        factors.append("High upfront investment")
    if attributes.get("skill", 0) <= 4:
        factors.append("Steep learning curve")
    if attributes.get("time", 0) >= 8:
        factors.append("High time commitment")
    return factors if factors else ["Balanced risk profile"]


def generate_mitigation_advice(risk_level, attributes):
    if risk_level == "High":
        advice = ["Start with a sub-niche to reduce direct competition."]
        if attributes.get("investment", 0) >= 7:
            advice.append("Phase equipment purchases instead of buying all at once.")
        if attributes.get("skill", 0) <= 4:
            advice.append("Run a 6-8 week practice cycle before full launch.")
        return advice
    if risk_level == "Moderate":
        return ["Track monthly metrics and keep a content backlog."]
    return ["Prioritize consistency to exploit favorable conditions."]


def _is_advantage(criterion, mine, theirs):
    goal_type = CRITERIA.get(criterion, "maximize")
    if goal_type == "maximize":
        return mine > theirs
    return mine < theirs


def build_comparisons(attributes, runner_attrs):
    comparisons = []
    for criterion, goal_type in CRITERIA.items():
        my_val = attributes.get(criterion, 0)
        their_val = runner_attrs.get(criterion, 0)
        if goal_type == "maximize":
            delta = my_val - their_val
            if abs(delta) >= 1:
                comparisons.append(
                    {
                        "criterion": criterion,
                        "criterion_label": get_criterion_label(criterion),
                        "message": f"{get_criterion_label(criterion)}: {my_val} vs {their_val}",
                        "delta": round(delta, 2),
                        "advantage": delta > 0,
                    }
                )
        else:
            delta = their_val - my_val
            if abs(delta) >= 1:
                comparisons.append(
                    {
                        "criterion": criterion,
                        "criterion_label": get_criterion_label(criterion),
                        "message": f"{get_criterion_label(criterion)} need: {my_val} vs {their_val}",
                        "delta": round(delta, 2),
                        "advantage": delta > 0,
                    }
                )
    return comparisons[:4]


def build_trade_offs(attributes, winner_attrs, niche_name, winner_name):
    if niche_name == winner_name:
        return {"is_winner": True, "message": "Top-ranked option for current priorities."}

    wins = []
    losses = []
    for criterion in CRITERIA:
        mine = attributes.get(criterion, 0)
        theirs = winner_attrs.get(criterion, 0)
        if _is_advantage(criterion, mine, theirs):
            wins.append(get_criterion_label(criterion))
        elif _is_advantage(criterion, theirs, mine):
            losses.append(get_criterion_label(criterion))

    win_text = ", ".join(wins[:2]) if wins else "few priority criteria"
    loss_text = ", ".join(losses[:2]) if losses else "no major areas"
    return {
        "is_winner": False,
        "message": f"Beats {winner_name} on {win_text}, but trails on {loss_text}.",
    }


def build_why_not_narrative(concerns, winner_name, is_winner):
    if is_winner:
        return "No major blockers under current priorities."
    if not concerns:
        return f"Main reason not ranked #1: {winner_name} has a better weighted balance."
    top_concern = concerns[0]["criterion_label"]
    return f"Main reason not ranked #1: weaker performance in {top_concern} for current weights."


def generate_final_recommendation(rank, risk_level, strength_count, concern_count):
    if rank == 1:
        if risk_level == "Low" and strength_count >= 2:
            return "Strong fit with low execution risk. Recommended as primary choice."
        if risk_level == "High":
            return "High upside but execution-sensitive. Proceed only with mitigation plan."
        return "Best current fit. Validate with a 4-week pilot before full commitment."
    if risk_level == "Low":
        return "Strong backup option if your priorities shift."
    if concern_count == 0:
        return "Viable alternative with balanced trade-offs."
    return "Alternative option, but requires mitigation in weak areas."


def generate_explanation(
    niche_name,
    attributes,
    contributions,
    risk_score,
    risk_level,
    weights,
    all_niche_data,
    ranked_list,
):
    rank = next((i + 1 for i, (name, _) in enumerate(ranked_list) if name == niche_name), 1)
    winner_name = ranked_list[0][0] if ranked_list else niche_name
    winner_attrs = all_niche_data.get(winner_name, {}).get("attributes", {})

    sorted_contrib = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    criterion_contrib = [c for c in sorted_contrib if c[0] in CRITERIA]
    top_positive = [c for c in criterion_contrib[:3] if c[1] > 0]
    weakest = min(criterion_contrib, key=lambda x: x[1]) if criterion_contrib else (None, 0)

    runner_up = None
    if len(ranked_list) > 1:
        runner_up = ranked_list[1] if rank == 1 else ranked_list[0]

    strengths = []
    for crit, contrib in top_positive:
        strengths.append(
            {
                "criterion": crit,
                "criterion_label": get_criterion_label(crit),
                "contribution": round(contrib, 3),
                "raw_score": attributes.get(crit, 0),
                "percentile": calculate_percentile(crit, attributes.get(crit, 0), all_niche_data),
                "context": get_strength_context(crit, attributes.get(crit, 0)),
            }
        )

    concerns = []
    if weakest[0]:
        crit = weakest[0]
        concerns.append(
            {
                "criterion": crit,
                "criterion_label": get_criterion_label(crit),
                "raw_score": attributes.get(crit, 0),
                "percentile": calculate_percentile(crit, attributes.get(crit, 0), all_niche_data),
                "context": get_concern_context(crit),
            }
        )

    runner_attrs = runner_up[1].get("attributes", {}) if runner_up else {}
    comparisons = build_comparisons(attributes, runner_attrs) if runner_up else []
    trade_offs = build_trade_offs(attributes, winner_attrs, niche_name, winner_name)

    explanation = {
        "rank": rank,
        "summary": generate_summary(niche_name, rank, top_positive),
        "strengths": strengths,
        "concerns": concerns,
        "comparisons": comparisons,
        "risk_assessment": {
            "level": risk_level,
            "score": risk_score,
            "factors": identify_risk_factors(attributes),
            "mitigation": generate_mitigation_advice(risk_level, attributes),
        },
        "trade_offs": trade_offs,
        "why_not_top": build_why_not_narrative(concerns, winner_name, rank == 1),
        "recommendation": generate_final_recommendation(
            rank,
            risk_level,
            len(strengths),
            len(concerns),
        ),
    }
    return explanation
