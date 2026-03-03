# Build Process – NicheNavigator

---

## Day 1 – Understanding the Assignment

On the first day, I discussed the assignment with a few others who also received it. We shared interpretations of the problem statement and clarified doubts about what the evaluators might be expecting.

After that, I carefully read the entire question again and tried to break it down.

The key insight I derived was that this was not just a coding assignment. The evaluation criteria emphasized:

- Clarity of thinking  
- System design maturity  
- Transparency in the build process  
- Responsible use of AI  

The most important constraint was:

- The system must not rely entirely on AI  
- The logic must be explainable  
- The user should be able to change inputs and get different outcomes  

From this, I understood that building a fully AI-driven recommendation tool would not align with the spirit of the assignment. The core decision-making logic needed to be deterministic and structured.

This shifted my mindset from "build something smart" to "build something explainable."

---

## Day 2 – Exploring Possible Domains

I started exploring possible domains for the decision companion.

### Idea 1: Travel Decision Companion

My first idea was a travel-based system. It would help users decide between bundled tourist activities versus individual bookings, optimize itineraries, and compare costs.

However, as I thought deeper, I realized:
- Travel decisions involve too many uncertain variables.
- Real-time pricing and constraints would increase complexity.
- The scope could quickly become unmanageable within 11 days.

It felt ambitious but risky.

---

### Idea 2: Healthy Food Decision Companion

Next, I considered a system that evaluates whether a food item is healthy based on calories, sugar content, and nutritional values.

While feasible, it felt:
- Too common
- Less strategically interesting
- More like a nutrition calculator than a decision system

It did not strongly demonstrate system design thinking.

---

## Final Decision – YouTube Niche Navigator

Eventually, I selected the YouTube niche selection domain.

This choice was personal and strategic.

I currently run a YouTube channel myself and understand the difficulty of:
- Growing an audience
- Reaching monetization eligibility
- Competing in saturated niches

YouTube is a zero-budget business opportunity accessible even to students. However, competition is extremely high, and choosing the wrong niche can lead to burnout or stagnation.

This domain naturally contains trade-offs:
- Skill alignment
- Time commitment
- Monetization potential
- Competition level
- Growth trends
- Initial investment

This made it ideal for a structured multi-criteria decision system.

---

## Day 3 – Modeling the Decision Framework

Once the domain was finalized, I began designing the decision model.

I limited the system intentionally to:
- Three niche options
- Six evaluation criteria

This was a deliberate scope-control decision to:
- Maintain depth over breadth
- Avoid overengineering
- Ensure clarity and strong documentation

I evaluated multiple decision modeling techniques:

Considered:
- Analytic Hierarchy Process (AHP)
- Machine Learning classification
- Weighted scoring model

Selected:
- Weighted Multi-Criteria Scoring

Reason:
- Simpler implementation
- Fully explainable
- Clear traceability
- Easy to test

The scoring methodology included normalization to handle maximize/minimize criteria and ensure fairness.

---

## Day 4 – Architecture and Implementation

On Day 4, I focused on structuring the architecture properly.

I separated the system into:

1. Decision Engine
2. Weight Adjustment Module
3. Risk Analysis Module
4. (Planned) Web Layer using Flask

I ensured that:
- The decision engine is independent of Flask.
- Logic modules are modular and testable.
- Imports are structured using package-based execution.

While testing, I encountered a module resolution issue when running test scripts directly. The error was:

ModuleNotFoundError: No module named 'decision_engine'

After investigating, I realized the issue was related to execution context and Python package structure. I resolved it by running tests using:

python -m tests.manual_test

This ensured proper module resolution and reinforced clean architecture practices.

---

## Reflection So Far

The biggest shift in this project was understanding that:

Explainability > Complexity

Instead of trying to build a highly intelligent AI system, I focused on building a transparent and structured decision model.

The goal is not to predict YouTube success, but to help users think more clearly about their choices.

The next steps will focus on:
- Explanation generation
- Ranking clarity
- Web interface integration
- Improved testing


## Day 5 – Core Engine Enhancement (Day 2 of focused build)

After establishing the foundation, I focused on three critical gaps:
1. **Explanation capability** – The "why" behind recommendations
2. **Sensitivity analysis** – Understanding recommendation robustness  
3. **Input validation** – Production-ready error handling


I realized the system was calculating scores but not communicating reasoning effectively. The assignment specifically asks to "explain why a particular recommendation was made."

**Design decisions:**
- Structured explanations with: summary, strengths, concerns, risk context, recommendation
- Context-aware messaging (different text for high vs low scores)
- No templated strings – dynamic generation based on actual contributions
- Deterministic logic: same scores always produce same explanations

**Rejected approach:** Using AI/LLM to generate explanations.
**Reason:** Would violate explainability constraint and create non-deterministic outputs.


This was my "above and beyond" feature. I wanted to answer: *"How confident should the user be in this recommendation?"*

**Algorithm design:**
- Perturb each weight by ±15% across multiple iterations
- Track position stability for each niche
- Calculate variance and most common ranking
- Identify scenarios where a different niche would win

**Key insight:** If small changes in priorities flip the recommendation, the decision is sensitive and requires more user reflection.

**Implementation challenge:** Ensuring perturbations stayed within 1-10 range while maintaining weight ratios.
**Solution:** Clamp individual weights before normalization, not after.


Added defensive programming:
- `validator.py` with comprehensive input checking
- Custom `ValidationError` for clear error messaging
- Updated `manual_test.py` to demonstrate all features

**Refactoring decision:** Updated niche structure to separate `attributes` from `metadata`.
**Why:** Cleaner separation of concerns – scoring engine only needs attributes, explanation module benefits from metadata.


## Day 6 – Niche Expansion & Output Clarity (Day 3 of focused build)

Expanded from 3 to 10 niches and enhanced explanation depth.


Researched 2024-2025 YouTube creator economy trends to identify high-potential niches with distinct risk profiles.

**Selection criteria for new niches:**
- Must fill gaps in current risk/reward spectrum
- Must have clear differentiation from existing 3
- Must maintain scoring anchor points (1-2 and 9-10 extremes)
- Must represent viable creator paths with different barrier types

**Added 7 niches:**
1. **Personal Finance** – High trust barrier, strong monetization (YMYL category)
2. **Creative Design** – Visual skill-based, portfolio-driven
3. **Health & Fitness** – High responsibility, results-based credibility
4. **Productivity & Lifestyle** – Low barrier, high competition (beginner trap)
5. **Book Reviews** – Long tail, minimal investment, slow growth
6. **Business/Entrepreneurship** – Credibility-dependent, high CPM
7. **Science/Education** – High accuracy requirements, evergreen content

**Scoring methodology:**
- Used observed CPM data, competition saturation, and skill requirements
- Ensured at least one niche at extremes for each criterion to maintain normalization quality
- Cross-referenced with creator economy reports (no real-time scraping)


Realized "why this niche" required **comparative context**, not just absolute scores.

**Added to explanation module:**
- **Percentile rankings**: Shows where niche stands vs all 10 options
- **Category average comparison**: "40% above average" vs raw scores
- **Runner-up analysis**: Specific wins/losses vs #2 ranked niche
- **Trade-off identification**: Explicit "you win on X, they win on Y" language
- **Swap potential indicator**: Flags when small priority shifts change winner

**Design decision:** Explanations now require `all_niche_data` and `ranked_list` parameters.
**Trade-off:** More complex function signature, but enables rich comparative context.

**Rejected:** Simplifying to only show winner's explanation.
**Reason:** Users need to understand why #2 lost to make informed trade-off decisions.


Ran manual test with 10 niches to verify:
- Normalization still effective with wider score distribution
- Explanation comparisons generate meaningful context
- Sensitivity analysis remains performant (10 niches × 6 criteria × perturbations)

**Observed:** With 10 niches, sensitivity analysis becomes more valuable – more alternatives exist.


## Day 7 – Prompt Parser & Web Interface (Day 4 of focused build)

Built natural language input system and Flask web layer.

**Decision:** Keyword-based parsing with regex, not LLM classification.

**Rationale:**
- Deterministic: Same prompt → same weights (explainable)
- No API dependency or latency
- Transparent logic: Can trace why "coding" boosted skill weight

**Implementation:**
- Goal detection via keyword matching (side_income, long_term, passion)
- Criterion extraction via pattern matching
- Negation handling ("not technical" lowers skill weight)
- Fallback to defaults with validation error if no signals found

**Rejected:** Using LLM to generate weights directly.
**Reason:** Violates core constraint - weights must be explainable and reproducible.

**Endpoints:**
- `POST /api/analyze` - Main decision endpoint
- `GET /api/health` - Status check
- `GET /` - HTML interface

**Design decisions:**
- Parser → Engine → Response pipeline
- JSON API for flexibility (mobile app could use same backend)
- Minimal HTML frontend for demonstration

**Error handling:**
- ValidationError (400) for unparseable prompts
- Generic 500 for processing failures (don't expose internals)

## Day 8 – UI Refinements, Refinement Questions, and Personalization Improvements (March 03, 2026)

Today, focused on addressing UI usability issues and improving recommendation personalization to handle cases where passion/interest mismatches with side_income rankings (e.g., gamer getting finance niches).

**Issue Identification:**
- Dropdowns and analyze button not functioning correctly in some configurations.
- Button enabled even without profession/goal selected, leading to generic recommendations (AI Tools, Personal Finance, Business).
- Refinement questions needed for mismatches (e.g., gaming background but finance #1).
- Interests like "gaming" not having strong enough effect to override profession.

**UI Refinements:**
- Added disable state to "Find My Best Niches" button until profession and goal selected (JS validation).
- Improved tab switching and verification flow for free-form prompt.
- Added score bars, notes, and badges to result cards for clearer visual feedback.

**Refinement Logic Implementation:**
- Added flag in /api/analyze to detect mismatches (side_income goal + non-top predicted niche).
- Created /api/refine endpoint to re-score with user choice (fast/balanced/passion).
- Adjustments:
  - "fast": Keep original.
  - "balanced": Reduce monetization/growth, boost skill/time.
  - "passion": Force predicted niche + strong skill/time boost, reduce money pressure.

**Parser Enhancements:**
- Strengthened interest override: Entering "gaming" now forces Gaming Content as predicted niche + bigger boosts (+6 skill, +5 time, -4 monetization, -3 competition).

**Testing & Observations:**
- With gamer + side_income + "gaming" interest: Gaming now ranks higher (often #1 or #2).
- Refinement question appears on mismatches; selecting "passion" pushes passion niche to top.
- No-input runs prevented; UI feels more robust.

**Rejected:** Making interest override 100% force #1 (too rigid — keeps some balance).
**Reason:** User should still see objective trade-offs.

**Trade-off:** Added one extra user click for mismatches, but improves personalization and satisfaction.
