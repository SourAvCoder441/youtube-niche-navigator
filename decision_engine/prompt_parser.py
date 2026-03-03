"""
Structured natural language parser for decision engine.
Hybrid approach: guided input with optional free-form and verification layer.
"""

import re
from decision_engine.validator import ValidationError


# Domain knowledge base - extensible lookup tables
PROFESSION_TO_DOMAIN = {
    # Tech
    "software engineer": "tech", "developer": "tech", "programmer": "tech",
    "coder": "tech", "engineer": "tech", "data scientist": "tech",
    "web developer": "tech", "app developer": "tech", "computer science": "tech",
    "Software Developer": "tech", "Web Developer": "tech", "Data Scientist": "tech",
    # Design
    "designer": "design", "graphic designer": "design", "ui designer": "design",
    "ux designer": "design", "artist": "design", "creative": "design",
    "photographer": "design", "video editor": "design",
    "Graphic Designer": "design", "UI/UX Designer": "design", "Artist": "design",
    # Finance
    "accountant": "finance", "financial analyst": "finance", "banker": "finance",
    "investor": "finance", "trader": "finance", "economist": "finance",
    "finance professional": "finance", "cpa": "finance",
    "Accountant": "finance", "Financial Advisor": "finance", "Banker": "finance",
    # Health
    "doctor": "health", "physician": "health", "nurse": "health",
    "trainer": "health", "fitness coach": "health", "nutritionist": "health",
    "therapist": "health", "personal trainer": "health", "gym instructor": "health",
    "Physician": "health", "Nurse": "health", "Fitness Coach": "health", "Nutritionist": "health",
    "health professional": "health",
    # Science
    "teacher": "science", "professor": "science", "researcher": "science",
    "scientist": "science", "phd": "science", "academic": "science",
    "physicist": "science", "biologist": "science", "chemist": "science",
    "Teacher": "science", "Professor": "science", "Researcher": "science", "Scientist": "science",
    # Business
    "entrepreneur": "business", "founder": "business", "ceo": "business",
    "startup": "business", "business owner": "business", "consultant": "business",
    "marketer": "business", "sales": "business",
    "Entrepreneur": "business", "Founder": "business", "CEO": "business", "Business Owner": "business",
    # Gaming (low skill entry)
    "gamer": "gaming", "streamer": "gaming", "player": "gaming",
    "Gamer": "gaming", "Streamer": "gaming", "Content Creator": "gaming",
    # Writing
    "writer": "books", "author": "books", "journalist": "books",
    "blogger": "books", "editor": "books", "poet": "books",
    "Writer": "books", "Author": "books", "Blogger": "books",
    # General (low skill)
    "student": "general", "beginner": "general", "hobbyist": "general",
    "enthusiast": "general", "none": "general", "": "general",
    "Student": "general", "Beginner": "general", "Hobbyist": "general", "Other": "general"
}

DOMAIN_TO_NICHE = {
    "tech": {"niche": "Coding Tutorials", "skill_boost": 8, "alt": "AI Tools & Tech Explainers"},
    "design": {"niche": "Creative Design", "skill_boost": 7, "alt": None},
    "finance": {"niche": "Personal Finance", "skill_boost": 6, "alt": "Business & Entrepreneurship"},
    "health": {"niche": "Health & Fitness", "skill_boost": 5, "alt": None},
    "science": {"niche": "Science & Education", "skill_boost": 8, "alt": None},
    "business": {"niche": "Business & Entrepreneurship", "skill_boost": 6, "alt": "Personal Finance"},
    "gaming": {"niche": "Gaming Content", "skill_boost": 3, "alt": None},
    "books": {"niche": "Book Reviews & Literature", "skill_boost": 3, "alt": None},
    "general": {"niche": "Productivity & Lifestyle", "skill_boost": 2, "alt": None}
}

GOAL_KEYWORDS = {
    "side_income": ["side income", "extra money", "part time", "passive income", 
                    "side hustle", "earn money", "make money", "supplement income", "quick cash"],
    "long_term": ["career", "full time", "quit job", "main income", "sustainable",
                  "long term", "professional", "future", "build business", "long-term growth"],
    "passion": ["hobby", "passion", "fun", "enjoy", "personal interest", "creative outlet"]
}

# Default weights
DEFAULT_WEIGHTS = {
    "skill": 5,
    "time": 5,
    "monetization": 5,
    "competition": 5,
    "growth": 5,
    "investment": 5
}

def detect_domain(profession):
    """Map profession to domain."""
    profession_lower = profession.lower().strip()
    for key, domain in PROFESSION_TO_DOMAIN.items():
        if key in profession_lower:
            return domain
    return "general"  # Default if not detected

def predict_niche(domain):
    """Predict primary niche based on domain."""
    if domain in DOMAIN_TO_NICHE:
        return DOMAIN_TO_NICHE[domain]["niche"]
    return None

def adjust_for_domain(weights, domain):
    """Boost weights based on domain skill requirements."""
    if domain in DOMAIN_TO_NICHE:
        skill_boost = DOMAIN_TO_NICHE[domain]["skill_boost"]
        weights["skill"] = min(10, weights["skill"] + skill_boost // 2)  # Half boost to weight
    return weights

def adjust_for_time(weights, hours):
    """Adjust weights based on available hours (fixed inversion)."""
    if hours <= 5:
        weights["time"] = 8  # High importance: Prioritize time-efficient niches
        weights["investment"] = min(10, weights["investment"] + 3)  # Assume low budget
    elif 5 < hours <= 20:
        weights["time"] = 5
    else:
        weights["time"] = 2  # Low importance if plenty of time
    return weights

def adjust_for_priorities(weights, priorities):
    """Boost weights for mentioned priorities."""
    for p in priorities:
        p_lower = p.lower()
        if p_lower in weights:
            weights[p_lower] = min(10, weights[p_lower] + 4)  # More extreme boost
        elif "money" in p_lower or "revenue" in p_lower:
            weights["monetization"] += 4
        elif "easy" in p_lower:
            weights["skill"] -= 3
            weights["competition"] += 3
    return weights

def adjust_for_constraints(weights, constraints):
    """Penalize weights for constraints (with negation handling)."""
    for c in constraints:
        c_lower = c.lower()
        negation = "not" in c_lower or "no" in c_lower or "don't" in c_lower
        adjustment = -3 if not negation else +3  # Better negation
        if "time" in c_lower:
            weights["time"] = max(1, weights["time"] + adjustment)
        if "money" in c_lower or "budget" in c_lower:
            weights["investment"] = max(1, weights["investment"] + adjustment)
        if "skill" in c_lower or "technical" in c_lower:
            weights["skill"] = max(1, weights["skill"] + adjustment)
        if "competition" in c_lower:
            weights["competition"] = max(1, weights["competition"] + adjustment)
    return weights

def clamp_weights(weights):
    """Clamp weights between 1 and 10."""
    for key in weights:
        weights[key] = max(1, min(10, weights[key]))
    return weights

def detect_goal(goal_desc):
    """Detect goal from description (no weight adjust here)."""
    goal_lower = goal_desc.lower()
    for goal, keywords in GOAL_KEYWORDS.items():
        if any(k in goal_lower for k in keywords):
            return goal
    return None

def parse_structured(profession, hours_per_week, goal, priorities, constraints):
    """Parse structured input."""
    weights = DEFAULT_WEIGHTS.copy()
    
    # Domain and niche prediction
    domain = detect_domain(profession)
    predicted_niche = predict_niche(domain)
    weights = adjust_for_domain(weights, domain)
    
    # Time adjustment (fixed)
    hours = parse_hours(hours_per_week)
    weights = adjust_for_time(weights, hours)
    
    # Priorities and constraints
    weights = adjust_for_priorities(weights, priorities)
    weights = adjust_for_constraints(weights, constraints)
    
    # Clamp
    weights = clamp_weights(weights)
    
    return {
        "weights": weights,
        "goal": goal or detect_goal(""),  # Use provided goal
        "domain": domain,
        "predicted_niche": predicted_niche,
        "extracted": {
            "profession": profession,
            "hours": hours,
            "priorities": priorities,
            "constraints": constraints
        },
        "input_method": "structured",
        "explanation_trace": []  # Add traces if needed
    }

def parse_freeform(prompt_text):
    prompt_lower = prompt_text.lower()
    
    # ... keep your existing profession, hours, goal, priorities, constraints extraction ...

    result = parse_structured(profession, hours, goal, priorities, constraints)
    result["input_method"] = "freeform"
    result["extracted"] = {
        "profession": profession,
        "hours": hours,
        "priorities": priorities,
        "constraints": constraints
    }

    # NEW: strong interest override (can override predicted niche)
    interest_patterns = [
        r"(?:really want|want to make|passionate about|love making) (?:content about|videos on|a channel on) (.+?)(?:\.|\,| and|$)",
        r"my (?:passion|interest|hobby) is (?:.+? )?(.+?)(?:\.|\,| and|$)",
        r"(gaming|books|reading|fitness|ai|coding|design|finance|business|science)"
    ]

    for pattern in interest_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            topic = match.group(1).strip().lower() if match.groups() else match.group(0).lower()
            topic_to_niche = {
                "gaming": "Gaming Content",
                "game": "Gaming Content",
                "games": "Gaming Content",
                "book": "Book Reviews & Literature",
                "books": "Book Reviews & Literature",
                "reading": "Book Reviews & Literature",
                "fitness": "Health & Fitness",
                "workout": "Health & Fitness",
                "ai": "AI Tools & Tech Explainers",
                "artificial intelligence": "AI Tools & Tech Explainers",
                "coding": "Coding Tutorials",
                "programming": "Coding Tutorials",
                "design": "Creative Design",
                "finance": "Personal Finance",
                "business": "Business & Entrepreneurship",
                "science": "Science & Education"
            }
            for k, niche_name in topic_to_niche.items():
                if k in topic:
                    result["predicted_niche"] = niche_name
                    result["override_reason"] = f"Detected strong interest in '{topic}' → forced niche: {niche_name}"
                    # Optional: give extra weight boost to skill/time
                    result["weights"]["skill"] = min(10, result["weights"]["skill"] + 3)
                    result["weights"]["time"] = min(10, result["weights"]["time"] + 2)
                    break
            if "override_reason" in result:
                break

    return result

def parse_hours(hours_input):
    """Normalize hours input to number."""
    if isinstance(hours_input, (int, float)):
        return float(hours_input)
    
    hours_str = str(hours_input).lower().strip()
    
    if hours_str in ["none", "no time", "zero"]:
        return 0
    if hours_str in ["minimal", "very little", "busy", "limited"]:
        return 2
    if hours_str in ["part time", "part-time", "some"]:
        return 10
    if hours_str in ["full time", "full-time", "dedicated"]:
        return 40
    if hours_str in ["all time", "always", "24/7"]:
        return 60
    
    try:
        return float(hours_str)
    except:
        return 10


def parse_prompt(prompt_text, structured_data=None):
    """
    Main entry point: chooses parser based on input type.
    """
    if structured_data:
        return parse_structured(
            structured_data.get("profession", "general"),
            structured_data.get("hours_per_week", 10),
            structured_data.get("goal", ""),
            structured_data.get("priorities", []),
            structured_data.get("constraints", [])
        )
    else:
        return parse_freeform(prompt_text)