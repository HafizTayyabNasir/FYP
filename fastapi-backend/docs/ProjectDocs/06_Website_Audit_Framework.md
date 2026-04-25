# 06 — Website Audit Framework (Theory + Orchestrator Design)

## 6.1 Purpose

A website audit is used to quantify the quality of a business website and identify improvement opportunities that can be explained in outreach.

The project’s audit framework produces:

- module scores (0–5)
- flaws (human-readable issues)
- an overall score
- summary and recommendations

## 6.2 Why Auditing Supports Outreach

Audit findings provide:

- **specificity**: avoid generic outreach templates
- **credibility**: concrete evidence (“missing meta description”, “slow response time”)
- **business impact**: tie technical issues to lost customers

This aligns with consultative selling strategies:

- diagnose → explain impact → propose solution → call-to-action.

## 6.3 Audit Categories (Common Industry View)

A modern web quality audit often includes:

- SEO foundations
- performance and user experience
- security / HTTPS
- accessibility
- best practices (headers, caching, compression)

This project focuses on a subset that is explainable and can be computed quickly.

## 6.4 Modular Audit Architecture

### 6.4.1 Module interface (conceptual)
Each audit module should follow a consistent contract:

- Input: URL (and sometimes fetched HTML)
- Output:
  - score (0–5)
  - flaws list
  - optional structured details

This allows the orchestrator to:

- run modules in parallel,
- aggregate results,
- compute overall score.

### 6.4.2 Benefits

- extensibility: add modules without rewriting orchestrator
- isolation: bugs in one module don’t break entire audit
- comparability: same score scale across modules

## 6.5 Orchestrator Theory

An orchestrator is a coordinator that:

1. normalizes input URL
2. schedules module tasks (often parallel)
3. collects results with timeouts
4. converts results into standardized response schema

The orchestrator should be deterministic:

- same input should produce similar outputs (network variability accepted)

## 6.6 Parallel Execution

### 6.6.1 Why parallelize
Audit modules are mostly network/IO bound:

- fetching HTML
- DNS and TLS handshakes

Running them sequentially increases latency.

### 6.6.2 Thread pools
A `ThreadPoolExecutor` is suitable when using synchronous libraries.

Key design points:

- limit `max_workers`
- set per-task timeouts
- isolate exceptions per module

## 6.7 URL Normalization

### 6.7.1 Problem
Users enter URLs in multiple forms:

- `example.com`
- `http://example.com`
- `https://www.example.com/`

### 6.7.2 Solution
Normalize to a canonical scheme:

- default to `https://`
- strip whitespace
- ensure non-empty

This avoids duplication and audit failures.

## 6.8 Scoring Scale (0–5)

### 6.8.1 Why 0–5
A 0–5 scale is:

- simple to interpret
- matches star-rating mental model
- good for UI display

### 6.8.2 Calibration
To keep module scores comparable, each module should define:

- what constitutes a 5 (excellent)
- what constitutes a 0 (critical failure)

In the report, include the rubric for each module.

## 6.9 Result Aggregation

### 6.9.1 Overall score
Common aggregations:

- arithmetic mean
- weighted mean
- min-score emphasis (security-critical)

This project uses simple averaging in the orchestrator.

### 6.9.2 Recommendations
Recommendations can be derived from:

- module flaws
- known best practices
- prioritization rules

A useful approach:

- generate 3–8 recommendations that are actionable and business-friendly.

## 6.10 Output Design

### 6.10.1 Human and machine readability
The output should serve two audiences:

- UI/user: summary + recommendations
- internal automation: structured module fields

A good schema design is:

- stable fields for UI
- optional details for debugging

## 6.11 Audit Validity and Limitations

### 6.11.1 Heuristic nature
Many checks are heuristics, not authoritative standards.

Example:

- checking presence of viewport meta tag suggests mobile friendliness, but doesn’t guarantee good mobile UX.

### 6.11.2 Network variability
Performance checks vary due to:

- server load
- location
- caching

To reduce noise:

- run multiple samples,
- use median,
- or rely on PageSpeed API (future improvement).

## 6.12 Ethical Considerations

Audits are passive checks (HTTP requests) but still:

- generate traffic
- can be interpreted as scanning

Ensure:

- bounded timeouts
- limited frequency
- avoid aggressive crawling

## 6.13 Future Module Ideas

- Accessibility: alt attributes, ARIA, contrast
- Security headers: CSP, X-Frame-Options
- Technology stack detection
- Sitemap and robots.txt analysis
- Broken links and 404 scanning
- Core Web Vitals via PageSpeed

## 6.14 Summary

The audit framework is a modular, parallelized system that converts a website into interpretable scores and issue lists. This enables data-driven outreach and provides measurable project outputs suitable for academic evaluation.
