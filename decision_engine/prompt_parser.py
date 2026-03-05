"""
Structured natural language parser for decision engine.
Hybrid approach: guided input with optional free-form and verification layer.
"""

import re
from decision_engine.validator import ValidationError


# Domain knowledge base - extensible lookup tables
PROFESSION_TO_DOMAIN = {
    "software engineer": "tech", "developer": "tech", "programmer": "tech",
    "coder": "tech", "engineer": "tech", "data scientist": "tech",
    "web developer": "tech", "app developer": "tech", "computer science": "tech",
    "Software Developer": "tech", "Web Developer": "tech", "Data Scientist": "tech",
    "designer": "design", "graphic designer": "design", "ui designer": "design",
    "ux designer": "design", "artist": "design", "creative": "design",
    "photographer": "design", "video editor": "design",
    "Graphic Designer": "design", "UI/UX Designer": "design", "Artist": "design",
    "accountant": "finance", "financial analyst": "finance", "banker": "finance",
    "investor": "finance", "trader": "finance", "economist": "finance",
    "finance professional": "finance", "cpa": "finance",
    "Accountant": "finance", "Financial Advisor": "finance", "Banker": "finance",
    "doctor": "health", "physician": "health", "nurse": "health",
    "trainer": "health", "fitness coach": "health", "nutritionist": "health",
    "therapist": "health", "personal trainer": "health", "gym instructor": "health",
    "Physician": "health", "Nurse": "health", "Fitness Coach": "health", "Nutritionist": "health",
    "health professional": "health",
    "teacher": "science", "professor": "science", "researcher": "science",
    "scientist": "science", "phd": "science", "academic": "science",
    "physicist": "science", "biologist": "science", "chemist": "science",
    "Teacher": "science", "Professor": "science", "Researcher": "science", "Scientist": "science",
    "entrepreneur": "business", "founder": "business", "ceo": "business",
    "startup": "business", "business owner": "business", "consultant": "business",
    "marketer": "business", "sales": "business",
    "Entrepreneur": "business", "Founder": "business", "CEO": "business", "Business Owner": "business",
    "gamer": "gaming", "streamer": "gaming", "player": "gaming",
    "Gamer": "gaming", "Streamer": "gaming", "Content Creator": "gaming",
    "writer": "books", "author": "books", "journalist": "books",
    "blogger": "books", "editor": "books", "poet": "books",
    "Writer": "books", "Author": "books", "Blogger": "books",
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

DEFAULT_WEIGHTS = {
    "skill": 5,
    "time": 5,
    "monetization": 5,
    "competition": 5,
    "growth": 5,
    "investment": 5
}

def detect_domain(profession):
    profession_lower = profession.lower().strip()
    for key, domain in PROFESSION_TO_DOMAIN.items():
        if key in profession_lower:
            return domain
    return "general"

def predict_niche(domain):
    if domain in DOMAIN_TO_NICHE:
        return DOMAIN_TO_NICHE[domain]["niche"]
    return None

def adjust_for_domain(weights, domain):
    if domain in DOMAIN_TO_NICHE:
        skill_boost = DOMAIN_TO_NICHE[domain]["skill_boost"]
        weights["skill"] = min(10, weights["skill"] + skill_boost // 2)
    return weights

def adjust_for_time(weights, hours):
    if hours <= 5:
        weights["time"] = 8
        weights["investment"] = min(10, weights["investment"] + 3)
    elif 5 < hours <= 20:
        weights["time"] = 5
    else:
        weights["time"] = 2
    return weights

def adjust_for_priorities(weights, priorities):
    for p in priorities:
        p_lower = p.lower()
        if p_lower in weights:
            weights[p_lower] = min(10, weights[p_lower] + 4)
        elif "money" in p_lower or "revenue" in p_lower:
            weights["monetization"] += 4
        elif "easy" in p_lower or "beginner" in p_lower:
            weights["skill"] -= 3
            weights["competition"] += 3
    return weights

def adjust_for_constraints(weights, constraints):
    for c in constraints:
        c_lower = c.lower()
        negation = any(word in c_lower for word in ["not", "no", "don't", "cannot"])
        adjustment = -3 if not negation else +3
        if any(k in c_lower for k in ["time", "hours", "busy", "limited time"]):
            weights["time"] = max(1, weights["time"] + adjustment)
        if any(k in c_lower for k in ["money", "budget", "cost", "expensive", "investment"]):
            weights["investment"] = max(1, weights["investment"] + adjustment)
        if any(k in c_lower for k in ["skill", "technical", "learn", "hard"]):
            weights["skill"] = max(1, weights["skill"] + adjustment)
        if "competition" in c_lower:
            weights["competition"] = max(1, weights["competition"] + adjustment)
    return weights

def clamp_weights(weights):
    for key in weights:
        weights[key] = max(1, min(10, weights[key]))
    return weights

def detect_goal(goal_desc):
    goal_lower = goal_desc.lower()
    for goal, keywords in GOAL_KEYWORDS.items():
        if any(k in goal_lower for k in keywords):
            return goal
    return None

def parse_structured(profession, hours_per_week, goal, priorities, constraints):
    weights = DEFAULT_WEIGHTS.copy()
    
    domain = detect_domain(profession)
    predicted_niche = predict_niche(domain)
    weights = adjust_for_domain(weights, domain)
    
    hours = parse_hours(hours_per_week)
    weights = adjust_for_time(weights, hours)
    
    weights = adjust_for_priorities(weights, priorities)
    weights = adjust_for_constraints(weights, constraints)
    
    weights = clamp_weights(weights)
    
    inferred_goal = goal if goal in {"side_income", "long_term", "passion"} else None

    result = {
        "weights": weights,
        "goal": inferred_goal,
        "domain": domain,
        "predicted_niche": predicted_niche,
        "extracted": {
            "profession": profession,
            "hours": hours,
            "priorities": priorities,
            "constraints": constraints
        },
        "input_method": "structured"
    }
    
    # === VERY STRONG INTEREST OVERRIDE (main change) ===
    interest_keywords = {
        "gaming": "Gaming Content",
        "game": "Gaming Content",
        "games": "Gaming Content",
        "let's play": "Gaming Content",
        "book": "Book Reviews & Literature",
        "books": "Book Reviews & Literature",
        "reading": "Book Reviews & Literature",
        "fitness": "Health & Fitness",
        "workout": "Health & Fitness",
        "gym": "Health & Fitness",
        "ai": "AI Tools & Tech Explainers",
        "artificial intelligence": "AI Tools & Tech Explainers",
        "chatgpt": "AI Tools & Tech Explainers",
        "coding": "Coding Tutorials",
        "programming": "Coding Tutorials",
        "python": "Coding Tutorials",
        "design": "Creative Design",
        "figma": "Creative Design",
        "finance": "Personal Finance",
        "money": "Personal Finance",
        "business": "Business & Entrepreneurship",
        "startup": "Business & Entrepreneurship",
        "science": "Science & Education",
        "education": "Science & Education"
    }

    priorities_text = " ".join([p.lower() for p in priorities])
    matched_niche = None
    matched_topic = None

    for topic, niche_name in interest_keywords.items():
        if topic in priorities_text:
            matched_niche = niche_name
            matched_topic = topic
            break
    
    if matched_niche:
        result["predicted_niche"] = matched_niche
        result["override_reason"] = f"Strong interest in '{matched_topic}' → forced niche: {matched_niche}"
        
        # Extremely strong boosts when interest is specified
        result["weights"]["skill"] = min(10, result["weights"]["skill"] + 10)      # massive skill boost
        result["weights"]["time"] = min(10, result["weights"]["time"] + 9)        # time efficiency
        result["weights"]["monetization"] = max(1, result["weights"]["monetization"] - 7)   # money secondary
        result["weights"]["competition"] = max(1, result["weights"]["competition"] - 6)     # help saturated
        result["weights"]["growth"] = max(1, result["weights"]["growth"] - 5)               # growth secondary
    
    # Extra passion boost if goal is passion
    if result["goal"] == "passion":
        result["weights"]["skill"] = min(10, result["weights"]["skill"] + 5)
        result["weights"]["time"] = min(10, result["weights"]["time"] + 5)
        result["weights"]["monetization"] = max(1, result["weights"]["monetization"] - 5)
        result["weights"]["competition"] = max(1, result["weights"]["competition"] - 3)

    return result


def parse_freeform(prompt_text):
    prompt_lower = prompt_text.lower()
    
    profession = "general"
    profession_patterns = [
        r"(i am|i'm|my background is|work as) (a|an) ([\w\s]+)",
        r"profession: ([\w\s]+)",
        r"background: ([\w\s]+)"
    ]
    for pattern in profession_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            profession = match.group(1).strip() if len(match.groups()) == 1 else match.group(3).strip()
            break
    
    hours = 10
    hour_patterns = [
        r"(\d+)\s*hours?\s*(a|per)\s*week",
        r"(\d+)\s*h\s*/?\s*w",
        r"part time", r"full time", r"no time", r"busy", r"limited time"
    ]
    for pattern in hour_patterns:
        if isinstance(pattern, str) and pattern in prompt_lower:
            if pattern in ["part time", "limited time"]:
                hours = 10
            elif pattern == "full time":
                hours = 40
            elif pattern in ["no time", "busy"]:
                hours = 2
            break
        else:
            match = re.search(pattern, prompt_lower)
            if match:
                try:
                    hours = int(match.group(1))
                except:
                    pass
                break
    
    goal_desc = prompt_text
    goal = detect_goal(goal_desc)
    
    priorities = []
    priority_patterns = [
        r"care about ([\w\s,]+)",
        r"priority is ([\w\s,]+)",
        r"matters most is ([\w\s,]+)",
        r"focus on ([\w\s,]+)",
        r"important to me is ([\w\s,]+)",
        r"i value ([\w\s,]+)",
        r"main topics.*: ([\w\s,]+)",
        r"interests.*: ([\w\s,]+)"
    ]
    for pattern in priority_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            priorities = [p.strip() for p in match.group(1).split(",")]
            break
    
    constraints = []
    constraint_indicators = ["don't have", "no ", "limited", "can't", "struggle with", "hate spending"]
    for indicator in constraint_indicators:
        if indicator in prompt_lower:
            idx = prompt_lower.find(indicator)
            context = prompt_lower[idx:idx+50]
            constraints.append(context.strip())
    
    result = parse_structured(profession, hours, goal, priorities, constraints)
    result["input_method"] = "freeform"
    result["extracted"] = {
        "profession": profession,
        "hours": hours,
        "priorities": priorities,
        "constraints": constraints
    }
    
    return result


def parse_hours(hours_input):
    if isinstance(hours_input, (int, float)):
        return float(hours_input)
    
    hours_str = str(hours_input).lower().strip()
    
    if hours_str in ["none", "no time", "zero", "busy", "limited"]:
        return 2
    if hours_str in ["minimal", "very little"]:
        return 5
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
