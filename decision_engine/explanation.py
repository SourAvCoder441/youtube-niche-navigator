"""
Explanation generation module for decision transparency.
Generates human-readable justifications with comparison context.
"""

from decision_engine.criteria import CRITERIA


def generate_explanation(niche_name, attributes, contributions, risk_score, risk_level, 
                        weights, all_niche_data, ranked_list):
    """
    Generate comprehensive explanation with comparison context.
    
    Args:
        niche_name: Name of the niche
        attributes: Dict of criterion scores
        contributions: Dict of weighted contributions
        risk_score: Calculated risk score (0-10)
        risk_level: 'High', 'Moderate', or 'Low'
        weights: Final adjusted weights used
        all_niche_data: Dict of all niches with scores and attributes
        ranked_list: List of (name, data) tuples sorted by rank
    
    Returns:
        Dict with structured explanation including comparisons
    """
    # Determine rank
    rank = next(i for i, (name, _) in enumerate(ranked_list) if name == niche_name) + 1
    
    # Sort contributions by impact
    sorted_contributions = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    top_positive = [c for c in sorted_contributions if c[1] > 0.08][:2]
    bottom_contributor = sorted_contributions[-1]
    
    # Get runner-up for comparison (#2 if we're #1, #1 if we're #2+)
    runner_up = ranked_list[0] if rank > 1 else (ranked_list[1] if len(ranked_list) > 1 else None)
    
    explanation = {
        "rank": rank,
        "summary": generate_summary(niche_name, rank, top_positive, attributes),
        "strengths": [],
        "concerns": [],
        "comparisons": generate_comparisons(niche_name, attributes, all_niche_data, runner_up, top_positive),
        "risk_assessment": {},
        "trade_offs": generate_trade_offs(niche_name, attributes, all_niche_data, ranked_list[0][0]),
        "recommendation": ""
    }
    
    # Build strengths
    for criterion, contribution in top_positive:
        explanation["strengths"].append({
            "criterion": criterion,
            "criterion_label": get_criterion_label(criterion),
            "contribution": round(contribution, 3),
            "raw_score": attributes[criterion],
            "percentile": calculate_percentile(criterion, attributes[criterion], all_niche_data),
            "context": get_strength_context(criterion, attributes[criterion])
        })
    
    # Build concerns
    if bottom_contributor[1] < 0.06:
        explanation["concerns"].append({
            "criterion": bottom_contributor[0],
            "criterion_label": get_criterion_label(bottom_contributor[0]),
            "raw_score": attributes[bottom_contributor[0]],
            "percentile": calculate_percentile(bottom_contributor[0], attributes[bottom_contributor[0]], all_niche_data),
            "context": get_concern_context(bottom_contributor[0], attributes[bottom_contributor[0]])
        })
    
    # Risk assessment
    explanation["risk_assessment"] = {
        "level": risk_level,
        "score": risk_score,
        "factors": identify_risk_factors(attributes),
        "mitigation": generate_mitigation_advice(risk_level, attributes)
    }
    
    # Trade-offs and final recommendation
    explanation["recommendation"] = generate_final_recommendation(
        niche_name, rank, risk_level, len(explanation["strengths"]), 
        len(explanation["concerns"]), runner_up
    )
    
    return explanation


def generate_summary(niche_name, rank, top_contributors, attributes):
    """Generate one-line summary with rank context."""
    if not top_contributors:
        return f"{niche_name} ranks #{rank} with balanced performance across all criteria."
    
    primary = top_contributors[0]
    criterion = primary[0]
    
    rank_suffix = {1: "st", 2: "nd", 3: "rd"}.get(rank, "th")
    
    summaries = {
        "skill": f"{niche_name} ranks #{rank}{rank_suffix} by leveraging your expertise in a high-skill domain.",
        "time": f"{niche_name} ranks #{rank}{rank_suffix} due to strong alignment with your available time.",
        "monetization": f"{niche_name} ranks #{rank}{rank_suffix} with exceptional revenue potential.",
        "competition": f"{niche_name} ranks #{rank}{rank_suffix} by operating in a less saturated market segment.",
        "growth": f"{niche_name} ranks #{rank}{rank_suffix} by riding strong market growth trends.",
        "investment": f"{niche_name} ranks #{rank}{rank_suffix} with minimal financial barrier to entry."
    }
    
    return summaries.get(criterion, f"{niche_name} ranks #{rank}{rank_suffix} with strong {get_criterion_label(criterion)}.")


def generate_comparisons(niche_name, attributes, all_niche_data, runner_up, top_contributors):
    """Generate specific comparisons to other niches."""
    comparisons = []
    
    # Compare to category average
    for criterion, contribution in top_contributors[:2]:
        scores = [data["attributes"][criterion] for data in all_niche_data.values()]
        avg_score = sum(scores) / len(scores)
        user_score = attributes[criterion]
        
        if user_score > avg_score:
            diff = ((user_score - avg_score) / avg_score) * 100
            comparisons.append({
                "type": "category_average",
                "criterion": criterion,
                "message": f"Scores {user_score}/10, {diff:.0f}% above category average ({avg_score:.1f})",
                "advantage": True
            })
    
    # Compare to runner-up if available
    if runner_up:
        runner_name, runner_data = runner_up
        runner_attrs = runner_data["attributes"]
        
        # Find where we win
        winning_criteria = []
        for criterion in attributes:
            if attributes[criterion] > runner_attrs[criterion]:
                winning_criteria.append((criterion, attributes[criterion] - runner_attrs[criterion]))
        
        if winning_criteria:
            best_win = max(winning_criteria, key=lambda x: x[1])
            comparisons.append({
                "type": "runner_up",
                "vs": runner_name,
                "criterion": best_win[0],
                "message": f"Wins on {get_criterion_label(best_win[0])} by {best_win[1]} points vs {runner_name}",
                "advantage": True
            })
        
        # Find where we lose (if close race)
        losing_criteria = []
        for criterion in attributes:
            if attributes[criterion] < runner_attrs[criterion]:
                losing_criteria.append((criterion, runner_attrs[criterion] - attributes[criterion]))
        
        if losing_criteria and len(comparisons) < 3:
            worst_loss = max(losing_criteria, key=lambda x: x[1])
            comparisons.append({
                "type": "trade_off",
                "vs": runner_name,
                "criterion": worst_loss[0],
                "message": f"Trade-off: {runner_name} leads on {get_criterion_label(worst_loss[0])} by {worst_loss[1]} points",
                "advantage": False
            })
    
    return comparisons


def generate_trade_offs(niche_name, attributes, all_niche_data, winner_name):
    """Identify explicit trade-offs vs the winner."""
    if niche_name == winner_name:
        return {"is_winner": True, "message": "Top recommendation based on your priorities."}
    
    winner_attrs = all_niche_data[winner_name]["attributes"]
    
    trade_offs = []
    for criterion in attributes:
        diff = attributes[criterion] - winner_attrs[criterion]
        if diff >= 2:  # We win significantly here
            trade_offs.append({
                "criterion": criterion,
                "advantage": "yours",
                "magnitude": diff
            })
        elif diff <= -2:  # They win significantly
            trade_offs.append({
                "criterion": criterion,
                "advantage": "winner",
                "magnitude": abs(diff)
            })
    
    if not trade_offs:
        return {
            "is_winner": False,
            "message": f"Close competition with {winner_name}. Small priority shifts could change ranking.",
            "swap_potential": True
        }
    
    your_wins = [t for t in trade_offs if t["advantage"] == "yours"]
    their_wins = [t for t in trade_offs if t["advantage"] == "winner"]
    
    return {
        "is_winner": False,
        "message": f" vs {winner_name}: You win on {len(your_wins)} criteria, they win on {len(their_wins)}.",
        "your_advantages": [get_criterion_label(t["criterion"]) for t in your_wins],
        "their_advantages": [get_criterion_label(t["criterion"]) for t in their_wins],
        "swap_potential": len(your_wins) > len(their_wins)
    }


def calculate_percentile(criterion, value, all_niche_data):
    """Calculate percentile rank within all niches."""
    scores = [data["attributes"][criterion] for data in all_niche_data.values()]
    below = sum(1 for s in scores if s < value)
    return int((below / len(scores)) * 100)


def get_criterion_label(criterion):
    """Return human-readable label."""
    labels = {
        "skill": "Skill Alignment",
        "time": "Time Compatibility", 
        "monetization": "Monetization Potential",
        "competition": "Competition Level",
        "growth": "Growth Potential",
        "investment": "Initial Investment"
    }
    return labels.get(criterion, criterion)


def get_strength_context(criterion, value):
    """Contextual description for high-performing criterion."""
    contexts = {
        "skill": {
            "high": "Your expertise creates natural content authority and reduces research time",
            "medium": "Your skills provide solid foundation with room to grow",
            "low": "Lower barrier allows focus on other differentiators"
        },
        "time": {
            "high": "Substantial time enables consistent, high-quality production",
            "medium": "Moderate commitment balances quality with sustainability",
            "low": "Efficient formats possible with limited availability"
        },
        "monetization": {
            "high": "Multiple revenue streams: ads, sponsorships, courses, consulting",
            "medium": "Standard monetization through ads and select partnerships",
            "low": "Requires creative monetization or passion-driven approach"
        },
        "competition": {
            "high": "Differentiation critical in crowded space",
            "medium": "Balanced competition allows niche positioning",
            "low": "First-mover advantage possible in emerging space"
        },
        "growth": {
            "high": "Riding strong market tailwinds and rising demand",
            "medium": "Steady growth with established audience",
            "low": "Mature market requires unique angle for growth"
        },
        "investment": {
            "high": "Professional equipment enables premium content quality",
            "medium": "Moderate setup costs for decent production value",
            "low": "Minimal barrier to entry, start with basic tools"
        }
    }
    
    level = "high" if value >= 7 else "medium" if value >= 4 else "low"
    return contexts.get(criterion, {}).get(level, "")


def get_concern_context(criterion, value):
    """Contextual description for low-performing criterion."""
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
    """Identify specific attributes contributing to risk."""
    factors = []
    
    if attributes["competition"] >= 8:
        factors.append("High competition saturation")
    if attributes["investment"] >= 7:
        factors.append("Significant upfront investment required")
    if attributes["skill"] <= 4:
        factors.append("Steep learning curve for required skills")
    if attributes["time"] >= 8:
        factors.append("High time commitment increases burnout risk")
        
    return factors if factors else ["Balanced risk profile"]


def generate_mitigation_advice(risk_level, attributes):
    """Generate specific advice based on risk factors."""
    if risk_level == "High":
        advice = ["Consider sub-niche specialization to reduce competition exposure"]
        if attributes["investment"] >= 7:
            advice.append("Phase equipment purchases to spread costs")
        if attributes["skill"] <= 4:
            advice.append("Invest 3-6 months in skill building before launch")
        return advice
    elif risk_level == "Moderate":
        return ["Monitor key metrics monthly", "Maintain emergency content buffer"]
    else:
        return ["Focus on consistency to capitalize on favorable conditions"]


def generate_final_recommendation(niche_name, rank, risk_level, strength_count, concern_count, runner_up):
    """Generate actionable final recommendation with context."""
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