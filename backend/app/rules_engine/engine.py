"""
Procurement Compass - Deterministic Rules Engine
Version: 2.0 (Updated through GFR 31.01.2026)

THE LLM NEVER DECIDES. All logic here is 100% deterministic, auditable, and rule-provenanced.
"""

import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.models import (
    ProcurementInput,
    DecisionObject,
    ThresholdBand,
    ApprovalAuthorityResult,
    RequiredDocument,
    ProcurementClassificationResult
)
from app.classification.classifier import ProcurementClassifier

CONFIG_DIR = Path(__file__).parent.parent / "config"

class RulesEngine:
    def __init__(self):
        self.classifier = ProcurementClassifier()
        self.load_config()

    def load_config(self):
        with open(CONFIG_DIR / "thresholds.json", "r", encoding="utf-8") as f:
            self.thresholds_data = json.load(f)
        with open(CONFIG_DIR / "rulesets.json", "r", encoding="utf-8") as f:
            self.rulesets_data = json.load(f)
        with open(CONFIG_DIR / "sources.json", "r", encoding="utf-8") as f:
            self.sources_data = json.load(f)
        with open(CONFIG_DIR / "institution.json", "r", encoding="utf-8") as f:
            self.institution_data = json.load(f)

    def resolve_ruleset(self, procurement_date_str: Optional[str], override: Optional[str] = None) -> Dict[str, Any]:
        """Resolves applicable ruleset based strictly on procurement date."""
        if override:
            for rs in self.rulesets_data:
                if rs["ruleset_id"] == override:
                    return rs

        if not procurement_date_str:
            # Default to current if date unknown, but date resolution guard will flag NEEDS_INFO
            return self.rulesets_data[0]

        try:
            p_date = datetime.strptime(procurement_date_str, "%Y-%m-%d").date()
        except ValueError:
            return self.rulesets_data[0]

        cutoff_date = date(2026, 2, 1)
        if p_date >= cutoff_date:
            return self.rulesets_data[0]  # gfr_2017_updated_31_01_2026
        else:
            return self.rulesets_data[1]  # gfr_2017_historical_original

    def check_split_purchases(self, inp: ProcurementInput, threshold_limit: float) -> Optional[Dict[str, Any]]:
        """Detects if related recent purchases within 30-day window aggregate above threshold."""
        if not inp.related_recent_purchases:
            return None

        recent_total = sum(rp.value_inr for rp in inp.related_recent_purchases)
        combined_val = (inp.estimated_value_inr or 0.0) + recent_total

        if combined_val > threshold_limit and (inp.estimated_value_inr or 0.0) <= threshold_limit:
            return {
                "flag": "split_purchase_suspected",
                "related_value": recent_total,
                "combined_value": combined_val,
                "window_days": 30,
                "purchases_count": len(inp.related_recent_purchases),
                "message": "Related recent purchases may need to be considered together under the applicable procurement rule (GFR Rule 144 prohibition of splitting demand)."
            }
        return None

    def evaluate(self, inp: ProcurementInput, assessment_id: str) -> DecisionObject:
        missing_fields: List[str] = []
        flags: List[str] = []
        escalation_reasons: List[str] = []
        applied_rules: List[Dict[str, Any]] = []
        required_docs: List[RequiredDocument] = []

        # 1. Validation of essential input fields
        if inp.estimated_value_inr is None:
            missing_fields.append("estimated_value_inr")

        if not inp.procurement_date:
            missing_fields.append("procurement_date")

        # 2. Date / Ruleset Resolution
        ruleset = self.resolve_ruleset(inp.procurement_date, inp.ruleset_override)
        ruleset_id = ruleset["ruleset_id"]

        # 3. Procurement Classification
        classification = self.classifier.classify(inp)
        if classification.category == "UNCERTAIN":
            escalation_reasons.append("Procurement classification is materially uncertain based on provided description.")

        # 4. Tax basis validation
        if inp.tax_inclusive is None:
            missing_fields.append("tax_inclusive")

        # 5. GeM Status Evaluation
        gem_assessment = {
            "status": inp.gem_status,
            "evidence": inp.gem_evidence,
            "note": ""
        }

        # 6. Check for deliberate institutional policy conflict
        if inp.institution_policy_loaded:
            conflict_info = self.institution_data.get("deliberate_conflict")
            if conflict_info:
                # If user's purchase resembles the conflicting clause (goods up to 75,000 without GeM)
                if (inp.estimated_value_inr and 50000 < inp.estimated_value_inr <= 75000 
                    and inp.gem_status in ["search_not_performed", "not_applicable"]):
                    escalation_reasons.append(
                        f"POLICY CONFLICT DETECTED: {conflict_info['title']} ({conflict_info['clause_ref']}) "
                        f"purports to allow direct purchase up to ₹75,000 without GeM, which directly conflicts with "
                        f"Central GFR Rule 154 (₹50,000 cap) and GFR Rule 149 (mandatory GeM first). System cannot safely resolve conflict."
                    )
                    flags.append("policy_conflict_detected")

        # 7. Check for Emergency Procurement (§21)
        if inp.is_emergency:
            escalation_reasons.append("Emergency procurement route requires explicit disaster/urgency certification outside automated deterministic rules. Escalation to Competent Authority required.")
            flags.append("emergency_procurement_declared")

        # 8. Check for Proprietary / Single-Source Procurement (§22)
        if inp.is_proprietary or inp.is_single_source:
            escalation_reasons.append("Proprietary / Single Tender Enquiry (Rule 166) requires non-delegable approval of Competent Authority and PAC Certificate.")
            flags.append("proprietary_pac_declared")
            required_docs.append(RequiredDocument(
                name="Proprietary Article Certificate (PAC) Format GFR Rule 166",
                mandatory=True,
                rule_ref="Rule 166",
                description="Statutory certificate justifying single OEM manufacture and absence of equivalent alternatives."
            ))

        # 9. Handle Rate Contract (§20)
        if inp.is_rate_contract_item:
            procurement_route = "rate_contract"
            applied_rules.append({
                "rule_ref": "Rate Contract Framework",
                "source": "Manual for Procurement of Goods 2024",
                "description": "Procurement executed against valid existing Rate Contract / Standing Agreement."
            })
            required_docs.append(RequiredDocument(
                name="Valid Rate Contract Agreement Copy & Standing Price Schedule",
                mandatory=True,
                rule_ref="Rate Contract",
                description="Copy of active rate contract establishing contracted ceiling price and vendor terms."
            ))

        # 10. Missing GeM check for common goods/services
        if classification.category in ["GOODS", "COMPOSITE", "NON_CONSULTANCY_SERVICES"] and not inp.is_rate_contract_item:
            if inp.gem_status in ["unknown", "search_not_performed"]:
                missing_fields.append("gem_status")
                gem_assessment["note"] = "GeM search not performed or availability not established. GFR Rule 149 mandates prior GeM availability check."

        # 11. Research Eligibility Check (§9)
        # Only flag if user explicitly asserted research purpose or scientific equipment
        if (inp.research_purpose is True or inp.scientific_equipment is True):
            if inp.special_research_eligibility == "unknown":
                missing_fields.append("special_research_eligibility")
                flags.append("research_eligibility_unverified")

        # 12. Evaluate Route & Thresholds
        procurement_route = "escalate"
        threshold_band: Optional[ThresholdBand] = None
        val = inp.estimated_value_inr or 0.0
        is_scientific_special_eligible = (
            inp.special_research_eligibility == "eligible" 
            and inp.research_purpose is True 
            and inp.scientific_equipment is True
        )

        if inp.is_emergency or inp.is_proprietary or inp.is_single_source:
            procurement_route = "escalate"

        elif inp.is_rate_contract_item:
            procurement_route = "rate_contract"

        elif inp.estimated_value_inr is None:
            procurement_route = "escalate"

        elif inp.gem_status in ["unknown", "search_not_performed"] and classification.category in ["GOODS", "COMPOSITE", "NON_CONSULTANCY_SERVICES"]:
            procurement_route = "escalate"

        # Non-Goods Handling
        elif classification.category == "CONSULTANCY_SERVICES":
            procurement_route = "consultancy_selection"
            applied_rules.append({
                "rule_ref": "Consultancy Manual 2025 Para 1.4",
                "source": "manual_consultancy_services_2025",
                "description": "Intellectual / bespoke advisory services governed by QCBS / LCS selection framework."
            })
            required_docs.append(RequiredDocument(
                name="Terms of Reference (ToR) and RFP Document",
                mandatory=True,
                rule_ref="Consultancy Manual Para 2.1",
                description="Comprehensive Scope of Work, Technical Evaluation Criteria, and Deliverables schedule."
            ))

        elif classification.category == "WORKS":
            procurement_route = "works_tendering"
            applied_rules.append({
                "rule_ref": "Manual for Works 2025 Para 1.2",
                "source": "manual_works_2025",
                "description": "Civil / electrical / structural works contract to be executed via CPWD / Engineering division."
            })
            required_docs.append(RequiredDocument(
                name="Detailed Project Report (DPR) & Technical Sanction",
                mandatory=True,
                rule_ref="Works Manual Para 1.3",
                description="Engineering estimate and statutory Technical Sanction by competent engineering authority."
            ))

        elif classification.category == "NON_CONSULTANCY_SERVICES":
            if inp.gem_status == "available_verified":
                if val <= 25000:
                    procurement_route = "GeM_direct"
                elif val <= 500000:
                    procurement_route = "GeM_lowest_of_three"
                else:
                    procurement_route = "GeM_bidding"
            else:
                procurement_route = "service_bidding"
                applied_rules.append({
                    "rule_ref": "Manual for Non-Consultancy Services 2025 Para 1.3",
                    "source": "manual_services_non_consultancy_2025",
                    "description": "Outsourced services with measurable deliverables."
                })

        # Physical Goods or Composite (primarily Goods)
        elif classification.category in ["GOODS", "COMPOSITE"]:
            if inp.gem_status == "available_verified":
                # GeM Route under Rule 149
                applied_rules.append({
                    "rule_ref": "Rule 149",
                    "source": "gfr_2017_updated_2026",
                    "description": "Mandatory procurement through Government e-Marketplace (GeM)."
                })
                if val <= 25000:
                    procurement_route = "GeM_direct"
                    threshold_band = ThresholdBand(
                        lower=0,
                        upper=25000,
                        rule_ref="Rule 149(i)",
                        source_doc="GFR2017_updated_31012026.pdf",
                        page=35,
                        effective_from="2020-01-01"
                    )
                    required_docs.append(RequiredDocument(
                        name="GeM Direct Purchase Order and Seller Invoice",
                        mandatory=True,
                        rule_ref="Rule 149(i)",
                        description="Order placed with any registered GeM seller meeting quality and delivery specifications."
                    ))
                elif val <= 500000:
                    procurement_route = "GeM_lowest_of_three"
                    threshold_band = ThresholdBand(
                        lower=25000.01,
                        upper=500000,
                        rule_ref="Rule 149(ii)",
                        source_doc="GFR2017_updated_31012026.pdf",
                        page=35,
                        effective_from="2020-01-01"
                    )
                    required_docs.append(RequiredDocument(
                        name="GeM L1 Comparison Sheet (min 3 manufacturers)",
                        mandatory=True,
                        rule_ref="Rule 149(ii)",
                        description="Comparative price report showing L1 selection amongst at least three different manufacturers on GeM."
                    ))
                else:
                    procurement_route = "GeM_bidding"
                    threshold_band = ThresholdBand(
                        lower=500000.01,
                        upper=None,
                        rule_ref="Rule 149(iii)",
                        source_doc="GFR2017_updated_31012026.pdf",
                        page=35,
                        effective_from="2020-01-01"
                    )
                    required_docs.append(RequiredDocument(
                        name="GeM Custom Bid / Reverse Auction Summary Report",
                        mandatory=True,
                        rule_ref="Rule 149(iii)",
                        description="Online bidding / reverse auction evaluation summary generated on GeM."
                    ))

            elif inp.gem_status == "unavailable_verified":
                # Non-GeM GFR Routes
                # Check required Non-Availability Certificate
                required_docs.append(RequiredDocument(
                    name="GeM Non-Availability Certificate (NAC) / GeM Search Report",
                    mandatory=True,
                    rule_ref="Rule 149 & DoE OM",
                    description="Verified documentation establishing non-availability of item on GeM prior to outside procurement."
                ))

                # Determine applicable thresholds based on ruleset and scientific eligibility
                if is_scientific_special_eligible:
                    # Special Scientific Provisions
                    direct_max = 200000.0
                    pc_max = 2500000.0

                    if val <= direct_max:
                        procurement_route = "direct_purchase"
                        threshold_band = ThresholdBand(
                            lower=0,
                            upper=direct_max,
                            rule_ref="Rule 154 Special Provision",
                            source_doc="om-scientific-thresholds-2024.pdf",
                            page=2,
                            effective_from="2024-10-01"
                        )
                        applied_rules.append({
                            "rule_ref": "Rule 154 Special Provision",
                            "source": "doe_om_scientific_research_2024",
                            "description": "Special enhanced threshold for scientific research apparatus up to ₹2,00,000 without quotation."
                        })
                        required_docs.append(RequiredDocument(
                            name="Rule 154 Special Scientific Quality & Price Certificate",
                            mandatory=True,
                            rule_ref="Rule 154 Special Provision",
                            description="Personal certification of requisite quality and reasonable price by Investigator."
                        ))
                    elif val <= pc_max:
                        procurement_route = "purchase_committee"
                        threshold_band = ThresholdBand(
                            lower=direct_max + 0.01,
                            upper=pc_max,
                            rule_ref="Rule 155 Special Provision",
                            source_doc="om-scientific-thresholds-2024.pdf",
                            page=3,
                            effective_from="2024-10-01"
                        )
                        applied_rules.append({
                            "rule_ref": "Rule 155 Special Provision",
                            "source": "doe_om_scientific_research_2024",
                            "description": "Special Scientific Purchase Committee threshold above ₹2,00,000 up to ₹25,00,000."
                        })
                        required_docs.append(RequiredDocument(
                            name="Rule 155 Scientific Purchase Committee Joint Certificate",
                            mandatory=True,
                            rule_ref="Rule 155 Special Provision",
                            description="Joint certificate signed by 3-member Scientific Purchase Committee following market survey."
                        ))
                    else:
                        procurement_route = "advertised_tender"
                        threshold_band = ThresholdBand(
                            lower=pc_max + 0.01,
                            upper=None,
                            rule_ref="Rule 162",
                            source_doc="GFR2017_updated_31012026.pdf",
                            page=40,
                            effective_from="2026-02-01"
                        )
                        applied_rules.append({
                            "rule_ref": "Rule 162",
                            "source": "gfr_2017_updated_2026",
                            "description": "Open Advertised Tender on CPPP for values exceeding ₹25,00,000."
                        })

                else:
                    # Standard Non-GeM Procurement (GFR Baseline)
                    if ruleset_id == "gfr_2017_historical_original":
                        direct_max = 25000.0
                        pc_max = 250000.0
                        applied_source = "gfr_2017_historical_2017"
                        source_doc_name = "GFR2017_original.pdf"
                        effective_start = "2017-03-01"
                    else:
                        direct_max = 50000.0
                        pc_max = 500000.0
                        applied_source = "gfr_2017_updated_2026"
                        source_doc_name = "GFR2017_updated_31012026.pdf"
                        effective_start = "2026-02-01"

                    if val <= direct_max:
                        procurement_route = "direct_purchase"
                        threshold_band = ThresholdBand(
                            lower=0,
                            upper=direct_max,
                            rule_ref="Rule 154",
                            source_doc=source_doc_name,
                            page=36 if ruleset_id == "gfr_2017_updated_2026" else 34,
                            effective_from=effective_start
                        )
                        applied_rules.append({
                            "rule_ref": "Rule 154",
                            "source": applied_source,
                            "description": f"Purchase of goods without quotation up to ₹{int(direct_max):,} on each occasion."
                        })
                        required_docs.append(RequiredDocument(
                            name="Rule 154 Statutory Certificate of Requisite Quality & Reasonable Price",
                            mandatory=True,
                            rule_ref="Rule 154",
                            description="Mandatory officer certification in exact statutory format prescribed by Rule 154."
                        ))
                    elif val <= pc_max:
                        procurement_route = "purchase_committee"
                        threshold_band = ThresholdBand(
                            lower=direct_max + 0.01,
                            upper=pc_max,
                            rule_ref="Rule 155",
                            source_doc=source_doc_name,
                            page=36 if ruleset_id == "gfr_2017_updated_2026" else 35,
                            effective_from=effective_start
                        )
                        applied_rules.append({
                            "rule_ref": "Rule 155",
                            "source": applied_source,
                            "description": f"Purchase of goods by Local Purchase Committee above ₹{int(direct_max):,} up to ₹{int(pc_max):,}."
                        })
                        required_docs.append(RequiredDocument(
                            name="Rule 155 Local Purchase Committee Joint Certificate & Survey Report",
                            mandatory=True,
                            rule_ref="Rule 155",
                            description="Joint certificate signed by 3 committee members surveying market for price reasonableness."
                        ))
                    elif val <= 2500000.0:
                        procurement_route = "limited_tender"
                        threshold_band = ThresholdBand(
                            lower=pc_max + 0.01,
                            upper=2500000.0,
                            rule_ref="Rule 161",
                            source_doc=source_doc_name,
                            page=39,
                            effective_from=effective_start
                        )
                        applied_rules.append({
                            "rule_ref": "Rule 161",
                            "source": applied_source,
                            "description": "Limited Tender Enquiry (LTE) for goods up to ₹25,00,000."
                        })
                    else:
                        procurement_route = "advertised_tender"
                        threshold_band = ThresholdBand(
                            lower=2500000.01,
                            upper=None,
                            rule_ref="Rule 162",
                            source_doc=source_doc_name,
                            page=40,
                            effective_from=effective_start
                        )
                        applied_rules.append({
                            "rule_ref": "Rule 162",
                            "source": applied_source,
                            "description": "Advertised Tender Enquiry on Central Public Procurement Portal (CPPP) for goods above ₹25 Lakhs."
                        })

                # Check Institutional Overlay internal limit
                if inp.institution_policy_loaded and procurement_route == "direct_purchase":
                    internal_cap = self.institution_data.get("internal_thresholds", {}).get("direct_purchase_internal_cap", 40000)
                    if val > internal_cap:
                        flags.append(f"Institutional overlay note: Central rule permits direct purchase up to ₹{int(threshold_band.upper or 0):,}, but internal institute guidelines cap direct purchase at ₹{internal_cap:,}.")

        # 13. Split Purchase Check (§19)
        if threshold_band and threshold_band.upper:
            split_res = self.check_split_purchases(inp, threshold_band.upper)
            if split_res:
                flags.append("split_purchase_suspected")
                applied_rules.append({
                    "rule_ref": "Rule 144",
                    "source": "gfr_2017_updated_2026",
                    "description": split_res["message"]
                })

        # 14. Approval Authority Determination (MANDATORY SAFETY LAW §3 & §18)
        # Never infer Dean/Director from titles. Only populate if explicit delegation matches.
        approval_authority = ApprovalAuthorityResult(
            status="not_found",
            value=None,
            source=None,
            note="Competent Authority — institutional delegation must be verified against approved financial powers."
        )

        if inp.institution_policy_loaded:
            # Check explicit delegation matrix
            delegation_list = self.institution_data.get("delegation_matrix", [])
            for entry in delegation_list:
                limit = entry.get("limit_inr")
                fs = entry.get("funding_source", "any")
                if fs == "any" or fs == inp.funding_source:
                    if limit is None or val <= limit:
                        approval_authority = ApprovalAuthorityResult(
                            status="explicit",
                            value=entry["role"],
                            source="Institute Purchase Manual v3.1 Schedule B",
                            delegation_limit_inr=limit,
                            note=f"Approved under Institutional Delegation of Financial Powers for {entry['role']}."
                        )
                        break

        # 15. Final Status Determination (§17)
        if escalation_reasons:
            status = "ESCALATE"
        elif missing_fields:
            status = "NEEDS_INFO"
        elif classification.classification_status == "uncertain":
            status = "ESCALATE"
        else:
            status = "COMPLETE"

        # Evidence Status & Rule Coverage
        evidence_status = "complete" if status == "COMPLETE" else ("partial" if status == "NEEDS_INFO" else "conflicting" if "policy_conflict_detected" in flags else "insufficient")
        rule_coverage = "complete" if applied_rules else "insufficient"
        retrieval_quality = "verified"

        return DecisionObject(
            assessment_id=assessment_id,
            status=status,
            procurement_classification=classification,
            procurement_route=procurement_route,
            threshold_band=threshold_band,
            approval_authority=approval_authority,
            ruleset_used=ruleset_id,
            applied_rules=applied_rules,
            gem_assessment=gem_assessment,
            required_documents=required_docs,
            missing_fields=missing_fields,
            flags=flags,
            escalation_reasons=escalation_reasons,
            evidence_status=evidence_status,
            rule_coverage=rule_coverage,
            retrieval_quality=retrieval_quality
        )
