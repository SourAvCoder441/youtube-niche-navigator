# NicheNavigator – Decision Companion for YouTube Niches

**NicheNavigator** helps aspiring YouTubers choose a content niche by weighing personal goals against objective niche characteristics. It uses a transparent, deterministic multi‑criteria scoring model – **no black‑box AI** – so you always understand why a recommendation is made.

---

## 📖 Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Input Methods](#input-methods)
  - [Text Box (Quick Entry)](#text-box-quick-entry)
  - [CSV Upload (Full Control)](#csv-upload-full-control)
- [Scoring Methodology](#scoring-methodology)
- [Risk Model](#risk-model)
- [Interpreting the Results](#interpreting-the-results)
- [Assumptions & Limitations](#assumptions--limitations)
- [Running the Project](#running-the-project)
- [Future Improvements](#future-improvements)
- [Technology Stack](#technology-stack)

---

## Overview

Starting a YouTube channel involves multiple trade‑offs: skill alignment, time commitment, monetization potential, competition, growth prospects, and initial investment. Most creators rely on intuition, which can lead to mismatched choices and burnout.

NicheNavigator models this decision as a **weighted multi‑criteria evaluation**. You provide your background, goals, and a list of niche ideas – the system scores each niche, ranks them, and explains the reasoning. All calculations are deterministic and transparent.

---

## How It Works

1. **Step 1 – Profile & Goal**  
   - Select your profession (or choose “Other” and type your own).  
   - Indicate weekly hours available.  
   - Choose your primary goal: side income, long‑term career, or passion.  
   - Optionally list comma‑separated priorities and constraints (e.g., “growth, low competition”, “limited time, low budget”).  

2. **Step 2 – Options & Weights**  
   - Enter niche names (one per line) **or** upload a CSV file with your own attribute scores.  
   - Adjust the six criterion weights manually if desired (otherwise they are auto‑tuned based on your goal).  

3. **Step 3 – Results**  
   - View the top recommendation, confidence level, and a counterfactual (which niche would win if priorities shifted).  
   - For each evaluated niche, see a detailed card with:  
     - Rank, name, risk level, score (bolded).  
     - Score contribution bars.  
     - Strengths, concerns, and risk mitigation advice.  
     - Comparison with the runner‑up and winner.  

All logic is rule‑based – the ranking engine never uses AI.

---

## Input Methods

### Text Box (Quick Entry)

Type one niche per line, e.g.:
Gaming Shorts
AI Tool Reviews
Python Tutorials


The system **estimates** the six attributes for each niche using a built‑in keyword mapping. If a niche is not recognised, it falls back to average scores (5 across all criteria) and shows a warning.

### CSV Upload (Full Control)

For precise control, upload a CSV file with the following columns:

| Column        | Description                                  | Range  |
|---------------|----------------------------------------------|--------|
| `niche_name`  | Name of the niche (will appear in results)   | text   |
| `skill`       | How much expertise is required                | 1–10   |
| `time`        | Time efficiency (higher = less time needed)   | 1–10   |
| `monetization`| Revenue potential                             | 1–10   |
| `competition` | How crowded the niche is                      | 1–10   |
| `growth`      | Audience growth potential                     | 1–10   |
| `investment`  | Upfront cost (higher = cheaper to start)      | 1–10   |

**Example `my_niches.csv`**:
```csv
niche_name,skill,time,monetization,competition,growth,investment
Gaming Shorts,3,4,5,9,6,7
AI Tool Reviews,7,5,8,5,8,4
Python Tutorials,9,6,7,7,7,3

After uploading, the system uses your exact scores instead of estimating.

⚠️ All attribute values must be integers or decimals between 1 and 10. Missing values will cause an error.

Scoring Methodology
Normalisation
For maximise criteria (skill, time, monetisation, growth):
normalised = (value - min) / (max - min)

For minimise criteria (competition, investment):
normalised = (max - value) / (max - min)

Weighted Score
final_score = Σ ( weight[c] × normalised[c] )

Weights are either:
The custom weights you set in Step 2 (each 1–10, higher means more important), or
Automatically adjusted based on your goal if you leave custom weights at default.

Risk Model
Risk is calculated as a combination of competition, investment, and skill (inverted): 
risk = 0.4 × competition + 0.3 × investment + 0.3 × (10 - skill)

Risk Score	Level
≥ 7	High
4 – 6.9	Moderate
< 4	Low


Interpreting the Results
After evaluation, the results page shows:

Top Recommendation – the highest‑scoring niche.

Confidence – derived from sensitivity analysis (how stable the ranking is under small weight changes).

Counterfactual – which niche would win if your priorities shifted.

Each niche card includes:

Strengths – criteria where the niche excels, with contextual advice.

Concerns – weakest areas and potential pitfalls.

Why / Why Not – a short recommendation, why it’s not #1 (if applicable), and trade‑offs vs. the winner.

Comparison Context – head‑to‑head comparisons with the runner‑up.

Risk Mitigation – practical steps to reduce risk if you choose this niche.


Assumptions & Limitations
Attribute scores for built‑in niches are based on 2024‑2025 YouTube trends and are estimates, not guarantees.

The system assumes all criteria are independent – in reality, some may correlate (e.g., high competition often means higher skill).

Risk model is a simple linear combination; real‑world risk involves many more factors.

Only up to 12 niches can be evaluated at once to keep the interface clear.

The tool is not a crystal ball – it’s a thinking aid. Your execution, consistency, and creativity matter most.


Running the Project

1.Clone the repository.

2. Set up a virtual environment and install dependencies:
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Run the Flask app:
python web/app.py

4. Open your browser at http://127.0.0.1:5000.

5. Also deployed on Render : https://youtube-niche-navigator-1.onrender.com/


Future Improvements
User‑defined criteria – let users add their own evaluation dimensions.

Data‑driven scores – integrate with public APIs (e.g., YouTube search volume) to update niche attributes automatically.

More explanation formats – e.g., printable summary, comparison matrix.

Mobile app – wrap the current logic in a React Native frontend.

Technology Stack
Backend: Python, Flask

Decision Engine: Pure Python (no ML/AI libraries)

Frontend: HTML, CSS, JavaScript (vanilla)

Data Format: JSON for API, CSV for upload
