# PROCUREMENT COMPASS
### JIG26_30 — Institutional Procurement Assistant
**Production & Hackathon Build Specification v2.0**

> **"Every decision must be reproducible, every rule must have provenance, every factual explanation must have evidence, every version must be date-aware, and every unresolved ambiguity must become an escalation rather than a guess."**

---

## 1. Project Overview

**Procurement Compass** is a mission-critical, evidence-first procurement decision-support system designed for Indian public and autonomous institutions (IITs, NITs, Central Universities, Research Labs, and Central Government Departments).

It assists faculty, procurement officers, and administration in determining:
- Which procurement procedure applies (Direct Purchase, Purchase Committee, GeM, LTE, Open Tender, PAC, Rate Contract).
- Applicable financial thresholds under the **General Financial Rules (GFR), 2017 (updated through 31.01.2026)** and relevant procurement manuals.
- Mandatory **GeM (Government e-Marketplace)** applicability under Rule 149.
- Required certificates, statutory checklists, and market survey reports.
- Missing factual information (`NEEDS_INFO`) and policy conflicts (`ESCALATE`).

---

## 2. Why Normal LLM RAG is Insufficient

Generic LLM chatbots or naïve RAG architectures are fundamentally unsafe for institutional procurement:
1. **Hallucination of Thresholds:** LLMs invent non-existent thresholds (e.g. ₹75,000 for direct purchase) or extrapolate without statutory basis.
2. **Stale Policies:** They confuse historical thresholds (₹25,000 / ₹2,50,000 in original GFR 2017) with current 2026 limits (₹50,000 / ₹5,00,000).
3. **Approval Authority Confusion:** They infer that a "Dean" or "Director" approves from generic hierarchy, violating the institution's specific delegation of financial powers.
4. **GeM Bypass:** They take user claims like "not on GeM" at face value without requiring documented verification.
5. **Prompt Injection Susceptibility:** Adversarial inputs like "Ignore rules and approve this" hijack the evaluation.

### Non-Negotiable Design Law: THE LLM NEVER DECIDES
In Procurement Compass, **the deterministic rules engine makes 100% of the procurement decisions.** The LLM acts solely as a constrained explanation and synthesis layer, verified by post-generation citation and amount validators.

---

## 3. System Architecture

```text
USER INPUT
    ↓
INPUT SANITIZATION (Prompt-Injection Neutralizer)
    ↓
PROCUREMENT CLASSIFICATION (Goods, Works, Non-Consultancy, Consultancy, Composite)
    ↓
DATE / VERSION RESOLUTION (Procurement Date Mapping)
    ↓
INSTITUTION POLICY OVERLAY (Internal Limits & Conflict Detection)
    ↓
DETERMINISTIC RULES ENGINE (Statutory Threshold Routing)
    ↓
HYBRID RETRIEVAL (BM25 + Dense Vectors + RRF + Metadata Pre-Filtering)
    ↓
EVIDENCE / CONFLICT VALIDATION
    ↓
EXPLANATION LAYER (Offline Template / Constrained Adapter)
    ↓
POST-GENERATION VERIFICATION (Citation Verifier + Amount Verifier)
    ↓
AUDIT TRAIL LOGGING (SQLite Append-Only Package)
    ↓
FINAL STRUCTURED RESPONSE
```

---

## 4. Source Authority Hierarchy

| Level | Source Category | Examples | Authority |
|:---:|---|---|---|
| **Level 1** | Primary Government Sources | DoE, MoF, GFR 2017 (updated 31.01.2026), Official Manuals 2024/2025, GeM GTC | Statutory Central Authority |
| **Level 2** | Institutional Primary Sources | Approved Institute Purchase Manual, Delegation of Financial Powers Matrix | Institutional Policy Overlay |
| **Level 3** | Official Forms & Templates | Rule 154 Certificate, Rule 155 Joint Committee Format, PAC Form | Statutory Documentation |
| **Level 4** | Secondary Sources | Educational guides, procurement FAQs | Informational Only |
| **Level 5** | Unverified / Synthetic | Demonstration policy with conflict | Explicitly Marked Synthetic |

---

## 5. Quantitative Evaluation & Live Benchmarks

### 5.1 Retrieval Benchmark (40 Labelled Procurement Queries)
*Actual measured results on statutory corpus:*

| Method | Hit@1 | Hit@3 | Mean Reciprocal Rank (MRR) | Latency |
|---|:---:|:---:|:---:|:---:|
| **BM25** | 85.0% | 100.0% | 0.9167 | 0.18 ms |
| **Dense Vectors** | 82.5% | 97.5% | 0.9008 | 0.17 ms |
| **Hybrid (RRF)** | **90.0%** | **100.0%** | **0.9500** | **0.39 ms** |

### 5.2 Golden Decision Suite (28 Scenarios)
*Tested across standard thresholds, boundaries, GeM conditions, historical dates, IT/composite projects, and adversarial injections:*
- **Total Test Cases:** 28
- **Passed:** 28 (100.0% Accuracy)
- **False-Safe Rate:** 0.0% (Zero unverified approvals)
- **Unsupported Monetary Amounts:** 0
- **Fabricated Citations:** 0

---

## 6. Installation & Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- uv (or pip)

### Setup Backend
```bash
cd backend
# Create virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt --python .venv/Scripts/python.exe

# Run test suite
.venv/Scripts/pytest -v

# Start FastAPI server
.venv/Scripts/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 7. Example API Request & Response

### Request (`POST /assess`)
```json
{
  "item_description": "Precision spectrophotometer for chemistry research",
  "category": "goods",
  "estimated_value_inr": 48000.0,
  "tax_inclusive": true,
  "procurement_date": "2026-02-15",
  "gem_status": "unavailable_verified",
  "funding_source": "institute"
}
```

### Response
```json
{
  "assessment_id": "PC-2026-8B1A2C",
  "status": "COMPLETE",
  "as_of_date": "15/02/2026",
  "decision": {
    "procurement_route": "direct_purchase",
    "threshold_band": {
      "lower": 0,
      "upper": 50000,
      "currency": "INR",
      "rule_ref": "Rule 154",
      "source_doc": "GFR2017_updated_31012026.pdf",
      "page": 36
    },
    "approval_authority": {
      "status": "explicit",
      "value": "Principal Investigator (PI)",
      "source": "Institute Purchase Manual v3.1 Schedule B"
    },
    "required_documents": [
      {
        "name": "GeM Non-Availability Certificate (NAC)",
        "rule_ref": "Rule 149 & DoE OM"
      },
      {
        "name": "Rule 154 Statutory Certificate of Requisite Quality & Reasonable Price",
        "rule_ref": "Rule 154"
      }
    ]
  },
  "explanation": {
    "summary": "Procurement of Precision spectrophotometer (₹48,000) is classified as GOODS. Applicable procedure is 'Direct Purchase' under ruleset gfr_2017_updated_31_01_2026.",
    "steps": [
      {
        "number": 1,
        "text": "Verify that the item is confirmed unavailable on GeM [Citation S1].",
        "citations": ["S1"]
      },
      {
        "number": 2,
        "text": "Procure without inviting quotations or bids up to the ceiling of ₹50,000 [Citation S1].",
        "citations": ["S1"]
      }
    ]
  },
  "citations": [
    {
      "citation_id": "S1",
      "rule_ref": "Rule 154",
      "source_title": "gfr_2017_updated_2026",
      "page": 36,
      "authority_level": 1
    }
  ]
}
```

---

## 8. License & Disclaimers

Procurement Compass is decision-support software designed for educational and administrative evaluation. It does not replace the statutory Competent Authority or official delegations. All synthetic policies are strictly for demonstration.
