"""
Test Suite: Deterministic Rules Engine & 28 Golden Scenarios
"""

import pytest
from app.models import ProcurementInput
from app.rules_engine.engine import RulesEngine
from app.eval.benchmark import EvaluationEngine, GOLDEN_TEST_CASES

@pytest.fixture
def engine():
    return RulesEngine()

@pytest.fixture
def eval_engine():
    return EvaluationEngine()

def test_golden_cases_all_pass(eval_engine):
    """Verifies that all 28 golden test cases achieve 100% accuracy with 0 false-safe rate (§59, §60)."""
    results = eval_engine.run_golden_suite()
    assert results["passed"] == 28, f"Failed cases: {results['failed_cases']}"
    assert results["failed"] == 0
    assert results["accuracy"] == 1.0
    assert results["false_safe_rate"] == 0.0

def test_exact_threshold_boundary(engine):
    """Test boundary condition at ₹50,000 vs ₹50,001 (§58 case 2 & 3)."""
    inp_50k = ProcurementInput(
        item_description="Precision multimeter",
        category="goods",
        estimated_value_inr=50000.0,
        tax_inclusive=True,
        procurement_date="2026-02-15",
        gem_status="unavailable_verified"
    )
    dec_50k = engine.evaluate(inp_50k, "TEST-B50K")
    assert dec_50k.status == "COMPLETE"
    assert dec_50k.procurement_route == "direct_purchase"

    inp_50001 = ProcurementInput(
        item_description="Precision multimeter",
        category="goods",
        estimated_value_inr=50001.0,
        tax_inclusive=True,
        procurement_date="2026-02-15",
        gem_status="unavailable_verified"
    )
    dec_50001 = engine.evaluate(inp_50001, "TEST-B50001")
    assert dec_50001.status == "COMPLETE"
    assert dec_50001.procurement_route == "purchase_committee"

def test_version_time_machine(engine):
    """Test same purchase on 2023 date vs 2026 date yields different rulesets and routes (§51, §58 case 23 & 24)."""
    inp_historical = ProcurementInput(
        item_description="Oscilloscope probes",
        category="goods",
        estimated_value_inr=40000.0,
        tax_inclusive=True,
        procurement_date="2023-05-10",
        gem_status="unavailable_verified"
    )
    dec_hist = engine.evaluate(inp_historical, "TEST-HIST")
    assert dec_hist.ruleset_used == "gfr_2017_historical_original"
    assert dec_hist.procurement_route == "purchase_committee"  # Historical direct cap was ₹25K!

    inp_current = ProcurementInput(
        item_description="Oscilloscope probes",
        category="goods",
        estimated_value_inr=40000.0,
        tax_inclusive=True,
        procurement_date="2026-02-15",
        gem_status="unavailable_verified"
    )
    dec_curr = engine.evaluate(inp_current, "TEST-CURR")
    assert dec_curr.ruleset_used == "gfr_2017_updated_31_01_2026"
    assert dec_curr.procurement_route == "direct_purchase"  # Current direct cap is ₹50K!

def test_deliberate_conflict_triggers_escalation(engine):
    """Test synthetic deliberate conflict clause triggers immediate ESCALATION (§7, §27)."""
    inp_conflict = ProcurementInput(
        item_description="Lab supplies under synthetic 4.2",
        category="goods",
        estimated_value_inr=65000.0,
        tax_inclusive=True,
        procurement_date="2026-02-15",
        gem_status="search_not_performed",
        institution_policy_loaded=True
    )
    dec = engine.evaluate(inp_conflict, "TEST-CONF")
    assert dec.status == "ESCALATE"
    assert any("POLICY CONFLICT DETECTED" in r for r in dec.escalation_reasons)
