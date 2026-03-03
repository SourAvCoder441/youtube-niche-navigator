"""
Flask web application with structured input, domain-aware scoring, and refinement support.
"""

from flask import Flask, request, jsonify, render_template
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decision_engine.niche_profiles import NICHES
from decision_engine.weight_adjuster import adjust_weights
from decision_engine.scorer import calculate_scores, rank_niches
from decision_engine.risk_analysis import calculate_risk
from decision_engine.explanation import generate_explanation
from decision_engine.sensitivity import analyze_sensitivity
from decision_engine.prompt_parser import parse_prompt, PROFESSION_TO_DOMAIN, DOMAIN_TO_NICHE
from decision_engine.validator import ValidationError

app = Flask(__name__)


@app.route('/')
def index():
    """Render main input page with structured form."""
    professions = list(PROFESSION_TO_DOMAIN.keys())
    professions.extend([
        "Software Developer", "Web Developer", "Data Scientist",
        "Graphic Designer", "UI/UX Designer", "Artist",
        "Accountant", "Financial Advisor", "Banker",
        "Physician", "Nurse", "Fitness Coach", "Nutritionist",
        "Teacher", "Professor", "Researcher", "Scientist",
        "Entrepreneur", "Founder", "CEO", "Business Owner",
        "Writer", "Author", "Blogger",
        "Gamer", "Streamer", "Content Creator",
        "Student", "Beginner", "Hobbyist", "Other"
    ])
    professions = sorted(set(professions))
    
    return render_template('index.html', professions=professions)


@app.route('/api/parse', methods=['POST'])
def parse():
    data = request.get_json()
    
    try:
        if data.get('structured'):
            result = parse_prompt(None, structured_data=data['structured'])
        else:
            prompt = data.get('prompt', '').strip()
            if not prompt:
                return jsonify({"error": "Prompt cannot be empty"}), 400
            result = parse_prompt(prompt)
        
        return jsonify({
            "success": True,
            "parsed": result,
            "verification_needed": result.get('input_method') == 'freeform',
            "message": "Please verify we understood correctly"
        })
        
    except ValidationError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Parse error: {e}")
        return jsonify({"error": "Server error during parsing"}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    
    try:
        if data.get('structured'):
            parsed = parse_prompt(None, structured_data=data['structured'])
        else:
            parsed = parse_prompt(data.get('prompt', ''))
        
        weights = parsed['weights'].copy()  # copy to avoid mutating original
        goal = parsed['goal']
        predicted_niche = parsed.get('predicted_niche')
        
        print(f"\n{'='*60}")
        print(f"PROFESSION: {parsed.get('extracted', {}).get('profession', 'N/A')}")
        print(f"DOMAIN: {parsed.get('domain', 'N/A')}")
        print(f"PREDICTED NICHE: {predicted_niche}")
        print(f"BASE WEIGHTS: {weights}")
        print(f"GOAL: {goal}")
        
        adjusted_weights = adjust_weights(weights, goal)
        print(f"ADJUSTED WEIGHTS: {adjusted_weights}")
        
        scores = calculate_scores(
            NICHES, 
            adjusted_weights,
            preferred_niche=predicted_niche,
            domain_boost=0.50
        )
        
        ranked = rank_niches(scores)
        
        all_niche_data = {
            name: {"attributes": NICHES[name]["attributes"], "final_score": d["final_score"]}
            for name, d in scores.items()
        }
        
        recommendations = []
        for rank, (niche_name, data_item) in enumerate(ranked[:3], 1):
            attrs = NICHES[niche_name]["attributes"]
            risk_score, risk_level = calculate_risk(attrs)
            
            explanation = generate_explanation(
                niche_name, 
                attrs, 
                data_item["contributions"],
                risk_score,
                risk_level,
                adjusted_weights,
                all_niche_data,
                ranked
            )
            
            if data_item.get('domain_boost_applied'):
                explanation['summary'] += " (Includes 50% profession/interest boost.)"
            
            recommendations.append({
                "rank": rank,
                "name": niche_name,
                "score": round(data_item["final_score"], 4),
                "risk_level": risk_level,
                "explanation": explanation,
                "metadata": NICHES[niche_name]["metadata"],
                "domain_match": data_item.get('domain_boost_applied', False)
            })
        
        sensitivity = analyze_sensitivity(NICHES, weights, goal)
        
        response = {
            "success": True,
            "input_parsed": parsed,
            "weights": {"base": weights, "adjusted": adjusted_weights},
            "recommendations": recommendations,
            "sensitivity": sensitivity['confidence'],
            "predicted_match": predicted_niche
        }
        
        # Refinement flag for UI
        top_niche = recommendations[0]["name"] if recommendations else ""
        domain = parsed.get("domain", "")
        if (goal == "side_income" and 
            predicted_niche and 
            predicted_niche not in top_niche and 
            any(k in domain.lower() for k in ["gaming", "books", "health", "science", "design"])):
            response["show_refinement"] = True
            response["refinement_context"] = {
                "predicted": predicted_niche,
                "top_niche": top_niche,
                "original_parsed": parsed  # pass back for refinement
            }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Analyze error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/refine', methods=['POST'])
def refine():
    """
    Refinement endpoint: re-run analysis with user-selected adjustments.
    Expects original parsed input + choice from frontend.
    """
    data = request.get_json()
    
    try:
        original_parsed = data.get('original_parsed')
        choice = data.get('choice')
        
        if not original_parsed or not choice:
            return jsonify({"error": "Missing original_parsed or choice"}), 400
        
        # Make a copy to modify
        parsed = original_parsed.copy()
        weights = parsed['weights'].copy()
        goal = parsed['goal']
        predicted_niche = parsed.get('predicted_niche')
        
        # Apply refinement adjustments
        if choice == "fast":
            # Minimal change — keep original (fastest money)
            pass
        
        elif choice == "balanced":
            # Reduce money pressure, increase skill/time
            weights["monetization"] = max(3, weights["monetization"] - 3)
            weights["growth"] = max(3, weights["growth"] - 2)
            weights["skill"] = min(10, weights["skill"] + 4)
            weights["time"] = min(10, weights["time"] + 3)
            weights["competition"] = max(2, weights["competition"] - 2)  # slight help
        
        elif choice == "passion":
            # Strongly favor predicted/interest niche
            if predicted_niche:
                parsed['predicted_niche'] = predicted_niche  # reinforce
            else:
                # Fallback to domain primary
                parsed['predicted_niche'] = DOMAIN_TO_NICHE.get(parsed.get('domain', 'general'), {}).get('niche')
            
            weights["skill"] = min(10, weights["skill"] + 6)
            weights["time"] = min(10, weights["time"] + 5)
            weights["monetization"] = max(2, weights["monetization"] - 4)
            weights["competition"] = max(2, weights["competition"] - 3)
            weights["growth"] = max(3, weights["growth"] - 2)  # money secondary
        
        else:
            return jsonify({"error": "Invalid choice"}), 400
        
        # Re-apply goal adjustment (important!)
        adjusted_weights = adjust_weights(weights, goal)
        
        # Re-score
        scores = calculate_scores(
            NICHES,
            adjusted_weights,
            preferred_niche=parsed.get('predicted_niche'),
            domain_boost=0.50
        )
        
        ranked = rank_niches(scores)
        
        all_niche_data = {
            name: {"attributes": NICHES[name]["attributes"], "final_score": d["final_score"]}
            for name, d in scores.items()
        }
        
        recommendations = []
        for rank, (niche_name, data_item) in enumerate(ranked[:3], 1):
            attrs = NICHES[niche_name]["attributes"]
            risk_score, risk_level = calculate_risk(attrs)
            
            explanation = generate_explanation(
                niche_name, 
                attrs, 
                data_item["contributions"],
                risk_score,
                risk_level,
                adjusted_weights,
                all_niche_data,
                ranked
            )
            
            if data_item.get('domain_boost_applied'):
                explanation['summary'] += " (Includes 50% profession/interest boost.)"
            
            recommendations.append({
                "rank": rank,
                "name": niche_name,
                "score": round(data_item["final_score"], 4),
                "risk_level": risk_level,
                "explanation": explanation,
                "metadata": NICHES[niche_name]["metadata"],
                "domain_match": data_item.get('domain_boost_applied', False)
            })
        
        sensitivity = analyze_sensitivity(NICHES, weights, goal)
        
        return jsonify({
            "success": True,
            "input_parsed": parsed,
            "weights": {"base": weights, "adjusted": adjusted_weights},
            "recommendations": recommendations,
            "sensitivity": sensitivity['confidence'],
            "predicted_match": parsed.get('predicted_niche'),
            "refined_choice": choice
        })
        
    except Exception as e:
        print(f"Refine error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "niches": len(NICHES),
        "parser": "structured_v2_domain_aware"
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)