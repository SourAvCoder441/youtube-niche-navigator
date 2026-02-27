"""
Input validation module for decision engine.
Ensures data integrity before processing.
"""


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_weights(weights):
    """
    Validate user-provided weights.
    
    Args:
        weights: Dict of criterion weights
    
    Raises:
        ValidationError: If weights are invalid
    """
    if not isinstance(weights, dict):
        raise ValidationError("Weights must be provided as a dictionary")
    
    required_criteria = {"skill", "time", "monetization", "competition", "growth", "investment"}
    
    # Check all required keys present
    missing = required_criteria - set(weights.keys())
    if missing:
        raise ValidationError(f"Missing required criteria: {missing}")
    
    # Check no extra keys
    extra = set(weights.keys()) - required_criteria
    if extra:
        raise ValidationError(f"Unknown criteria provided: {extra}")
    
    # Validate each weight
    for criterion, value in weights.items():
        if not isinstance(value, (int, float)):
            raise ValidationError(f"Weight for '{criterion}' must be numeric, got {type(value)}")
        
        if not 1 <= value <= 10:
            raise ValidationError(f"Weight for '{criterion}' must be between 1 and 10, got {value}")
    
    return True


def validate_goal(goal):
    """
    Validate goal selection.
    
    Args:
        goal: String goal identifier or None
    
    Raises:
        ValidationError: If goal is invalid
    """
    valid_goals = {"side_income", "long_term", "passion", None}
    
    if goal not in valid_goals:
        raise ValidationError(f"Invalid goal '{goal}'. Must be one of: {valid_goals}")
    
    return True


def validate_niche_data(niches):
    """
    Validate niche profile data structure.
    
    Args:
        niches: Dict of niche profiles
    
    Raises:
        ValidationError: If structure is invalid
    """
    if not niches:
        raise ValidationError("At least one niche must be provided")
    
    required_attribute_keys = {"skill", "time", "monetization", "competition", "growth", "investment"}
    
    for niche_name, data in niches.items():
        if not isinstance(data, dict):
            raise ValidationError(f"Niche '{niche_name}' data must be a dict")
        
        if "attributes" not in data:
            raise ValidationError(f"Niche '{niche_name}' missing 'attributes' key")
        
        attrs = data["attributes"]
        missing_attrs = required_attribute_keys - set(attrs.keys())
        if missing_attrs:
            raise ValidationError(f"Niche '{niche_name}' missing attributes: {missing_attrs}")
        
        # Validate score ranges
        for attr, score in attrs.items():
            if not isinstance(score, (int, float)):
                raise ValidationError(f"Niche '{niche_name}' attribute '{attr}' must be numeric")
            if not 1 <= score <= 10:
                raise ValidationError(f"Niche '{niche_name}' attribute '{attr}' must be 1-10, got {score}")
    
    return True