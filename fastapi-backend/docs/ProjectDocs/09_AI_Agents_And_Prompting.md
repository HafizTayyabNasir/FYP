# 09 — AI Agents and Prompting (Theory)

## 9.1 Purpose

AI agents in this project are used for:

- generating outreach emails from structured audit findings
- extracting business details from website content

The system combines deterministic analysis (audits) with generative writing.

## 9.2 What is an “Agent” in this context

In modern AI engineering, an “agent” is often:

- a wrapper around an LLM
- with a system prompt (instructions)
- input data preparation
- output parsing/validation
- optional tools (HTTP fetch, retrieval, etc.)

In this project, agents behave more like:

- specialized prompt templates + provider calls.

## 9.3 Why Use LLMs for Outreach

Outreach writing requires:

- tone control (professional but human)
- personalization (industry, location, business goal)
- transforming technical issues into business language

Rule-based templates struggle to stay natural across many industries.

LLMs can:

- synthesize context
- vary phrasing
- produce readable drafts quickly

## 9.4 Prompt Engineering Foundations

### 9.4.1 System vs user messages
- **System message** sets role and constraints.
- **User message** provides the task and data.

### 9.4.2 Prompt invariants
To ensure predictable outputs, prompts should:

- specify exact output format
- include examples (few-shot) if needed
- forbid spam words and manipulative claims
- define tone and length constraints

### 9.4.3 Structured inputs
Provide inputs in structured form:

- business_name
- website_url
- scores (0–5)
- list of specific issues
- industry, location, target audience

This is a key engineering step: the LLM’s quality depends heavily on the quality of structured context.

## 9.5 Output Contract Design

### 9.5.1 Why output contracts matter
Without strict format constraints, LLM outputs can:

- omit key info
- change formatting unpredictably
- include disallowed content

Define a contract:

- 3 subject lines
- 1 email body
- optional follow-up question if data missing

### 9.5.2 Parsing and validation
Validation strategies:

- regex checks (subject count)
- length checks
- profanity/spam word filters
- ensure the email references provided website

If validation fails:

- re-prompt with corrections
- or show user a warning

## 9.6 Personalization Strategy

### 9.6.1 What personalization means
Personalization is not inserting a name; it is selecting *relevant details*:

- industry-specific pain points
- localized language (city/service area)
- business goal alignment

### 9.6.2 Using audit findings
Examples of personalization from audit findings:

- missing SSL → “customers may see security warnings”
- slow load → “users leave before menu loads”
- missing social links → “harder to validate brand trust”

### 9.6.3 Using extracted business data
Extraction can provide:

- services offered
- pricing cues
- target audience
- unique selling points

This can be blended into the outreach narrative.

## 9.7 LLM Provider Abstraction

A production system should isolate provider differences:

- OpenAI / Groq / others
- different model names
- different rate limits

A provider adapter should manage:

- API keys
- request building
- retries and backoff
- response parsing

The project settings include keys for multiple providers, suggesting intent to support multiple LLMs.

## 9.8 Safety and Compliance (Email Generation)

### 9.8.1 Avoiding deceptive claims
The agent should not:

- guarantee outcomes
- claim it has accessed private analytics
- state false facts

### 9.8.2 Avoiding spam patterns
Spam-like signals include:

- excessive punctuation
- aggressive urgency
- “free money” promises

Prompts should explicitly forbid them.

### 9.8.3 Handling sensitive information
The model should not generate:

- personal data beyond what is provided
- credential-like strings

## 9.9 Human-in-the-loop and Editing

Even with good prompting:

- human review is recommended before sending
- editing improves relevance and reduces risk

In a report, describe why human-in-the-loop is important.

## 9.10 Evaluation of AI Outputs

Evaluation methods:

- human rating of relevance, tone, clarity
- A/B testing subject lines (future work)
- compliance checks (spam terms)

A simple rubric:

- personalization (0–5)
- professionalism (0–5)
- clarity of offer (0–5)
- appropriate call-to-action (0–5)

## 9.11 Failure Modes

- hallucination (inventing facts)
- repetitive templates
- incorrect tone
- missing required fields

Mitigations:

- strict prompts
- provide structured inputs
- validation + re-try

## 9.12 Research Discussion (Academic framing)

This project illustrates an applied research approach:

- deterministic measurement (audits)
- generative communication (LLM)
- pipeline design for business outcomes

You can frame it as:

- “AI-assisted sales enablement”
- “personalized outreach generation from website quality signals”

## 9.13 Summary

AI agents transform audit outputs into human-style outreach messages. Prompt engineering, provider abstraction, and validation are key engineering disciplines to ensure outputs are safe, useful, and consistent.
