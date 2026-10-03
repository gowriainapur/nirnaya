"""
Procurement Compass - FastAPI Main Application
Evidence-first, deterministic, version-aware procurement decision-support system.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.models import (
    ProcurementInput,
    AssessmentResponse,
    CitationRef,
    SourceDocument
)
from app.rules_engine.engine import RulesEngine
from app.retrieval.retriever import PolicyRetriever
from app.generation.generator import ExplanationGenerator
from app.guardrails.guards import GuardrailsPipeline
from app.audit.audit_store import AuditStore
from app.eval.benchmark import EvaluationEngine

app = FastAPI(
    title="Procurement Compass API",
    description="Institutional Procurement Decision-Support System (GFR 2017 updated through 31.01.2026)",
    version="2.0.0"
)

# Enable CORS for local Vite development & demonstration UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core engine singletons
rules_engine = RulesEngine()
retriever = PolicyRetriever()
generator = ExplanationGenerator()
guardrails = GuardrailsPipeline()
audit_store = AuditStore()
eval_engine = EvaluationEngine()

@app.get("/api/health")
def get_health():
    """Health check endpoint exposing runtime metadata and corpus state."""
    return {
        "status": "healthy",
        "service": "Procurement Compass",
        "version": "2.0.0",
        "current_ruleset": "gfr_2017_updated_31_01_2026",
        "sources_count": len(rules_engine.sources_data),
        "policy_chunks_count": len(retriever.chunks),
        "golden_test_cases_count": 28,
        "benchmark_queries_count": 40,
        "as_of_time": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/api/sources", response_model=List[Dict[str, Any]])
def get_sources():
    """Returns the complete authoritative source register with hierarchy levels."""
    return rules_engine.sources_data

@app.get("/api/rulesets")
def get_rulesets():
    """Returns the list of version-aware rulesets and effective dates."""
    return rules_engine.rulesets_data

class SearchRequest(BaseModel):
    query: str
    mode: str = "hybrid"  # "bm25", "dense", "hybrid"
    top_k: int = 5
    category: Optional[str] = None
    procurement_date: Optional[str] = None
    allow_synthetic: bool = True

@app.post("/api/search")
def search_corpus(req: SearchRequest):
    """Executes filtered retrieval across the policy corpus."""
    filters = {
        "category": req.category,
        "procurement_date": req.procurement_date,
        "allow_synthetic": req.allow_synthetic
    }
    if req.mode == "bm25":
        results = retriever.search_bm25(req.query, top_k=req.top_k, **filters)
    elif req.mode == "dense":
        results = retriever.search_dense(req.query, top_k=req.top_k, **filters)
    else:
        results = retriever.search_hybrid(req.query, top_k=req.top_k, **filters)
    return {
        "query": req.query,
        "mode": req.mode,
        "results_count": len(results),
        "results": results
    }

@app.post("/api/assess", response_model=AssessmentResponse)
def assess_procurement(inp: ProcurementInput):
    """Full deterministic assessment pipeline with guardrails, retrieval, and verification."""
    assessment_id = f"PC-{datetime.utcnow().strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"

    # 1. Sanitize untrusted input against prompt injections
    clean_inp, inj_flags = guardrails.sanitize_untrusted_input(inp)

    # 2. Run deterministic rules engine
    decision = rules_engine.evaluate(clean_inp, assessment_id)
    if inj_flags:
        decision.flags.extend(inj_flags)

    # 3. Retrieve supporting statutory evidence
    category_for_retrieval = decision.procurement_classification.category.lower()
    retrieved_chunks = retriever.retrieve_for_assessment(
        item_description=clean_inp.item_description,
        procurement_route=decision.procurement_route,
        category=category_for_retrieval,
        procurement_date=clean_inp.procurement_date,
        top_k=4
    )

    # 4. Map into formal CitationRef objects
    citations: List[CitationRef] = []
    chunk_ids = []
    for idx, c in enumerate(retrieved_chunks, 1):
        cid = f"S{idx}"
        chunk_ids.append(c["chunk_id"])
        citations.append(CitationRef(
            citation_id=cid,
            rule_ref=c.get("rule_ref", "Statutory Rule"),
            source_title=c.get("doc_id", "Official Source"),
            source_version=c.get("version", "Current"),
            page=c.get("page"),
            authority_level=c.get("authority_level", 1),
            is_synthetic=c.get("is_synthetic", False),
            excerpt=c.get("text", "")[:350] + "..."
        ))

    # 5. Generate verified procedural explanation
    explanation, verification_record = generator.generate(clean_inp, decision, citations)

    # 6. Save append-only audit trail package
    audit_store.save_record(
        assessment_id=assessment_id,
        procurement_date=clean_inp.procurement_date,
        user_input=clean_inp.model_dump(),
        ruleset_version=decision.ruleset_used,
        classification=decision.procurement_classification.category,
        route=decision.procurement_route,
        status=decision.status,
        decision_object=decision.model_dump(),
        retrieval_mode="hybrid_decomposed",
        retrieved_chunk_ids=chunk_ids,
        verification_result=verification_record,
        generation_backend="deterministic_verified"
    )

    proc_date_str = clean_inp.procurement_date or "Unspecified"
    try:
        as_of_fmt = datetime.strptime(clean_inp.procurement_date, "%Y-%m-%d").strftime("%d/%m/%Y") if clean_inp.procurement_date else "N/A"
    except Exception:
        as_of_fmt = proc_date_str

    return AssessmentResponse(
        assessment_id=assessment_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
        procurement_date=proc_date_str,
        as_of_date=as_of_fmt,
        decision=decision,
        explanation=explanation,
        citations=citations,
        audit={
            "assessment_id": assessment_id,
            "input_hash": audit_store.compute_input_hash(clean_inp.model_dump()),
            "ruleset_used": decision.ruleset_used,
            "retrieval_mode": "hybrid_decomposed",
            "chunks_count": len(retrieved_chunks)
        },
        verification=verification_record
    )

class WhatIfRequest(BaseModel):
    base_input: ProcurementInput
    variations: Dict[str, Any]

@app.post("/api/what-if")
def simulate_what_if(req: WhatIfRequest):
    """Simulates controlled variations on a procurement input deterministically (§52)."""
    base_dict = req.base_input.model_dump()
    sim_results = []

    # Run base
    base_id = "WHATIF-BASE"
    base_dec = rules_engine.evaluate(req.base_input, base_id)
    sim_results.append({
        "scenario": "Baseline",
        "changed_parameter": "None",
        "value": None,
        "status": base_dec.status,
        "route": base_dec.procurement_route,
        "threshold_upper": base_dec.threshold_band.upper if base_dec.threshold_band else None,
        "ruleset_used": base_dec.ruleset_used
    })

    # Run each variation
    for param, val in req.variations.items():
        mod_dict = dict(base_dict)
        mod_dict[param] = val
        mod_input = ProcurementInput(**mod_dict)
        mod_id = f"WHATIF-{param.upper()}"
        mod_dec = rules_engine.evaluate(mod_input, mod_id)
        sim_results.append({
            "scenario": f"Variation: {param}",
            "changed_parameter": param,
            "value": str(val),
            "status": mod_dec.status,
            "route": mod_dec.procurement_route,
            "threshold_upper": mod_dec.threshold_band.upper if mod_dec.threshold_band else None,
            "ruleset_used": mod_dec.ruleset_used
        })

    return {
        "assessment_id": base_id,
        "simulation_count": len(sim_results),
        "results": sim_results
    }

class PolicyCompareRequest(BaseModel):
    ruleset_a: str = "gfr_2017_historical_original"
    ruleset_b: str = "gfr_2017_updated_31_01_2026"

@app.post("/api/compare")
def compare_policies(req: PolicyCompareRequest):
    """Compares two policy frameworks and shows exact threshold shifts and citations (§51, §57)."""
    diff_table = [
        {
            "parameter": "Rule 154 Direct Purchase without Quotation (Goods)",
            "ruleset_a_value": "₹25,000",
            "ruleset_a_ref": "GFR 2017 Original Rule 154 (p.34)",
            "ruleset_b_value": "₹50,000",
            "ruleset_b_ref": "GFR 2017 Updated 31.01.2026 Rule 154 (p.36)",
            "change_type": "THRESHOLD_INCREASED",
            "delta": "+₹25,000 (+100%)"
        },
        {
            "parameter": "Rule 155 Purchase Committee Limit (Goods)",
            "ruleset_a_value": "₹2,50,000",
            "ruleset_a_ref": "GFR 2017 Original Rule 155 (p.35)",
            "ruleset_b_value": "₹5,00,000",
            "ruleset_b_ref": "GFR 2017 Updated 31.01.2026 Rule 155 (p.36)",
            "change_type": "THRESHOLD_INCREASED",
            "delta": "+₹2,50,000 (+100%)"
        },
        {
            "parameter": "Special Scientific Research Rule 154 Threshold",
            "ruleset_a_value": "Not Available (Standard ₹25K)",
            "ruleset_a_ref": "None",
            "ruleset_b_value": "₹2,00,000",
            "ruleset_b_ref": "DoE OM Scientific Thresholds 2024 (p.2)",
            "change_type": "SPECIAL_PROVISION_ADDED",
            "delta": "+₹1,50,000 over standard"
        },
        {
            "parameter": "Special Scientific Research Rule 155 Committee Threshold",
            "ruleset_a_value": "Not Available (Standard ₹2.5L)",
            "ruleset_a_ref": "None",
            "ruleset_b_value": "₹25,00,000",
            "ruleset_b_ref": "DoE OM Scientific Thresholds 2024 (p.3)",
            "change_type": "SPECIAL_PROVISION_ADDED",
            "delta": "+₹20,00,000 over standard"
        },
        {
            "parameter": "GeM Rule 149 Procurement Mandate",
            "ruleset_a_value": "Optional / Initial Rollout",
            "ruleset_a_ref": "GFR 2017 Early Circulars",
            "ruleset_b_value": "Mandatory across 3 distinct price tiers",
            "ruleset_b_ref": "GFR 2017 Rule 149 & GeM GTC v4.0",
            "change_type": "STATUTORY_MANDATE_STRENGTHENED",
            "delta": "Offline purchase prohibited without NAC"
        }
    ]
    return {
        "ruleset_a": req.ruleset_a,
        "ruleset_b": req.ruleset_b,
        "diff_count": len(diff_table),
        "comparison": diff_table
    }

@app.post("/api/eval")
def run_evaluation():
    """Executes full evaluation: 28 golden cases + 40-query retrieval benchmark (§32, §58)."""
    retrieval_benchmark = eval_engine.run_retrieval_benchmark()
    golden_test_results = eval_engine.run_golden_suite()
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "retrieval_benchmark": retrieval_benchmark,
        "golden_test_results": golden_test_results
    }

@app.get("/api/audit")
def get_audit_trail(limit: int = Query(default=20, ge=1, le=100)):
    """Retrieves immutable audit records from SQLite."""
    records = audit_store.get_records(limit=limit)
    return {
        "total_returned": len(records),
        "records": records
    }

@app.get("/api/decision/{assessment_id}")
def get_decision(assessment_id: str):
    """Retrieves specific assessment package by ID."""
    rec = audit_store.get_by_id(assessment_id)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Assessment ID {assessment_id} not found.")
    return rec

# Mount built frontend static assets if available
from fastapi.staticfiles import StaticFiles
from pathlib import Path
FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")
