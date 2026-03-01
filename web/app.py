"""
Flask web application for NicheNavigator.
Provides API endpoints for prompt-based decision support.
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
from decision_engine.prompt_parser import parse_prompt
from decision_engine.validator import ValidationError

app = Flask(__name__)


@app.route('/')
def index():
    """Render main input page."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    API endpoint: Analyze prompt and return recommendations.
    
    Request: {"prompt": "I want side income, good at coding, limited time"}
    Response: {"recommendations": [...], "parsed": {...}, "sensitivity": {...}}
    """
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt required"}), 400
    
    try:
        # Parse natural language
        parsed = parse_prompt(data['prompt'])
        base_weights = parsed['weights']
        goal = parsed['goal']
        
        # Process through decision engine
        weights = adjust_weights(base_weights, goal)
        scores = calculate_scores(NICHES, weights)
        ranked = rank_niches(scores)
        
        # Prepare all niche data for explanations
        all_niche_data = {
            name: {"attributes": NICHES[name]["attributes"], "score": data["final_score"]}
            for name, data in scores.items()
        }
        
        # Build recommendations
        recommendations = []
        for rank, (niche_name, data) in enumerate(ranked[:5], 1):
            attributes = NICHES[niche_name]["attributes"]
            risk_score, risk_level = calculate_risk(attributes)
            
            explanation = generate_explanation(
                niche_name, attributes, data["contributions"],
                risk_score, risk_level, weights,
                all_niche_data, ranked
            )
            
            recommendations.append({
                "rank": rank,
                "name": niche_name,
                "score": round(data["final_score"], 4),
                "risk_level": risk_level,
                "explanation": explanation,
                "metadata": NICHES[niche_name]["metadata"]
            })
        
        # Sensitivity analysis
        sensitivity = analyze_sensitivity(NICHES, base_weights, goal)
        
        return jsonify({
            "success": True,
            "parsed": parsed,
            "weights": {"base": base_weights, "adjusted": weights},
            "recommendations": recommendations,
            "sensitivity": {
                "confidence": sensitivity["confidence"],
                "alternative_scenarios": sensitivity["alternative_scenarios"][:2]
            }
        })
        
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Processing failed"}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "niches_loaded": len(NICHES),
        "version": "1.0.0"
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)