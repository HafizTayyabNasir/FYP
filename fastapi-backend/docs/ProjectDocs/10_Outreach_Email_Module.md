# 10 — Outreach Email Module (Theory)

## 10.1 Purpose

The outreach module converts:

- business identity (name, industry, location)
- audit findings (scores + flaws)
- extracted business data (optional)

into:

- draft outreach email(s)
- subject line variants

It also supports sending emails via SMTP.

## 10.2 Cold Outreach Fundamentals

### 10.2.1 Objectives of cold outreach
- start a conversation
- earn permission for a call
- offer value without sounding spammy

### 10.2.2 Consultative outreach
Consultative outreach emphasizes:

- diagnosis (audit)
- impact explanation
- solution framing
- soft CTA

This is usually more effective than generic sales copy.

## 10.3 Email Structure Theory

A typical outreach email includes:

1. **Personal opener**: references business and context.
2. **Observation**: highlights 1–3 audit findings.
3. **Impact**: explains consequence in business terms.
4. **Solution**: proposes how to fix.
5. **CTA**: invites short call or reply.
6. **Signature**: name/company.

## 10.4 Subject Line Theory

Subject lines drive open rate.

Patterns:

- personal + specific: “Quick note about {BusinessName} site”
- benefit: “2 fixes to improve bookings from mobile”
- curiosity: “One thing I noticed on your homepage”

Constraints:

- avoid spam words
- keep under ~50 characters when possible

## 10.5 Personalization Depth Levels

### Level 0: generic
- no mention of business
- template feel

### Level 1: shallow
- insert business name

### Level 2: contextual
- mention industry and location

### Level 3: diagnostic
- reference audit findings

### Level 4: strategic
- connect findings to a business goal (calls, bookings)

The project aims at Level 3–4.

## 10.6 Business Impact Translation

Technical issues must be translated:

- “Missing SSL” → “browser warnings reduce trust”
- “Slow load” → “users abandon before booking”
- “Missing metadata” → “less visible in search”
- “Not mobile friendly” → “mobile users struggle to navigate”

This translation is critical to outreach effectiveness.

## 10.7 SMTP Sending Theory

### 10.7.1 SMTP basics
SMTP is a protocol for sending email.

A sending workflow:

- connect to SMTP server
- start TLS
- authenticate
- send MIME message

### 10.7.2 MIME message composition
Emails can include:

- plain-text part
- HTML part

Best practice:

- always include plain-text (deliverability)
- keep HTML simple

### 10.7.3 Deliverability considerations
Deliverability depends on:

- sending domain reputation
- SPF/DKIM/DMARC alignment
- message content
- sending frequency

For a student project, SMTP sending works, but a report should mention deliverability is complex.

### 10.7.4 Rate limiting and throttling
If sending many emails:

- space sends over time
- randomize small delays
- cap per hour/day

This reduces spam flags.

## 10.8 Compliance Considerations

Cold outreach legality varies by country.

Common principles:

- include an opt-out method
- do not send deceptive claims
- contact only relevant businesses

For academic reporting, state that compliance is a responsibility of the user.

## 10.9 Logging and Auditing

Outbound email systems should log:

- recipient
- timestamp
- subject
- status (sent/failed)
- errors (without logging passwords)

This supports debugging and accountability.

## 10.10 Failure Modes

- SMTP credentials missing
- provider blocks sign-in
- network failures
- email rejected

Mitigation:

- clear error messages
- retry for transient errors
- queue sending into background tasks

## 10.11 Future Enhancements

- IMAP sync to track replies
- message templates per industry
- automatic follow-up sequences
- A/B testing for subject lines
- tracking pixels (ethical concerns)

## 10.12 Summary

The outreach module combines audit-driven personalization with SMTP delivery. It is a practical application of AI-assisted business communication grounded in measurable technical signals.
