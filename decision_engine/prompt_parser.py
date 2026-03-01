"""
Natural language prompt parser for decision engine.
Extracts structured weights and goals from user text.
Uses keyword extraction with optional LLM enhancement.
"""

import re
from decision_engine.validator import ValidationError


def parse_prompt(prompt_text, use_llm=False):
    """
    Parse natural language prompt into structured inputs.
    
    Args:
        prompt_text: User's natural language description
        use_llm: Whether to use LLM for complex parsing
    
    Returns:
        Dict with 'weights' and 'goal'
    
    Raises:
        ValidationError: If prompt cannot be parsed
    """
    prompt_lower = prompt_text.lower()
    
    # Initialize defaults
    weights = {
        "skill": 5,
        "time": 5,
        "monetization": 5,
        "competition": 5,
        "growth": 5,
        "investment": 5
    }
    goal = None
    
    # Extract goal keywords
    goal_keywords = {
        "side_income": ["side income", "extra money", "part time", "passive income", "quick money"],
        "long_term": ["long term", "career", "full time", "sustainable", "future"],
        "passion": ["passion", "hobby", "love", "enjoy", "interest", "fun"]
    }
    
    for goal_type, keywords in goal_keywords.items():
        if any(kw in prompt_lower for kw in keywords):
            goal = goal_type
            break
    
    # Extract criterion priorities
    criterion_patterns = {
        "skill": [r"(good at|expert|skilled|experience|background).*(coding|programming|design|finance)"],
        "time": [r"(\\d+).*(hour|hr).*(day|week)", "full time", "part time", "limited time"],
        "monetization": ["money", "income", "revenue", "profit", "earn", "monetize", "cpm"],
        "competition": ["competition", "saturated", "crowded", "stand out", "unique"],
        "growth": ["growth", "viral", "trending", "fast", "quick growth", "explode"],
        "investment": ["budget", "cheap", "free", "equipment", "invest", "cost"]
    }
    
    # Boost weights based on mentions
    for criterion, patterns in criterion_patterns.items():
        mention_count = 0
        for pattern in patterns:
            if isinstance(pattern, str):
                if pattern in prompt_lower:
                    mention_count += 1
            else:
                if re.search(pattern, prompt_lower):
                    mention_count += 1
        
        # Adjust weight based on mention intensity
        if mention_count > 0:
            weights[criterion] = min(10, 5 + (mention_count * 2))
    
    # Handle explicit "not" or "don't care" to lower weights
    negation_patterns = {
        "skill": ["not technical", "no skill", "beginner", "learn from scratch"],
        "time": ["no time", "busy", "limited availability"],
        "monetization": ["not for money", "hobby", "fun not profit"],
        "competition": ["don't care about competition", "competition doesn't matter"],
        "growth": ["not looking for growth", "slow and steady"],
        "investment": ["no budget", "zero investment", "can't spend"]
    }
    
    for criterion, negs in negation_patterns.items():
        if any(neg in prompt_lower for neg in negs):
            weights[criterion] = max(1, weights[criterion] - 3)
    
    # Validate extracted data
    if all(w == 5 for w in weights.values()) and not goal:
        raise ValidationError("Could not extract preferences from prompt. Please be more specific.")
    
    return {
        "weights": weights,
        "goal": goal,
        "parsed_intent": infer_intent(weights, goal)
    }


def infer_intent(weights, goal):
    """Generate human-readable summary of parsed intent."""
    top_criteria = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:2]
    
    intent_parts = []
    if goal:
        intent_parts.append(f"Goal: {goal.replace('_', ' ')}")
    
    intent_parts.append(f"Priorities: {', '.join([c[0] for c in top_criteria])}")
    
    return " | ".join(intent_parts)