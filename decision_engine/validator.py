"""
Input validation module for decision engine.
Ensures data integrity before processing.
"""

from decision_engine.criteria import CRITERIA

REQUIRED_CRITERIA = set(CRITERIA.keys())
VALID_GOALS = {"side_income", "long_term", "passion", None}


class ValidationError(Exception):
    """Custom exception for validation failures."""


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_weights(weights):
    if not isinstance(weights, dict):
        raise ValidationError("Weights must be provided as a dictionary")

    missing = REQUIRED_CRITERIA - set(weights.keys())
    if missing:
        raise ValidationError(f"Missing required criteria: {sorted(missing)}")

    extra = set(weights.keys()) - REQUIRED_CRITERIA
    if extra:
        raise ValidationError(f"Unknown criteria provided: {sorted(extra)}")

    for criterion, value in weights.items():
        if not _is_number(value):
            raise ValidationError(f"Weight for '{criterion}' must be numeric")
        if not 1 <= float(value) <= 10:
            raise ValidationError(f"Weight for '{criterion}' must be between 1 and 10, got {value}")
    return True


def validate_goal(goal):
    if goal not in VALID_GOALS:
        raise ValidationError(f"Invalid goal '{goal}'. Must be one of: {sorted(g for g in VALID_GOALS if g)} or None")
    return True


def validate_niche_attributes(niche_name, attrs):
    if not isinstance(attrs, dict):
        raise ValidationError(f"Niche '{niche_name}' attributes must be a dictionary")

    missing = REQUIRED_CRITERIA - set(attrs.keys())
    if missing:
        raise ValidationError(f"Niche '{niche_name}' missing attributes: {sorted(missing)}")

    extra = set(attrs.keys()) - REQUIRED_CRITERIA
    if extra:
        raise ValidationError(f"Niche '{niche_name}' has unknown attributes: {sorted(extra)}")

    cleaned = {}
    for criterion in REQUIRED_CRITERIA:
        value = attrs.get(criterion)
        if value is None:
            raise ValidationError(f"Niche '{niche_name}' attribute '{criterion}' is missing")
        if not _is_number(value):
            raise ValidationError(f"Niche '{niche_name}' attribute '{criterion}' must be numeric")
        num = float(value)
        if not 1 <= num <= 10:
            raise ValidationError(
                f"Niche '{niche_name}' attribute '{criterion}' must be between 1 and 10, got {value}"
            )
        cleaned[criterion] = num
    return cleaned


def validate_niche_data(niches):
    if not niches or not isinstance(niches, dict):
        raise ValidationError("At least one niche must be provided")

    for niche_name, data in niches.items():
        if not isinstance(data, dict):
            raise ValidationError(f"Niche '{niche_name}' data must be a dictionary")
        if "attributes" not in data:
            raise ValidationError(f"Niche '{niche_name}' missing 'attributes' key")
        data["attributes"] = validate_niche_attributes(niche_name, data["attributes"])
    return True
