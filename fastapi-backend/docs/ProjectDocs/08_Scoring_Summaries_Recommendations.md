# 08 — Scoring, Summaries, Recommendations (Theory)

## 8.1 Purpose

Raw module outputs (scores + flaws) must be converted into:

- overall score
- summary narrative
- prioritized recommendations

This is critical because outreach recipients are non-technical.

## 8.2 Scoring Theory

### 8.2.1 Why score at all
Scores enable:

- quick comparison across prospects
- ranking leads by urgency/opportunity
- tracking improvement over time

### 8.2.2 Interpretable scoring
A score should be:

- bounded
- consistent across modules
- explainable

A 0–5 scale is easy for both technical and non-technical audiences.

### 8.2.3 Calibration pitfalls
If one module is too strict, it dominates.

Mitigation:

- define rubrics
- test on sample websites
- adjust thresholds

### 8.2.4 Weighted scoring (optional)
Some systems use weights:

- SSL/security weighted higher
- performance weighted high for ecommerce

Formula:

$$\text{overall} = \frac{\sum_i w_i s_i}{\sum_i w_i}$$

For an FYP, simple mean is a good baseline; weights can be described as future enhancement.

## 8.3 Summary Generation

### 8.3.1 Goal
A summary is a short explanation of what was found.

A good summary:

- mentions 2–4 most important findings
- uses plain language
- highlights business impact

### 8.3.2 Example structure

- “Your website loads slowly on first request, which can increase bounce rate.”
- “SSL is valid but missing HSTS, which is a best-practice security header.”
- “SEO metadata is incomplete, reducing search visibility.”

### 8.3.3 How to select findings
Selection heuristics:

- pick lowest scoring modules
- pick modules with critical flaws (no HTTPS)
- pick user-facing issues first (mobile, speed)

## 8.4 Recommendation Generation

### 8.4.1 Principles
Recommendations must be:

- actionable
- specific
- prioritized
- aligned with the audit

### 8.4.2 Prioritization strategies

1. **Risk-first**: address security issues before marketing issues.
2. **Impact-first**: address speed and mobile for conversions.
3. **Quick wins**: metadata fixes, redirects, alt tags.

In outreach, a balanced approach is effective:

- show 1 urgent issue
- show 2 high-impact issues
- show 1–2 quick wins

### 8.4.3 Mapping flaws to fixes
Create a mapping table:

- flaw → user impact → recommended fix

Example:

- “Missing meta description” → “lower CTR” → “add unique description per page”
- “HTTP does not redirect to HTTPS” → “users see insecure pages” → “301 redirect + update canonical URLs”

### 8.4.4 Avoiding over-promising
Recommendations should use cautious language:

- “can improve”
- “likely to reduce”

Avoid guarantees (“will increase revenue”).

## 8.5 Reporting Style Guidelines

For business owners:

- avoid jargon (“TTFB” → “server response time”)
- explain outcomes (“fewer bookings/calls”)
- propose a clear plan

For academic reporting:

- include the rubric
- describe thresholds and rationale
- include evaluation examples

## 8.6 Handling Partial Failures

If a module fails, treat it carefully:

- do not accuse the website of being “bad”
- mark it as “could not be evaluated”

In an overall score, you can:

- exclude failed modules from mean
- or include as 0 (harsher)

In this project, module failures are represented with score 0; in a report, explain why and propose improvements.

## 8.7 Recommendation Personalization

Recommendations can be personalized by:

- industry: restaurants prioritize phone/address/hours and booking flows
- location: multi-branch businesses need location pages
- goal: ecommerce focuses on checkout speed and trust badges

This can be automated via AI agents.

## 8.8 Human-in-the-loop Review

Even with automation, a human review improves:

- correctness (avoid false positives)
- tone (avoid aggressive outreach)
- compliance (avoid contacting restricted addresses)

A practical workflow:

- audit → generate draft → user reviews → send.

## 8.9 Summary

This chapter explains how audit module outputs can be turned into meaningful narratives and action plans. This translation layer bridges technical metrics and outreach effectiveness, and it is a key contributor to the project’s real-world value.
