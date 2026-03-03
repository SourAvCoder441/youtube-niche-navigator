def clamp_weights(weights):
    for key in weights:
        if weights[key] < 1:
            weights[key] = 1
        elif weights[key] > 10:
            weights[key] = 10
    return weights


def normalize_weights(weights):
    total = sum(weights.values())
    if total == 0:
        total = 1.0  # avoid division by zero (shouldn't happen)
    return {k: v / total for k, v in weights.items()}


def adjust_weights(base_weights, goal):
    weights = base_weights.copy()

    if goal == "side_income":
        # Strong focus on quick money + low barrier
        weights["monetization"] += 3      # was +4 → slightly less extreme
        weights["growth"] += 2
        weights["competition"] += 5       # NEW: strong penalty for saturated niches
        weights["investment"] += 3        # extra emphasis on truly low entry cost
        weights["skill"] -= 1             # side income shouldn't demand genius-level skill

    elif goal == "long_term":
        weights["growth"] += 4
        weights["skill"] += 3
        weights["monetization"] -= 2
        weights["competition"] += 2       # long-term → can survive some competition

    elif goal == "passion":
        weights["skill"] += 4
        weights["time"] += 3
        weights["monetization"] -= 3
        weights["competition"] -= 1       # passion → competition matters less

    weights = clamp_weights(weights)
    weights = normalize_weights(weights)

    return weights