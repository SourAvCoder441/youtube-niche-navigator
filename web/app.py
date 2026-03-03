"""
Flask web application with structured input and domain-aware scoring.
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
    # Add common variations
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
    """
    Step 1: Parse input and return for verification.
    """
    data = request.get_json()
    
    try:
        if data.get('structured'):
            result = parse_prompt(None, structured_data=data['structured'])
        else:
            result = parse_prompt(data.get('prompt', ''))
        
        return jsonify({
            "success": True,
            "parsed": result,
            "verification_needed": result.get('input_method') == 'freeform',
            "message": "Please verify we understood correctly"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Step 2: Process after verification with domain-aware scoring.
    """
    data = request.get_json()
    
    try:
        # Parse input
        if data.get('structured'):
            parsed = parse_prompt(None, structured_data=data['structured'])
        else:
            parsed = parse_prompt(data.get('prompt', ''))
        
        weights = parsed['weights']
        goal = parsed['goal']
        predicted_niche = parsed.get('predicted_niche')
        
        # DEBUG: Log what we received
        print(f"\n{'='*60}")
        print(f"PROFESSION: {parsed.get('extracted', {}).get('profession', 'N/A')}")
        print(f"DOMAIN: {parsed.get('domain', 'N/A')}")
        print(f"PREDICTED NICHE: {predicted_niche}")
        print(f"BASE WEIGHTS: {weights}")
        print(f"GOAL: {goal}")
        
        # Adjust weights based on goal (only here, no double adjust)
        adjusted_weights = adjust_weights(weights, goal)
        print(f"ADJUSTED WEIGHTS: {adjusted_weights}")
        
        # Calculate scores WITH domain boost (increased to 50%)
        scores = calculate_scores(
            NICHES, 
            adjusted_weights,
            preferred_niche=predicted_niche,
            domain_boost=0.50  # Increased for more variation
        )
        
        ranked = rank_niches(scores)
        
        # Log top 3 and all scores for debug
        print(f"ALL SCORES: { {name: d['final_score'] for name, d in scores.items()} }")
        print(f"TOP 3:")
        for i, (name, data) in enumerate(ranked[:3], 1):
            boost_flag = " [BOOSTED]" if data.get('domain_boost_applied') else ""
            print(f"  {i}. {name}: {data['final_score']:.4f}{boost_flag}")
        print(f"{'='*60}\n")
        
        # Build recommendations
        all_niche_data = {
            name: {"attributes": NICHES[name]["attributes"], "score": d["final_score"]}
            for name, d in scores.items()
        }
        
        recommendations = []
        for rank, (niche_name, data) in enumerate(ranked[:5], 1):
            attrs = NICHES[niche_name]["attributes"]
            risk_score, risk_level = calculate_risk(attrs)
            
            # FIXED: Added all_niche_data and ranked parameters
            explanation = generate_explanation(
                niche_name, 
                attrs, 
                data["contributions"],
                risk_score,
                risk_level,
                adjusted_weights,
                all_niche_data,  # Was missing
                ranked           # Was missing
            )
            
            # Add domain boost note to explanation if applied
            if data.get('domain_boost_applied'):
                explanation['summary'] += " (Includes 50% profession expertise boost.)"
            
            recommendations.append({
                "rank": rank,
                "name": niche_name,
                "score": round(data["final_score"], 4),
                "risk_level": risk_level,
                "explanation": explanation,
                "metadata": NICHES[niche_name]["metadata"],
                "domain_match": data.get('domain_boost_applied', False)
            })
        
        # Sensitivity
        sensitivity = analyze_sensitivity(NICHES, weights, goal)
        
        return jsonify({
            "success": True,
            "input_parsed": parsed,
            "weights": {"base": weights, "adjusted": adjusted_weights},
            "recommendations": recommendations,
            "sensitivity": sensitivity['confidence'],
            "predicted_match": predicted_niche
        })
        
    except Exception as e:
        print(f"ERROR: {e}")
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