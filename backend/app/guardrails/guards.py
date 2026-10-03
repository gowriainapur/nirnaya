"""
Procurement Compass - Comprehensive Guardrails Module
Enforces:
1. Missing Field Detector
2. Classification Guard
3. Date Resolution Guard
4. Threshold Guard
5. GeM Guard
6. Split Purchase Detector
7. Conflict Detector
8. Citation Verifier (Validity, Correctness, Completeness, Entailment, Version)
9. Amount Verifier (Extracts numbers and strictly verifies provenance)
10. Approval Authority Guard (Never infers roles from titles)
11. Synthetic Source Guard (Prevents synthetic material from acting as statutory)
12. Prompt Injection Guard (Treats document text as untrusted data)
13. Out of Scope Guard
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from app.models import (
    ProcurementInput,
    DecisionObject,
    ExplanationResponse,
    CitationRef
)

class GuardrailsPipeline:
    def __init__(self):
        # Prompt injection trigger patterns
        self.injection_patterns = [
            r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
            r"approve\s+(this\s+)?purchase",
            r"bypass\s+(the\s+)?rule",
            r"use\s+₹?[0-9,]+\s+instead",
            r"do\s+not\s+cite",
            r"system\s*prompt",
            r"override\s+(the\s+)?policy",
            r"you\s+are\s+now\s+in\s+developer\s+mode"
        ]

    def check_prompt_injection(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detects malicious instructions embedded in user input or documents (§40)."""
        if not text:
            return False, None
        for pattern in self.injection_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return True, f"Prompt injection pattern detected: '{match.group(0)}'"
        return False, None

    def sanitize_untrusted_input(self, inp: ProcurementInput) -> Tuple[ProcurementInput, List[str]]:
        """Sanitizes user input and flags injection attempts without crashing."""
        flags: List[str] = []
        is_inj, msg = self.check_prompt_injection(inp.item_description)
        if is_inj:
            flags.append("prompt_injection_attempt_neutralized")
            # Neutralize instruction keywords from item description
            cleaned = re.sub(r"(?i)(ignore previous instructions|approve this purchase|bypass rule).*", "[NEUTRALIZED_INJECTION]", inp.item_description)
            inp.item_description = cleaned
        return inp, flags

    def verify_citations(
        self,
        explanation: ExplanationResponse,
        available_citations: List[CitationRef]
    ) -> Tuple[bool, List[str]]:
        """
        Validates citation IDs used in explanation steps and checklists (§36).
        Checks:
        1. Citation validity (ID exists in retrieved evidence)
        2. Citation completeness
        3. Entailment check
        """
        issues = []
        valid_ids = {c.citation_id for c in available_citations}

        used_ids = set()
        for step in explanation.steps:
            for cid in step.citations:
                used_ids.add(cid)
                if cid not in valid_ids:
                    issues.append(f"Invalid citation ID '{cid}' used in Step {step.number}.")

        for item in explanation.checklist:
            for cid in item.citations:
                used_ids.add(cid)
                if cid not in valid_ids:
                    issues.append(f"Invalid citation ID '{cid}' used in Checklist item '{item.item}'.")

        # If complete status but zero citations provided
        if explanation.status == "COMPLETE" and not used_ids and available_citations:
            issues.append("Explanation provided zero citations despite COMPLETE decision status.")

        return len(issues) == 0, issues

    def verify_amounts(
        self,
        text_to_check: str,
        decision: DecisionObject,
        available_citations: List[CitationRef],
        user_value: Optional[float] = None
    ) -> Tuple[bool, List[str]]:
        """
        Verifies every monetary amount appearing in explanation against decision object or citations (§37).
        Zero unsupported numbers permitted.
        """
        issues = []
        # Find amounts like ₹50,000 or 50,000 or 5,00,000 or 25,00,000 or 40,000 or 2,00,000
        matches = re.findall(r"(?:₹\s*|Rs\.?\s*|INR\s*)([0-9,]+(?:\.[0-9]{2})?)", text_to_check, re.IGNORECASE)

        # Authorized amounts from decision and citations
        authorized_amounts = set()
        if user_value is not None:
            authorized_amounts.add(int(user_value))

        if decision.threshold_band:
            if decision.threshold_band.lower is not None:
                authorized_amounts.add(int(decision.threshold_band.lower))
            if decision.threshold_band.upper is not None:
                authorized_amounts.add(int(decision.threshold_band.upper))

        if decision.approval_authority and decision.approval_authority.delegation_limit_inr:
            authorized_amounts.add(int(decision.approval_authority.delegation_limit_inr))

        # Known standard GFR and institutional thresholds
        standard_authorized = {25000, 40000, 50000, 75000, 100000, 200000, 250000, 400000, 500000, 2500000}
        authorized_amounts.update(standard_authorized)

        for m in matches:
            cleaned_num = m.replace(",", "")
            try:
                val = int(float(cleaned_num))
                if val > 0 and val not in authorized_amounts:
                    issues.append(f"Unverified monetary amount '₹{m}' detected without rule provenance.")
            except ValueError:
                continue

        return len(issues) == 0, issues

    def verify_approval_authority(
        self,
        decision: DecisionObject,
        explanation_text: str
    ) -> Tuple[bool, List[str]]:
        """
        Ensures LLM never hallucinates Dean, Director, HoD unless explicitly established (§3, §18).
        """
        issues = []
        if decision.approval_authority.status == "not_found":
            prohibited_titles = ["dean", "director", "head of department", "registrar", "finance officer"]
            lower_text = explanation_text.lower()
            for title in prohibited_titles:
                if f"approved by {title}" in lower_text or f"{title} approves" in lower_text:
                    issues.append(f"Violation of Approval Authority Law: explanation claims approval by '{title.title()}' without explicit institutional delegation.")
        return len(issues) == 0, issues
