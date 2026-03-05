# Research Log – NicheNavigator

---

## Overview

This document records all external references, AI prompts, and research inputs that influenced the development of this project.

The goal of this log is transparency — not justification.

---
## Day 1 - 2
## 1. Assignment Interpretation

Tool Used:
- ChatGPT

Purpose:
- To better understand the assignment expectations.
- To clarify what “We want to see how you build” implies.

Key Realization:
The assignment prioritizes:
- Clarity of thinking
- System design maturity
- Explainability
- Responsible AI usage

Decision:
Avoid building a fully AI-driven recommendation engine.

---

## 2. Decision Modeling Research

Search Queries:
- “Weighted scoring model decision making”
- “Multi criteria decision analysis simple implementation”
- “Normalization in decision systems maximize minimize”
- “Risk scoring formula example”

Concepts Reviewed:
- Multi-Criteria Decision Analysis (MCDA)
- Weighted Scoring Model
- Analytic Hierarchy Process (AHP)

Accepted:
- Weighted scoring model
- Min-max normalization
- Deterministic scoring logic

Rejected:
- AHP (too complex for scope)
- Machine learning approach (violates explainability constraint)
- Data scraping from YouTube (adds unnecessary dependency)

---

## 3. YouTube Ecosystem Understanding

Sources:
- General knowledge from running my own YouTube channel
- Observations about competition and monetization
- Creator economy discussions

Used To Justify:
- Competition scores
- Monetization assumptions
- Growth potential modeling
- Investment estimation

Note:
No real-time data scraping or external APIs were used.

---

## 4. AI Usage During Development

AI was used for:

- Clarifying architectural structure
- Generating structured documentation templates
- Refining explanation wording
- Reviewing modular design decisions

AI was NOT used for:

- Computing final rankings
- Making scoring decisions
- Determining weights automatically
- Acting as the decision engine

All core logic was implemented manually.

---

## 5. Debugging Assistance

Problem Encountered:
- Python module resolution error:
  ModuleNotFoundError: No module named 'decision_engine'

Resolution:
- Understood execution context issue
- Used module-based execution:
  python -m tests.manual_test
- Ensured clean package structure

AI helped clarify the reason behind the import behavior.

---

## 6. What Was Modified From AI Suggestions

- Simplified some architecture components to avoid overengineering.
- Reduced niche count from broader set to three for better depth.
- Avoided adding unnecessary AI parsing layer initially.
- Refined risk formula weights after manual reasoning.

---

## 7. Reflection on AI Use

AI acted as:
- A thinking partner
- A structuring assistant
- A documentation helper

AI did not replace:
- Logical reasoning
- Architectural decisions
- Scoring implementation

The core system remains deterministic and explainable.

## Day 3-4
### 1. AI Usage 

**Used for:**
- Clarifying sensitivity analysis mathematical approaches
- Reviewing explanation structure for completeness
- Debugging: Clarified Python `copy.deepcopy` necessity for weight mutation

**Not used for:**
- Writing explanation text (manual to ensure consistency)
- Determining stability thresholds (manual reasoning)
- Validation logic (straightforward conditional checks)

**Prompt example:**
> "What are standard methods for sensitivity analysis in multi-criteria decision making? Compare one-at-a-time vs Monte Carlo approaches for a system with 6 criteria and 3 alternatives."

**Response summary:**
- One-at-a-time: Easier to explain, shows individual criterion impact
- Monte Carlo: Better for complex systems, requires probability distributions
- Recommendation: OAT for transparency, Monte Carlo for complex models



## Day 5 

### 1. YouTube Niche Market Research

**AI Prompts Used:**

> "What are the top 10 YouTube niche categories in 2024-2025 with highest creator growth and monetization potential?"

**Response Summary:**
- Finance, AI/Tech, and Business niches showing highest CPM growth
- Lifestyle/Productivity oversaturated but low barrier maintains popularity
- Health/Fitness requires YMYL (Your Money Your Life) compliance awareness
- Book reviews and educational content have longer monetization timelines but steady growth

**Accepted:**
- Finance, Business, Health, Productivity, Book Reviews as viable additions
- CPM estimates: Finance ($8-15), Tech ($5-10), Gaming ($2-5)

> "Analyze competition levels and barrier to entry across YouTube niches: Finance, Creative Design, Health, Productivity, Business, Science Education"

**Response Summary:**
- Finance: High trust barrier, moderate competition (credibility filters)
- Creative Design: Portfolio-based, moderate competition (skill filters)
- Health: High compliance burden, moderate competition (certification expectations)
- Productivity: Low barrier, extreme competition (aesthetic-driven)
- Business: Credibility-dependent, moderate competition (experience required)
- Science: High accuracy requirements, low competition (expertise barrier)

**Applied to scoring:**
- Productivity: Competition 9 (highest), Skill 4 (lowest) – "beginner trap" niche
- Finance: Competition 7, Skill 7 – trust matters more than raw skill
- Science: Competition 5, Skill 9 – expertise barrier filters competition

---

### 2. Explanation Design Research

**Search Queries:**
- "how to explain multi-criteria decision results to users"
- "decision support system output clarity best practices"
- "comparative vs absolute performance feedback"

**Key Findings:**
- Users trust systems more when they see **relative performance** ("better than 80% of alternatives")
- **Trade-off transparency** increases decision confidence (knowing what you give up)
- **Percentile framing** more intuitive than raw scores for non-expert users

**Applied:**
- Added percentile calculation for each criterion
- Included "vs category average" comparisons
- Explicit trade-off identification vs runner-up
- "Swap potential" flag for sensitive rankings

**Rejected:**
- Using LLM to generate personalized explanations
- Reason: Violates deterministic constraint, adds non-explainable layer

---

### 3. Scoring Methodology Validation

**Concern:** With 10 niches, min-max normalization may compress distinctions.

**Analysis:**
- Current range: Competition 5-9, Skill 4-9, Investment 2-8
- Minimum spread maintained: 4-point range on all criteria
- Anchor points preserved: At least one niche at 1-2 and 9-10 for each criterion

**Decision:** Min-max normalization remains appropriate. No change to scoring methodology.

---

### 4. AI Usage 

**Used for:**
- Market research on niche viability and CPM ranges
- Competition analysis across categories
- Explanation design pattern research

**Not used for:**
- Determining specific scores (manual estimation based on research)
- Writing explanation text (manual implementation)
- Any scoring or ranking logic

**Prompt example:**
> "What are typical monetization timelines for YouTube niches: Finance, Productivity, Book Reviews, Science Education? Compare to Tech/Gaming baselines."

**Response applied:**
- Finance: 12-18 months (faster than average due to high CPM)
- Productivity: 18-24 months (slower due to competition)
- Book Reviews: 24-30 months (longest, audience building slow)
- Science: 18-24 months (steady but not viral)

**Modified from AI output:**
- Adjusted timelines based on personal creator experience
- Added 3-month buffer for "realistic expectations" vs "optimistic potential"


## Day 6

### 1. NLP Approach Selection

**AI Prompts Used:**

> "Compare approaches for extracting structured data from natural language: keyword extraction vs LLM classification vs rule-based parsing. Focus on determinism and explainability."

**Response Summary:**
- **Keyword extraction:** Fast, deterministic, transparent logic. Limited nuance.
- **LLM classification:** Handles ambiguity, contextual understanding. Non-deterministic, API-dependent.
- **Hybrid:** LLM for intent, rules for extraction. Complexity trade-off.

**Decision:** Pure keyword extraction with regex patterns.

**Rationale alignment:** Assignment requires explainability. LLM classification is a black box even if weights are applied correctly after.

---

### 2. Prompt Pattern Research

**Search Queries:**
- "natural language preference extraction patterns"
- "how users describe priorities in text"
- "negation detection in keyword matching"

**Applied Patterns:**
- Explicit values: "5 hours per day" → time weight boost
- Implicit priorities: "good at coding" → skill weight boost
- Negation: "not technical" → skill weight reduction
- Goal keywords: "side income", "passion project", "career"

---

### 3. Flask Architecture

**Reference:** Flask official documentation, API design patterns.

**Decisions:**
- Stateless API (no session storage)
- JSON in/out for machine readability
- Separate template for human interface
- CORS-ready for future frontend separation

---

### 4. AI Usage – Day 4

**Used for:**
- Researching NLP approach trade-offs
- Identifying common prompt patterns for priority expression
- Flask best practices confirmation

**Not used for:**
- Parser implementation (manual keyword logic)
- API endpoint logic
- Any scoring or ranking

**Prompt example:**
> "What are common ways users express 'I don't have much time' or 'I want to make money' in natural language? List variations."

**Response applied:**
- Time constraints: "limited time", "busy", "part time", "no time"
- Monetization: "side income", "extra money", "passive income", "earn"

---

### 5. Research Reflection

**Boundary maintained:** AI informs design choices, never executes decisions.

Parser is **peripheral layer** by design. Core engine untouched.


## Day 7

**Search Queries:**
- "UX best practices for recommendation systems refinement questions"
- "Progressive disclosure in decision tools UI"
- "How to disable button until form fields filled JS"
- "Explaining mismatches in recommendation UIs (e.g., Netflix-style 'why this?')"
- "CSS for progress bars and card layouts in Flask templates"

**References:**
- Nielsen Norman Group (NNGroup): Articles on progressive disclosure and personalization in UIs.
- Baymard Institute: Studies on form validation and disabled buttons to prevent errors.
- Material Design guidelines: For card layouts, score bars, and radio buttons in refinement sections.
- UX Matters: On explaining recommendations to build trust (e.g., "why not X?" notes).

**Applied:**
- Disabled analyze button until profession/goal selected (JS event listeners).
- Refinement questions for mismatches (radio options for fast/balanced/passion).
- Notes in UI for transparency (e.g., "This ranked high due to side-income potential, but doesn't match background").
- Score bars (simple CSS) for visual feedback.

**Rejected:**
- Full multi-step wizard form (too complex for scope).
- Reason: Keep initial input simple; refinement only when needed.

**AI Usage:**
- Used Grok to generate code snippets for JS validation and refinement logic.
- Not used for core scoring — only UI generation.

**Prompt example:**
> "Give complete index.html code with disable state for button if options not selected, and refinement section after results."

**Response applied:**
- Integrated UI code with tweaks for Flask/Jinja compatibility.
- Ensured no AI in decision logic; only for code structuring.

## Day 8 – UI Best Practices, Refinement Patterns, and Decision Companion Research (March 05, 2026)

**Search Queries:**
- "UX patterns for recommendation refinement questions"
- "Progressive disclosure in decision support tools"
- "How to disable form submit button until required fields filled JavaScript"
- "Explaining recommendation mismatches in UI (Netflix, Spotify examples)"
- "Multi-criteria decision making UI examples with user-defined options"

**References:**
- Nielsen Norman Group (NN/g): "Progressive Disclosure" – show refinement only when mismatch detected
- Baymard Institute: Form validation – disable submit until required fields (profession + goal) filled
- Material Design / Carbon Design: Card layouts, radio groups, progress bars for scoring
- UX Collective / Smashing Magazine: "Why this recommendation?" notes to build trust

**Applied:**
- Disabled analyze button until profession + goal selected (JS change event listeners)
- Refinement radio buttons (fast/balanced/passion) + re-scoring endpoint
- Score progress bars + color-coded notes for transparency
- Stronger interest override in parser (force niche + big weight shifts)

**AI Usage:**
- Used Grok to generate/refine JS for button disable + refinement UI block
- Not used for core scoring logic, weight adjustments, or niche attributes

**Prompt examples:**
- "Complete index.html with button disabled until profession and goal selected + refinement section after results"
- "How to make interests field override predicted niche and apply strong skill/time boosts in Python parser"

**Reflection:**
- Shifted from "recommend top 3" to "evaluate user niches" mindset
- UI now feels more like a companion (asks user to clarify intent when mismatch occurs)


