import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.abspath('backend'))

from app.models import ProcurementInput
from app.rules_engine.engine import RulesEngine
from app.eval.benchmark import GOLDEN_TEST_CASES

def run_cases():
    engine = RulesEngine()
    
    # Case 2: Exact boundary threshold
    case_boundary = next(c for c in GOLDEN_TEST_CASES if c["id"] == 2)
    res_boundary = engine.evaluate(case_boundary["input"], "test-1")
    
    # Case 7: Missing value
    case_missing = next(c for c in GOLDEN_TEST_CASES if c["id"] == 7)
    res_missing = engine.evaluate(case_missing["input"], "test-2")
    
    print("BOUNDARY CASE RESULTS (ID 2):")
    print(json.dumps(res_boundary.model_dump(), indent=2))
    
    print("\n\nMISSING DETAIL CASE RESULTS (ID 7):")
    print(json.dumps(res_missing.model_dump(), indent=2))

if __name__ == "__main__":
    run_cases()
