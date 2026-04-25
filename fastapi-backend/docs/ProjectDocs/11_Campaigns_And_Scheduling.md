# 11 — Campaigns and Scheduling (Theory)

## 11.1 Purpose

A campaign groups outreach efforts so the user can:

- organize prospects by theme (industry, city)
- control sending schedules
- monitor progress

The codebase currently includes file-based campaign storage and endpoint support.

## 11.2 Campaign Concepts

### 11.2.1 Campaign definition
A campaign is a set of leads plus outreach configuration:

- campaign name and description
- target business type
- target city/country
- status: draft/active/paused
- metrics: sent/opened/replied/bounced

### 11.2.2 Benefits
- batch planning
- repeatable outreach strategy
- easier reporting

In academic terms, campaigns provide experimental grouping for evaluation.

## 11.3 Campaign Lifecycle

### 11.3.1 Draft
- leads can be added
- email templates/agent configuration can be tuned

### 11.3.2 Active
- scheduler sends messages gradually
- throttling rules apply

### 11.3.3 Paused
- sending stops
- analysis can continue

### 11.3.4 Completed
- no more sends
- results archived

## 11.4 Scheduling Theory

### 11.4.1 Why schedule
Sending many emails at once is risky:

- triggers spam detection
- violates provider limits
- causes operational errors

Scheduling spreads sending.

### 11.4.2 Time windows
A scheduler can send within windows:

- business hours
- weekdays

This improves open probability.

### 11.4.3 Randomized jitter
Add small random delays:

- avoids robotic patterns

## 11.5 Throttling Theory

Throttling limits outbound messages:

- per minute
- per hour
- per day

Rules can incorporate:

- domain-level throttling (avoid blasting one domain)
- per-campaign caps

A simple strategy:

- max 10 emails/hour
- max 50 emails/day

These are examples; actual limits depend on SMTP provider.

## 11.6 Queue-Based Sending Architecture

### 11.6.1 Producer-consumer model
- producer: campaign scheduler enqueues tasks
- consumer: worker sends emails

This improves:

- reliability
- retries
- monitoring

Celery is commonly used for this.

### 11.6.2 Idempotency keys
When retrying sends, avoid duplicates using:

- unique message IDs
- record of “already sent”

## 11.7 Metrics and Analytics

### 11.7.1 Basic metrics
- sent count
- failure count
- bounce count

### 11.7.2 Open/reply tracking
Open tracking often requires:

- tracking pixel
- link tracking

Reply tracking requires:

- IMAP mailbox sync

These are typically advanced features.

### 11.7.3 Academic evaluation
You can evaluate:

- open rate
- reply rate
- response sentiment

Ethical note:

- disclose tracking if required by law.

## 11.8 Data Model (Conceptual)

A production model includes:

- Campaign
- CampaignLead (join table)
- OutboundEmail
- DeliveryEvent

Relations:

- Campaign has many leads
- Lead can belong to multiple campaigns

## 11.9 Error Handling

- SMTP send failure triggers retry
- repeated failures mark lead as “failed”
- invalid email marks lead “unreachable”

## 11.10 Future Enhancements

- segmentation by score thresholds
- auto-prioritize worst websites
- multi-step sequences (follow-ups)
- A/B testing prompts

## 11.11 Summary

Campaigns and scheduling provide the operational framework for outreach at scale. Even with a simple file-based implementation, the theoretical design supports strong academic discussion around queueing, throttling, and evaluation.
