"""
Procurement Compass - Classification Engine
Strict categorization of procurement:
- GOODS
- WORKS
- NON_CONSULTANCY_SERVICES
- CONSULTANCY_SERVICES
- COMPOSITE
- UNCERTAIN
"""

import re
from typing import List, Tuple
from app.models import ProcurementInput, ProcurementClassificationResult, DetailedCategoryType

class ProcurementClassifier:
    def __init__(self):
        # Keyword signals for primary categories
        self.goods_keywords = [
            "equipment", "apparatus", "laptop", "server", "desktop", "microscope", 
            "chemical", "reagent", "consumable", "furniture", "printer", "spectrometer", 
            "oscilloscope", "hardware", "device", "cables", "component", "sensor"
        ]
        self.works_keywords = [
            "construction", "civil works", "building", "renovation", "plumbing", 
            "structural", "electrical wiring", "erection", "substation", "flooring", 
            "civil repair", "demolition", "excavation", "pipeline", "masonry"
        ]
        self.non_consultancy_keywords = [
            "amc", "cmc", "maintenance", "housekeeping", "security guard", "catering", 
            "transport", "cleaning", "routine support", "helpdesk", "data entry", 
            "driver", "facility management", "repairs", "courier"
        ]
        self.consultancy_keywords = [
            "consultancy", "consultant", "advisory", "strategic study", "feasibility", 
            "bespoke software", "custom software development", "architectural design", 
            "algorithm design", "qcbs", "legal advice", "financial audit", "intellectual"
        ]
        self.cloud_it_keywords = [
            "cloud hosting", "aws", "azure", "gcp", "saas", "cloud implementation", 
            "system integration", "enterprise architecture"
        ]

    def classify(self, inp: ProcurementInput) -> ProcurementClassificationResult:
        desc = (inp.item_description or "").lower()
        signals: List[str] = []
        clauses: List[str] = []

        # Check explicit flags
        has_composite_flags = any([
            inp.contains_installation,
            inp.contains_commissioning,
            inp.contains_training,
            inp.contains_maintenance,
            inp.contains_software,
            inp.contains_cloud,
            inp.contains_integration
        ])

        # Scan text for category cues
        goods_hits = [k for k in self.goods_keywords if k in desc]
        works_hits = [k for k in self.works_keywords if k in desc]
        non_cons_hits = [k for k in self.non_consultancy_keywords if k in desc]
        cons_hits = [k for k in self.consultancy_keywords if k in desc]
        cloud_hits = [k for k in self.cloud_it_keywords if k in desc]

        # 1. Check for bespoke consultancy software vs off-the-shelf goods vs IT cloud
        if "bespoke" in desc or "custom software development" in desc or ("software development" in desc and "licence" not in desc):
            signals.append("Bespoke/custom software development detected -> Intellectual & advisory nature")
            clauses.append("Manual for Procurement of Consultancy Services 2025 Para 1.4")
            return ProcurementClassificationResult(
                category="CONSULTANCY_SERVICES",
                subtype="bespoke_software_development",
                classification_status="resolved",
                confidence="evidence_based",
                signals=signals,
                supporting_clauses=clauses
            )

        # 2. Check for Works
        if works_hits and not (goods_hits and ("install" in desc or inp.contains_installation)):
            signals.append(f"Civil/structural works detected: {', '.join(works_hits)}")
            clauses.append("Manual for Procurement of Works 2025 Para 1.2")
            return ProcurementClassificationResult(
                category="WORKS",
                subtype="civil_structural_works",
                classification_status="resolved",
                confidence="evidence_based",
                signals=signals,
                supporting_clauses=clauses
            )

        # 3. Check for pure Non-Consultancy Services
        if non_cons_hits and not goods_hits:
            signals.append(f"Routine non-consultancy service indicators: {', '.join(non_cons_hits)}")
            clauses.append("Manual for Procurement of Non-Consultancy Services 2025 Para 1.3")
            return ProcurementClassificationResult(
                category="NON_CONSULTANCY_SERVICES",
                subtype="routine_facility_or_maintenance",
                classification_status="resolved",
                confidence="evidence_based",
                signals=signals,
                supporting_clauses=clauses
            )

        # 4. Check for pure Consultancy Services
        if cons_hits and not goods_hits:
            signals.append(f"Consultancy/advisory indicators: {', '.join(cons_hits)}")
            clauses.append("Manual for Procurement of Consultancy Services 2025 Para 1.4")
            return ProcurementClassificationResult(
                category="CONSULTANCY_SERVICES",
                subtype="advisory_consulting",
                classification_status="resolved",
                confidence="evidence_based",
                signals=signals,
                supporting_clauses=clauses
            )

        # 5. Check for Composite Contracts (Equipment + Installation / AMC / Software)
        if (goods_hits and (has_composite_flags or non_cons_hits or cloud_hits or "installation" in desc or "amc" in desc or "commissioning" in desc)):
            composite_elements = []
            if inp.contains_installation or "installation" in desc or "install" in desc:
                composite_elements.append("installation")
            if inp.contains_commissioning or "commissioning" in desc:
                composite_elements.append("commissioning")
            if inp.contains_training or "training" in desc:
                composite_elements.append("training")
            if inp.contains_maintenance or "maintenance" in desc or "amc" in desc:
                composite_elements.append("AMC/maintenance")
            if inp.contains_software or inp.contains_cloud or inp.contains_integration:
                composite_elements.append("software/integration")

            signals.append(f"Composite procurement detected combining physical goods with: {', '.join(composite_elements)}")
            signals.append("Physical equipment constitutes predominant purpose and core value; incidental services ancillary.")
            clauses.append("Manual for Procurement of Goods 2024 Para 1.8 (Composite Contracts)")

            return ProcurementClassificationResult(
                category="COMPOSITE",
                subtype="goods_with_incidental_services",
                classification_status="resolved",
                confidence="evidence_based",
                signals=signals,
                supporting_clauses=clauses
            )

        # 6. Physical Goods
        if goods_hits or inp.category == "goods":
            subtype = "scientific_equipment" if (inp.scientific_equipment or "microscope" in desc or "spectrometer" in desc or "lab" in desc or "chemical" in desc) else "general_goods"
            signals.append(f"Physical goods detected: {', '.join(goods_hits) if goods_hits else 'user specified goods'}")
            clauses.append("GFR 2017 Rule 143 (Definition of Goods)")
            return ProcurementClassificationResult(
                category="GOODS",
                subtype=subtype,
                classification_status="resolved",
                confidence="evidence_based",
                signals=signals,
                supporting_clauses=clauses
            )

        # 7. Fallback based on user selected category if valid
        if inp.category == "services":
            return ProcurementClassificationResult(
                category="NON_CONSULTANCY_SERVICES",
                subtype="service_unspecified",
                classification_status="resolved",
                confidence="inferred",
                signals=["User categorized as services"],
                supporting_clauses=["Manual for Procurement of Non-Consultancy Services 2025"]
            )
        elif inp.category == "works":
            return ProcurementClassificationResult(
                category="WORKS",
                subtype="works_unspecified",
                classification_status="resolved",
                confidence="inferred",
                signals=["User categorized as works"],
                supporting_clauses=["Manual for Procurement of Works 2025"]
            )

        # 8. Ambiguous / Insufficient evidence
        return ProcurementClassificationResult(
            category="UNCERTAIN",
            subtype=None,
            classification_status="uncertain",
            confidence="uncertain",
            signals=["Insufficient keywords or conflicting signals to establish category unequivocally"],
            supporting_clauses=[]
        )
