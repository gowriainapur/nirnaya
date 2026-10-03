# Procurement Compass — System Architecture

**JIG26_30 — Institutional Procurement Assistant**
**Version:** 2.0 (GFR 2017 updated through 31.01.2026)

---

## 1. Non-Negotiable Core Architecture

The foundational design law of Procurement Compass is:

> **THE LLM NEVER DECIDES.**

The LLM is an **explanation and synthesis layer**, never a policy or decision engine.

```
+------------------------------------------------------------------------+
|                              USER INPUT                                |
| (Item description, category, value, date, GeM status, research flag)   |
+-----------------------------------+-+----------------------------------+
                                    |
                                    v
+-----------------------------------+------------------------------------+
|                    INPUT VALIDATION & SANITIZATION                     |
| - Missing field detector                                               |
| - Prompt-injection neutralizer (adversarial instruction defense)       |
+-----------------------------------+-+----------------------------------+
                                    |
                                    v
+-----------------------------------+------------------------------------+
|                   PROCUREMENT CLASSIFICATION                           |
| - GOODS / WORKS / NON_CONSULTANCY / CONSULTANCY / COMPOSITE            |
| - Signal-based & predominant-purpose analysis                          |
| - IT bespoke vs COTS / cloud resolution                                |
+-----------------------------------+-+----------------------------------+
                                    |
                                    v
+-----------------------------------+------------------------------------+
|                   DATE / VERSION RESOLUTION                            |
| - Resolves applicable statutory framework based on procurement_date    |
| - As-of Date resolution: gfr_2017_historical vs gfr_2017_updated_2026  |
+-----------------------------------+-+----------------------------------+
                                    |
                                    v
+-----------------------------------+------------------------------------+
|                  INSTITUTION POLICY OVERLAY                            |
| - Internal institutional caps (e.g. ₹40,000 direct ceiling)            |
| - Deliberate conflict detection (conflicting local vs central rule)   |
+-----------------------------------+-+----------------------------------+
                                    |
                                    v
+-----------------------------------+------------------------------------+
|                  DETERMINISTIC RULES ENGINE                            |
| - Threshold routing (Rule 154, 155, 161, 162)                          |
| - GeM mandate (Rule 149(i), (ii), (iii))                               |
| - Special scientific research thresholds (₹2L / ₹25L)                  |
| - Split-purchase aggregation detector                                  |
| - Controlled escalation logic                                          |
+-----------------------------------+-+----------------------------------+
                                    |
                                    v
+-----------------------------------+------------------------------------+
|                  HYBRID EVIDENCE RETRIEVAL                             |
| - BM25 lexical search (rule numbers, exact currency amounts)           |
| - Dense semantic vector search                                         |
| - Reciprocal Rank Fusion (RRF) with metadata pre-filtering             |
| - Query decomposition (7 targeted sub-queries)                         |
+-----------------------------------+-+----------------------------------+
                                    |
                                    v
+-----------------------------------+------------------------------------+
|                  EXPLANATION & VERIFICATION LAYER                      |
| - Deterministic template generation (offline guaranteed)               |
| - Post-generation citation verifier (validity, completeness)           |
| - Post-generation amount verifier (zero unsupported numbers)           |
| - Approval authority guard (strict delegation matrix check)            |
+-----------------------------------+-+----------------------------------+
                                    |
                                    v
+-----------------------------------+------------------------------------+
|                      AUDIT TRAIL & RESPONSE                            |
| - SQLite append-only audit record (input hash, decision object)        |
| - Structured JSON API response                                         |
+------------------------------------------------------------------------+
```

---

## 2. Route vs Approval Authority Separation

A mandatory safety rule implemented in Procurement Compass is the strict separation between:
1. `procurement_route` (e.g. `direct_purchase`, `purchase_committee`, `GeM_direct`, `advertised_tender`)
2. `approval_authority` (e.g. `Principal Investigator`, `Dean`, `Director`)

The system **never** infers approval authority from general job titles. Unless an explicit, loaded institutional delegation of financial powers exists for that exact funding source and threshold, the approval authority returns:

```json
{
  "status": "not_found",
  "value": null,
  "note": "Competent Authority — institutional delegation must be verified against approved financial powers."
}
```

---

## 3. Status Semantics

- **`COMPLETE`**: Classification resolved, ruleset resolved, threshold verified, GeM condition established, no source conflict, required documents cited with evidence.
- **`NEEDS_INFO`**: Missing fact that the user can supply (e.g. estimated value, procurement date, GeM status, verified research eligibility).
- **`ESCALATE`**: Source conflict detected, category materially uncertain, emergency declaration, proprietary claim without certified PAC, or out-of-corpus condition.
