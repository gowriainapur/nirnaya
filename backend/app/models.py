"""
Procurement Compass - Core Pydantic Models
Version: 2.0 (Updated through GFR 31.01.2026)
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import date, datetime

# Enums & Literals
StatusType = Literal["COMPLETE", "NEEDS_INFO", "ESCALATE"]
CategoryType = Literal["goods", "services", "works", "unknown"]
DetailedCategoryType = Literal["GOODS", "WORKS", "NON_CONSULTANCY_SERVICES", "CONSULTANCY_SERVICES", "COMPOSITE", "UNCERTAIN"]
GeMStatusType = Literal["available_verified", "unavailable_verified", "search_not_performed", "unknown", "not_applicable"]
FundingSourceType = Literal["institute", "project", "grant", "unknown"]
SpecialEligibilityType = Literal["eligible", "not_eligible", "unknown"]
ApprovalAuthorityStatusType = Literal["explicit", "not_found", "conflict"]
EvidenceStatusType = Literal["complete", "partial", "insufficient", "conflicting"]
RuleCoverageType = Literal["complete", "partial", "insufficient"]
RetrievalQualityType = Literal["verified", "weak", "failed"]

class RelatedPurchase(BaseModel):
    item_description: str
    date: str  # YYYY-MM-DD
    value_inr: float
    department: Optional[str] = None
    project_id: Optional[str] = None
    category: Optional[str] = "goods"

class ProcurementInput(BaseModel):
    item_description: str = Field(..., description="Description of the item or service to purchase")
    category: CategoryType = Field(default="unknown", description="Initial high-level category")
    estimated_value_inr: Optional[float] = Field(default=None, description="Estimated purchase value in INR")
    tax_inclusive: Optional[bool] = Field(default=None, description="Whether the estimate includes all taxes")

    procurement_date: Optional[str] = Field(default=None, description="Date of procurement action (YYYY-MM-DD)")
    decision_date: Optional[str] = Field(default=None, description="Current decision evaluation date (YYYY-MM-DD)")

    gem_status: GeMStatusType = Field(default="unknown", description="GeM availability status")
    gem_evidence: Optional[Dict[str, Any]] = Field(default=None, description="Documented GeM search result / report")

    funding_source: FundingSourceType = Field(default="unknown", description="Funding source")

    institution_type: Optional[str] = Field(default="", description="e.g. IIT, Central University, Autonomous Research Institute")
    institution_policy_loaded: bool = Field(default=True, description="Whether institutional policy overlay is active")

    research_purpose: Optional[bool] = Field(default=None, description="Whether for research / scientific activity")
    scientific_equipment: Optional[bool] = Field(default=None, description="Whether item qualifies as scientific apparatus/consumable")
    special_research_eligibility: SpecialEligibilityType = Field(default="unknown", description="Verified eligibility for GFR Rule 154/155 special research thresholds")

    is_emergency: bool = Field(default=False, description="Emergency procurement declaration")
    is_proprietary: bool = Field(default=False, description="Proprietary / PAC / single OEM claim")
    is_single_source: bool = Field(default=False, description="Single source purchase")
    is_rate_contract_item: bool = Field(default=False, description="Covered under an active rate contract")

    contains_installation: bool = Field(default=False)
    contains_commissioning: bool = Field(default=False)
    contains_training: bool = Field(default=False)
    contains_maintenance: bool = Field(default=False)
    contains_software: bool = Field(default=False)
    contains_cloud: bool = Field(default=False)
    contains_integration: bool = Field(default=False)

    related_recent_purchases: List[RelatedPurchase] = Field(default_factory=list, description="Recent purchases for split-demand detection")

    ruleset_override: Optional[str] = Field(default=None, description="Force specific ruleset (e.g. historical comparison)")


class ProcurementClassificationResult(BaseModel):
    category: DetailedCategoryType
    subtype: Optional[str] = None
    classification_status: Literal["resolved", "uncertain", "needs_info"]
    confidence: Literal["evidence_based", "inferred", "uncertain"]
    signals: List[str] = Field(default_factory=list)
    supporting_clauses: List[str] = Field(default_factory=list)


class ThresholdBand(BaseModel):
    lower: float
    upper: Optional[float] = None
    currency: str = "INR"
    rule_ref: str
    source_doc: str
    page: Optional[int] = None
    effective_from: str
    effective_to: Optional[str] = None


class ApprovalAuthorityResult(BaseModel):
    status: ApprovalAuthorityStatusType
    value: Optional[str] = None
    source: Optional[str] = None
    delegation_limit_inr: Optional[float] = None
    note: str = "Competent Authority — institutional delegation must be verified"


class RequiredDocument(BaseModel):
    name: str
    mandatory: bool = True
    rule_ref: str
    description: str
    template_available: bool = False


class DecisionObject(BaseModel):
    assessment_id: str
    status: StatusType
    procurement_classification: ProcurementClassificationResult
    procurement_route: str
    threshold_band: Optional[ThresholdBand] = None
    approval_authority: ApprovalAuthorityResult
    ruleset_used: str
    applied_rules: List[Dict[str, Any]] = Field(default_factory=list)
    gem_assessment: Dict[str, Any] = Field(default_factory=dict)
    required_documents: List[RequiredDocument] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    flags: List[str] = Field(default_factory=list)
    escalation_reasons: List[str] = Field(default_factory=list)
    evidence_status: EvidenceStatusType = "complete"
    rule_coverage: RuleCoverageType = "complete"
    retrieval_quality: RetrievalQualityType = "verified"


class CitationRef(BaseModel):
    citation_id: str  # e.g. "S1", "S2"
    rule_ref: str
    source_title: str
    source_version: str
    page: Optional[int] = None
    authority_level: int
    is_synthetic: bool = False
    excerpt: str


class ExplanationStep(BaseModel):
    number: int
    text: str
    citations: List[str] = Field(default_factory=list)


class ChecklistItem(BaseModel):
    item: str
    required: bool = True
    citations: List[str] = Field(default_factory=list)


class ExplanationEscalation(BaseModel):
    needed: bool = False
    reasons: List[str] = Field(default_factory=list)
    institution_authority_unresolved: bool = False


class ExplanationResponse(BaseModel):
    status: StatusType
    summary: str
    applicable_rules: List[Dict[str, str]] = Field(default_factory=list)
    steps: List[ExplanationStep] = Field(default_factory=list)
    checklist: List[ChecklistItem] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    flags: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    escalation: ExplanationEscalation = Field(default_factory=ExplanationEscalation)
    source_summary: List[str] = Field(default_factory=list)
    verification_note: str = ""


class AssessmentResponse(BaseModel):
    assessment_id: str
    timestamp: str
    procurement_date: str
    as_of_date: str
    decision: DecisionObject
    explanation: ExplanationResponse
    citations: List[CitationRef] = Field(default_factory=list)
    audit: Dict[str, Any] = Field(default_factory=dict)
    verification: Dict[str, Any] = Field(default_factory=dict)


# Source Registry Model
class SourceDocument(BaseModel):
    doc_id: str
    title: str
    issuer: str
    authority_level: int
    document_type: Literal["gfr", "om", "manual", "institution_policy", "form", "circular", "synthetic"]
    version: str
    publication_date: str
    effective_from: str
    effective_to: Optional[str] = None
    supersedes: List[str] = Field(default_factory=list)
    superseded_by: List[str] = Field(default_factory=list)
    source_url: str = ""
    is_synthetic: bool = False
    verified: bool = True
    summary: str = ""


# Clause Chunk Model
class PolicyChunk(BaseModel):
    chunk_id: str
    doc_id: str
    rule_ref: str
    page: Optional[int] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    version: str
    effective_from: str
    effective_to: Optional[str] = None
    authority_level: int
    applies_to: List[str] = Field(default_factory=list)
    text: str
    is_synthetic: bool = False
    heading: str = ""
    conditions: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
