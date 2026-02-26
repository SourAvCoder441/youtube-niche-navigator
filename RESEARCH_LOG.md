# Research Log – NicheNavigator

---

## Overview

This document records all external references, AI prompts, and research inputs that influenced the development of this project.

The goal of this log is transparency — not justification.

---

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