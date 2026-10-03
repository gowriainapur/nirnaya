"""
Test Suite: Hybrid Retrieval Engine & Benchmark
"""

import pytest
from app.retrieval.retriever import PolicyRetriever
from app.eval.benchmark import EvaluationEngine

@pytest.fixture
def retriever():
    return PolicyRetriever()

@pytest.fixture
def eval_engine():
    return EvaluationEngine()

def test_retriever_loads_corpus(retriever):
    assert len(retriever.chunks) > 0
    assert retriever.bm25 is not None
    assert len(retriever.dense_vectors) == len(retriever.chunks)

def test_bm25_preserves_numbers_and_rule_ref(retriever):
    hits = retriever.search_bm25("Rule 154 without quotation 50,000", top_k=3)
    assert len(hits) > 0
    assert hits[0]["rule_ref"] == "Rule 154"

def test_hybrid_rrf_scoring(retriever):
    hits = retriever.search_hybrid("purchase committee 5,00,000 Rule 155", top_k=3)
    assert len(hits) > 0
    assert "retrieval_score" in hits[0]
    assert hits[0]["retrieval_strategy"] == "hybrid_rrf"

def test_retrieval_benchmark_execution(eval_engine):
    bench = eval_engine.run_retrieval_benchmark()
    assert "bm25" in bench
    assert "dense" in bench
    assert "hybrid" in bench
    # Check that hybrid achieves high Hit@3 and MRR
    assert bench["hybrid"]["hit_at_3"] >= 0.85
    assert bench["hybrid"]["mrr"] >= 0.70
    assert bench["hybrid"]["avg_latency_ms"] < 100.0
