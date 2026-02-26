def clamp_weights(weights):
    for key in weights:
        if weights[key] < 1:
            weights[key] = 1
        elif weights[key] > 10:
            weights[key] = 10
    return weights


def normalize_weights(weights):
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


def adjust_weights(base_weights, goal):
    weights = base_weights.copy()

    if goal == "side_income":
        weights["monetization"] += 2
        weights["growth"] += 1

    elif goal == "long_term":
        weights["growth"] += 2
        weights["skill"] += 1
        weights["monetization"] -= 1

    elif goal == "passion":
        weights["skill"] += 2
        weights["time"] += 1
        weights["monetization"] -= 2

    weights = clamp_weights(weights)
    weights = normalize_weights(weights)

    return weights