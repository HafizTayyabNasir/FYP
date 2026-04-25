# 13 — Data Modeling & Storage Layer (Theory + Current State)

## 13.1 Purpose

A storage layer persists:

- discovered businesses
- audit results
- outreach drafts and sent messages
- campaign metadata
- inbox threads

The current project uses JSON files for demo simplicity, while also including placeholders for a more complete DB/repository architecture.

## 13.2 Current Persistence Approach (JSON Files)

### 13.2.1 Why JSON storage is used
For an FYP demo, JSON is useful:

- minimal setup
- easy to inspect
- portable across machines

### 13.2.2 Typical stored entities
- businesses list
- campaigns list
- email threads
- email messages

### 13.2.3 Issues with file-based storage

1. **Concurrent writes**
   - two requests can overwrite each other.

2. **No indexing**
   - listing/filtering requires scanning entire file.

3. **No integrity constraints**
   - cannot enforce uniqueness or relationships.

4. **No schema migrations**
   - changing structure breaks old data.

Mitigations (still file-based):

- file locking
- atomic writes (write temp + rename)
- version fields in records

## 13.3 Conceptual Relational Model

A production database design can be described in your report.

### 13.3.1 Core tables

**Business**
- id (UUID)
- name
- website
- email
- phone
- category
- address
- location
- created_at

**AuditRun**
- id
- business_id (FK)
- website_url
- run_at
- overall_score
- summary

**AuditModuleResult**
- audit_run_id (FK)
- module_name
- score
- flaws (JSON)
- details (JSON)

**Campaign**
- id
- name
- criteria
- status
- created_at

**CampaignLead**
- campaign_id
- business_id
- stage

**OutboundEmail**
- id
- campaign_id
- business_id
- subject
- body
- status
- sent_at

**EmailThread**
- id
- business_id
- subject
- status

**EmailMessage**
- id
- thread_id
- direction
- body
- created_at

### 13.3.2 Normalization discussion
This design is normalized to avoid duplication:

- business details stored once
- audit runs reference business
- module results reference audit run

This is valuable for academic reporting.

## 13.4 Repository Pattern (Theory)

### 13.4.1 What is a repository
A repository abstracts persistence behind an interface:

- `create_business()`
- `list_businesses()`
- `save_audit_run()`

Benefits:

- business logic is not coupled to storage
- easy to swap JSON storage with SQL DB
- easier to test with fake repositories

### 13.4.2 Unit of Work
A Unit of Work pattern coordinates commits:

- begin transaction
- apply changes
- commit/rollback

This is standard in database-backed systems.

## 13.5 Schema Versioning

Audit outputs evolve.

A recommended practice:

- store `schema_version` on audit records
- keep backward compatibility

This supports long-term maintenance.

## 13.6 Data Quality and Cleaning

### 13.6.1 Email validation
Before storing email:

- normalize case
- filter junk
- validate domain

### 13.6.2 Website URL normalization
Store a canonical representation:

- lowercase host
- normalize scheme
- strip trailing slashes

## 13.7 Privacy Considerations

Stored data can be personal data if it includes:

- personal emails
- phone numbers

Therefore:

- define retention policy
- allow deletion
- protect access

## 13.8 Audit Result Storage Strategy

Choices:

- store only latest audit per business
- store audit history

Audit history supports:

- progress tracking
- before/after comparisons
- experiment analysis

## 13.9 Scalability Considerations

As data grows:

- JSON approach becomes slow
- DB indexing becomes necessary

Common indexes:

- businesses by category/city
- audits by timestamp
- outbound emails by status

## 13.10 Summary

The project currently uses JSON for simplicity but is structurally aligned with a more formal persistence design. In your 500-page report, you can describe both the implemented approach and the production-ready relational model as future work.
