from decision_engine.criteria import CRITERIA


def normalize_value(value, min_value, max_value, goal_type):
    if max_value == min_value:
        return 0

    if goal_type == "maximize":
        return (value - min_value) / (max_value - min_value)
    else:  # minimize
        return (max_value - value) / (max_value - min_value)


def calculate_scores(niches, weights):
    scores = {}

    # For normalization, find min and max for each criterion
    min_max = {}

    for criterion in CRITERIA:
        values = [niches[n][criterion] for n in niches]
        min_max[criterion] = (min(values), max(values))

    for niche_name, attributes in niches.items():
        total_score = 0
        for criterion, goal_type in CRITERIA.items():
            min_val, max_val = min_max[criterion]
            normalized = normalize_value(
                attributes[criterion],
                min_val,
                max_val,
                goal_type
            )
            total_score += normalized * weights[criterion]

        scores[niche_name] = round(total_score, 4)

    return scores