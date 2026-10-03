export type StatusType = 'COMPLETE' | 'NEEDS_INFO' | 'ESCALATE';

export interface ProcurementInput {
  item_description: string;
  category: 'goods' | 'services' | 'works' | 'unknown';
  estimated_value_inr: number | null;
  tax_inclusive: boolean | null;
  procurement_date: string | null;
  decision_date?: string | null;
  gem_status: 'available_verified' | 'unavailable_verified' | 'search_not_performed' | 'unknown' | 'not_applicable';
  funding_source: 'institute' | 'project' | 'grant' | 'unknown';
  institution_type?: string;
  institution_policy_loaded: boolean;
  research_purpose: boolean | null;
  scientific_equipment: boolean | null;
  special_research_eligibility: 'eligible' | 'not_eligible' | 'unknown';
  is_emergency: boolean;
  is_proprietary: boolean;
  is_single_source: boolean;
  is_rate_contract_item: boolean;
  contains_installation: boolean;
  contains_commissioning: boolean;
  contains_training: boolean;
  contains_maintenance: boolean;
  contains_software: boolean;
  contains_cloud: boolean;
  contains_integration: boolean;
  related_recent_purchases: Array<{
    item_description: string;
    date: string;
    value_inr: number;
    department?: string;
    project_id?: string;
  }>;
  ruleset_override?: string | null;
}

export interface ThresholdBand {
  lower: number;
  upper: number | null;
  currency: string;
  rule_ref: string;
  source_doc: string;
  page?: number | null;
  effective_from: string;
  effective_to?: string | null;
}

export interface ApprovalAuthorityResult {
  status: 'explicit' | 'not_found' | 'conflict';
  value: string | null;
  source: string | null;
  delegation_limit_inr?: number | null;
  note: string;
}

export interface RequiredDocument {
  name: string;
  mandatory: boolean;
  rule_ref: string;
  description: string;
  template_available?: boolean;
}

export interface DecisionObject {
  assessment_id: string;
  status: StatusType;
  procurement_classification: {
    category: string;
    subtype?: string | null;
    classification_status: string;
    confidence: string;
    signals: string[];
    supporting_clauses: string[];
  };
  procurement_route: string;
  threshold_band: ThresholdBand | null;
  approval_authority: ApprovalAuthorityResult;
  ruleset_used: string;
  applied_rules: Array<{
    rule_ref: string;
    source: string;
    description: string;
  }>;
  gem_assessment: {
    status: string;
    note?: string;
    evidence?: any;
  };
  required_documents: RequiredDocument[];
  missing_fields: string[];
  flags: string[];
  escalation_reasons: string[];
  evidence_status: 'complete' | 'partial' | 'insufficient' | 'conflicting';
  rule_coverage: 'complete' | 'partial' | 'insufficient';
  retrieval_quality: 'verified' | 'weak' | 'failed';
}

export interface CitationRef {
  citation_id: string;
  rule_ref: string;
  source_title: string;
  source_version: string;
  page: number | null;
  authority_level: number;
  is_synthetic: boolean;
  excerpt: string;
}

export interface ExplanationResponse {
  status: StatusType;
  summary: string;
  applicable_rules: Array<{
    rule_ref: string;
    source: string;
    citation: string;
  }>;
  steps: Array<{
    number: number;
    text: string;
    citations: string[];
  }>;
  checklist: Array<{
    item: string;
    required: boolean;
    citations: string[];
  }>;
  missing_information: string[];
  flags: string[];
  assumptions: string[];
  escalation: {
    needed: boolean;
    reasons: string[];
    institution_authority_unresolved: boolean;
  };
  source_summary: string[];
  verification_note: string;
}

export interface AssessmentResponse {
  assessment_id: string;
  timestamp: string;
  procurement_date: string;
  as_of_date: string;
  decision: DecisionObject;
  explanation: ExplanationResponse;
  citations: CitationRef[];
  audit: {
    assessment_id: string;
    input_hash: string;
    ruleset_used: string;
    retrieval_mode: string;
    chunks_count: number;
  };
  verification: {
    citations_verified: boolean;
    amounts_verified: boolean;
    authority_verified: boolean;
    verification_status: 'passed' | 'failed';
    citation_issues?: string[];
    amount_issues?: string[];
    authority_issues?: string[];
  };
}

export interface SourceDocument {
  doc_id: string;
  title: string;
  issuer: string;
  authority_level: number;
  document_type: string;
  version: string;
  publication_date: string;
  effective_from: string;
  effective_to?: string | null;
  supersedes: string[];
  superseded_by: string[];
  source_url: string;
  is_synthetic: boolean;
  verified: boolean;
  summary: string;
}
