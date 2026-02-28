# Research Log – NicheNavigator

---

## Overview

This document records all external references, AI prompts, and research inputs that influenced the development of this project.

The goal of this log is transparency — not justification.

---
## Day 1
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

## Day 2
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



## Day 3 

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




