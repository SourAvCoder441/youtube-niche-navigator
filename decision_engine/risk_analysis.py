def calculate_risk(niche_attributes):
    competition = niche_attributes["competition"]
    investment = niche_attributes["investment"]
    skill = niche_attributes["skill"]

    risk_score = (
        0.4 * competition +
        0.3 * investment +
        0.3 * (10 - skill)
    )

    risk_score = round(risk_score, 2)

    if risk_score >= 7:
        risk_level = "High"
    elif risk_score >= 4:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    return risk_score, risk_level