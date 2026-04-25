# 12 — Mail Threads / Chat Inbox (Theory)

## 12.1 Purpose

The inbox module models outbound and inbound communications as **threads** and **messages**.

Why this matters:

- outreach is not just sending; it is conversation management
- threads allow a CRM-like workflow

The current codebase includes file-based storage for:

- `email_threads.json`
- `email_messages.json`

## 12.2 Threading Model Theory

### 12.2.1 Conversation thread
A thread groups messages by:

- recipient
- subject
- reply chain

In email protocols, a real thread uses headers:

- Message-ID
- In-Reply-To
- References

A simplified model can still provide useful UI grouping.

### 12.2.2 Message direction
Messages can be:

- outbound (sent by the system)
- inbound (received)

Direction is useful for UI display and stats.

## 12.3 State and Status

### 12.3.1 Thread status
Common states:

- active
- archived
- starred

### 12.3.2 Message status
Outbound message states:

- pending
- queued
- sent
- failed

In production, status can include delivery confirmations.

## 12.4 Storage and Querying

A file-based inbox is simple but has limitations:

- concurrency issues on write
- slow searching at scale

A database model would support:

- indexing by recipient
- filtering by status
- full-text search

## 12.5 IMAP Sync (Theory)

### 12.5.1 Why IMAP
IMAP allows reading email from a mailbox.

It can be used to:

- fetch replies
- detect bounces
- update thread status automatically

### 12.5.2 Challenges
- OAuth requirements for some providers
- mailbox quotas
- parsing MIME messages

### 12.5.3 Message parsing
Parsing email involves:

- decoding headers
- handling HTML/plain parts
- extracting quoted text

A robust parser is needed.

## 12.6 Security Considerations

- store IMAP credentials securely
- avoid logging message bodies
- protect inbox endpoints behind authentication

## 12.7 Basic Analytics

Thread and message counts can indicate:

- outreach volume
- failure rate
- inbound response volume

More advanced analysis:

- reply classification (positive/negative)
- sentiment analysis

## 12.8 Human Workflow

A typical workflow:

- send initial email
- wait for reply
- reply from thread
- archive when resolved

This aligns with CRM interaction patterns.

## 12.9 Failure Modes

- SMTP send succeeded but thread not updated (storage error)
- message duplicates due to retries
- missing inbound sync

Mitigations:

- transactional persistence
- idempotency keys
- background IMAP sync

## 12.10 Summary

Threads and messages provide the minimal communication layer needed for outreach operations. Even with simplified storage, the design is grounded in standard email threading concepts and can be expanded into full mailbox synchronization.
