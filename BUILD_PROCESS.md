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

### Morning: Explanation Module Design

I realized the system was calculating scores but not communicating reasoning effectively. The assignment specifically asks to "explain why a particular recommendation was made."

**Design decisions:**
- Structured explanations with: summary, strengths, concerns, risk context, recommendation
- Context-aware messaging (different text for high vs low scores)
- No templated strings – dynamic generation based on actual contributions
- Deterministic logic: same scores always produce same explanations

**Rejected approach:** Using AI/LLM to generate explanations.
**Reason:** Would violate explainability constraint and create non-deterministic outputs.

### Afternoon: Sensitivity Analysis Implementation

This was my "above and beyond" feature. I wanted to answer: *"How confident should the user be in this recommendation?"*

**Algorithm design:**
- Perturb each weight by ±15% across multiple iterations
- Track position stability for each niche
- Calculate variance and most common ranking
- Identify scenarios where a different niche would win

**Key insight:** If small changes in priorities flip the recommendation, the decision is sensitive and requires more user reflection.

**Implementation challenge:** Ensuring perturbations stayed within 1-10 range while maintaining weight ratios.
**Solution:** Clamp individual weights before normalization, not after.

### Evening: Validation & Integration

Added defensive programming:
- `validator.py` with comprehensive input checking
- Custom `ValidationError` for clear error messaging
- Updated `manual_test.py` to demonstrate all features

**Refactoring decision:** Updated niche structure to separate `attributes` from `metadata`.
**Why:** Cleaner separation of concerns – scoring engine only needs attributes, explanation module benefits from metadata.