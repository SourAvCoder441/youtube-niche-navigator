from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decision_engine.niche_profiles import NICHES
from decision_engine.weight_adjuster import adjust_weights, normalize_weights
from decision_engine.scorer import calculate_scores, rank_niches
from decision_engine.risk_analysis import calculate_risk
from decision_engine.explanation import generate_explanation
from decision_engine.sensitivity import analyze_sensitivity
from decision_engine.prompt_parser import parse_prompt, PROFESSION_TO_DOMAIN, DEFAULT_WEIGHTS
from decision_engine.validator import (
    ValidationError,
    validate_goal,
    validate_weights,
    validate_niche_attributes,
    validate_niche_data,
)

app = Flask(__name__)


@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)


@app.route("/")
def index():
    professions = sorted(set(PROFESSION_TO_DOMAIN.keys()))
    return render_template("index.html", professions=professions)


def estimate_attributes(niche_name):
    """
    Deterministic fallback when user provides only niche names.
    This is rule-based mapping, not AI inference.
    """
    name_lower = niche_name.lower()

    if any(k in name_lower for k in ["coding", "programming", "developer", "python", "javascript"]):
        return NICHES["Coding Tutorials"]["attributes"].copy()
    if any(k in name_lower for k in ["ai", "chatgpt", "automation", "tech"]):
        return NICHES["AI Tools & Tech Explainers"]["attributes"].copy()
    if any(k in name_lower for k in ["gaming", "game", "stream"]):
        return NICHES["Gaming Content"]["attributes"].copy()
    if any(k in name_lower for k in ["finance", "money", "invest", "stocks"]):
        return NICHES["Personal Finance"]["attributes"].copy()
    if any(k in name_lower for k in ["design", "ui", "ux", "figma", "creative"]):
        return NICHES["Creative Design"]["attributes"].copy()
    if any(k in name_lower for k in ["fitness", "health", "workout", "gym"]):
        return NICHES["Health & Fitness"]["attributes"].copy()
    if any(k in name_lower for k in ["productivity", "lifestyle", "habit"]):
        return NICHES["Productivity & Lifestyle"]["attributes"].copy()
    if any(k in name_lower for k in ["book", "reading", "literature"]):
        return NICHES["Book Reviews & Literature"]["attributes"].copy()
    if any(k in name_lower for k in ["business", "startup", "entrepreneur"]):
        return NICHES["Business & Entrepreneurship"]["attributes"].copy()
    if any(k in name_lower for k in ["science", "education", "physics", "biology"]):
        return NICHES["Science & Education"]["attributes"].copy()

    return {k: 5 for k in DEFAULT_WEIGHTS}


def get_profile_and_weights(profile):
    if not isinstance(profile, dict):
        raise ValidationError("Profile payload must be an object")

    parsed = parse_prompt(None, structured_data=profile)
    parsed_weights = parsed.get("weights", {}).copy()
    parsed_goal = parsed.get("goal")
    preferred_niche = parsed.get("predicted_niche")

    custom_weights = profile.get("custom_weights")
    if custom_weights:
        validate_weights(custom_weights)
        base_weights = {k: float(v) for k, v in custom_weights.items()}
    else:
        validate_weights(parsed_weights)
        base_weights = {k: float(v) for k, v in parsed_weights.items()}

    goal = profile.get("goal", parsed_goal)
    if goal == "":
        goal = None
    validate_goal(goal)

    return parsed, base_weights, goal, preferred_niche


def prepare_niches(user_niches):
    if not isinstance(user_niches, list):
        raise ValidationError("Niches must be a list")
    if not user_niches:
        raise ValidationError("At least one niche is required")
    if len(user_niches) > 12:
        raise ValidationError("Maximum 12 niches allowed per evaluation")

    niches_to_score = {}
    for raw_niche in user_niches:
        if not isinstance(raw_niche, dict):
            raise ValidationError("Each niche entry must be an object")

        name = str(raw_niche.get("name", "")).strip()
        if not name:
            continue

        attrs = raw_niche.get("attributes")
        if attrs:
            cleaned_attrs = validate_niche_attributes(name, attrs)
        else:
            cleaned_attrs = validate_niche_attributes(name, estimate_attributes(name))

        niches_to_score[name] = {"attributes": cleaned_attrs}

    if not niches_to_score:
        raise ValidationError("No valid niche names were provided")

    validate_niche_data(niches_to_score)
    return niches_to_score


def build_counterfactual(ranked, adjusted_weights):
    if len(ranked) < 2:
        return {
            "message": "Not enough options to generate counterfactual.",
            "winner": ranked[0][0] if ranked else None,
            "runner_up": None,
        }

    winner_name, winner_data = ranked[0]
    runner_name, runner_data = ranked[1]
    score_gap = round(winner_data["final_score"] - runner_data["final_score"], 4)

    sorted_weights = sorted(adjusted_weights.items(), key=lambda x: x[1], reverse=True)
    focus_criteria = [k for k, _ in sorted_weights[:2]]

    return {
        "winner": winner_name,
        "runner_up": runner_name,
        "score_gap": score_gap,
        "focus_criteria": focus_criteria,
        "message": (
            f"If your priority shifts away from {focus_criteria[0]} and {focus_criteria[1]}, "
            f"{runner_name} is the most likely option to overtake {winner_name}."
        ),
    }


def build_decision_memo(recommendations, confidence):
    if not recommendations:
        return "No recommendation generated."
    top = recommendations[0]
    return (
        f"Top recommendation: {top['name']} (score {top['score']}, risk {top['risk_level']}). "
        f"Confidence level is {confidence.get('level', 'Unknown')}. "
        f"Reason: {top['explanation']['summary']}"
    )


@app.route("/api/parse_profile", methods=["POST"])
def parse_profile():
    data = request.get_json() or {}
    try:
        parsed = parse_prompt(None, structured_data=data)
        return jsonify({"success": True, "parsed": parsed})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@app.route("/api/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json() or {}
    try:
        profile = data.get("profile", {})
        user_niches = data.get("niches", [])

        parsed, base_weights, goal, preferred_niche = get_profile_and_weights(profile)
        niches_to_score = prepare_niches(user_niches)

        adjusted_weights = adjust_weights(base_weights, goal) if goal else normalize_weights(base_weights)
        scores = calculate_scores(
            niches_to_score,
            adjusted_weights,
            preferred_niche=preferred_niche,
            domain_boost=0.30,
            alt_domain_boost=0.10,
        )
        ranked = rank_niches(scores)

        all_niche_data = {
            name: {
                "attributes": niches_to_score[name]["attributes"],
                "final_score": score_data["final_score"],
            }
            for name, score_data in scores.items()
        }

        recommendations = []
        for rank, (niche_name, score_data) in enumerate(ranked, 1):
            attrs = niches_to_score[niche_name]["attributes"]
            risk_score, risk_level = calculate_risk(attrs)
            explanation = generate_explanation(
                niche_name,
                attrs,
                score_data["contributions"],
                risk_score,
                risk_level,
                adjusted_weights,
                all_niche_data,
                ranked,
            )

            recommendations.append(
                {
                    "rank": rank,
                    "name": niche_name,
                    "score": round(score_data["final_score"], 4),
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "contributions": score_data["contributions"],
                    "explanation": explanation,
                }
            )

        sensitivity = analyze_sensitivity(niches_to_score, base_weights, goal)
        counterfactual = build_counterfactual(ranked, adjusted_weights)
        decision_memo = build_decision_memo(recommendations, sensitivity["confidence"])

        return jsonify(
            {
                "success": True,
                "deterministic_mode": True,
                "goal": goal,
                "parsed_profile": parsed,
                "weights": {
                    "base": base_weights,
                    "adjusted": adjusted_weights,
                },
                "recommendations": recommendations,
                "sensitivity": sensitivity,
                "counterfactual": counterfactual,
                "decision_memo": decision_memo,
            }
        )
    except ValidationError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": f"Evaluation failed: {exc}"}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "niches": len(NICHES), "deterministic_mode": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
