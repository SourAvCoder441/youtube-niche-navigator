"""
Explanation generation module for decision transparency.
Generates human-readable justifications for recommendations.
"""

from decision_engine.criteria import CRITERIA


def generate_explanation(niche_name, attributes, contributions, risk_score, risk_level, weights):
    """
    Generate comprehensive explanation for a niche ranking.
    
    Args:
        niche_name: Name of the niche
        attributes: Dict of criterion scores
        contributions: Dict of weighted contributions to final score
        risk_score: Calculated risk score (0-10)
        risk_level: 'High', 'Moderate', or 'Low'
        weights: Final adjusted weights used
    
    Returns:
        Dict with structured explanation components
    """
    # Sort contributions by impact
    sorted_contributions = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    top_positive = [c for c in sorted_contributions if c[1] > 0.1][:2]  # Top 2 meaningful contributors
    bottom_contributor = sorted_contributions[-1]
    
    explanation = {
        "summary": generate_summary(niche_name, top_positive, attributes),
        "strengths": [],
        "concerns": [],
        "risk_assessment": {},
        "recommendation": ""
    }
    
    # Build strengths list
    for criterion, contribution in top_positive:
        explanation["strengths"].append({
            "criterion": criterion,
            "criterion_label": get_criterion_label(criterion),
            "contribution": round(contribution, 3),
            "raw_score": attributes[criterion],
            "context": get_strength_context(criterion, attributes[criterion])
        })
    
    # Build concerns (only if contribution is low)
    if bottom_contributor[1] < 0.08:
        explanation["concerns"].append({
            "criterion": bottom_contributor[0],
            "criterion_label": get_criterion_label(bottom_contributor[0]),
            "raw_score": attributes[bottom_contributor[0]],
            "context": get_concern_context(bottom_contributor[0], attributes[bottom_contributor[0]])
        })
    
    # Risk assessment
    explanation["risk_assessment"] = {
        "level": risk_level,
        "score": risk_score,
        "factors": identify_risk_factors(attributes),
        "mitigation": generate_mitigation_advice(risk_level, attributes)
    }
    
    # Final recommendation
    explanation["recommendation"] = generate_final_recommendation(
        niche_name, risk_level, len(explanation["strengths"]), len(explanation["concerns"])
    )
    
    return explanation


def generate_summary(niche_name, top_contributors, attributes):
    """Generate one-line summary of why this niche ranked."""
    if not top_contributors:
        return f"{niche_name} shows balanced performance across criteria."
    
    primary = top_contributors[0]
    criterion = primary[0]
    label = get_criterion_label(criterion)
    
    summaries = {
        "skill": f"{niche_name} leverages your existing expertise effectively.",
        "time": f"{niche_name} fits well with your available time commitment.",
        "monetization": f"{niche_name} offers strong revenue potential.",
        "competition": f"{niche_name} operates in a less saturated market segment.",
        "growth": f"{niche_name} aligns with current market growth trends.",
        "investment": f"{niche_name} requires minimal upfront financial commitment."
    }
    
    return summaries.get(criterion, f"{niche_name} performs strongly in {label}.")


def get_criterion_label(criterion):
    """Return human-readable label for criterion."""
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


def generate_final_recommendation(niche_name, risk_level, strength_count, concern_count):
    """Generate actionable final recommendation."""
    if risk_level == "Low" and strength_count >= 2:
        return f"Strong candidate: {niche_name} offers favorable risk/reward balance with clear alignment to your priorities."
    elif risk_level == "High" and strength_count >= 2:
        return f"Viable but challenging: {niche_name} rewards execution excellence. Success requires addressing identified concerns proactively."
    elif concern_count == 0:
        return f"Solid option: {niche_name} shows consistent performance with no major red flags."
    else:
        return f"Conditional fit: {niche_name} works if you can mitigate the identified concern areas."