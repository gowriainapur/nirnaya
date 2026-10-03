import { ProcurementInput, AssessmentResponse, SourceDocument } from '../types';

const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchSources(): Promise<SourceDocument[]> {
  const res = await fetch(`${API_BASE}/sources`);
  return res.json();
}

export async function fetchRulesets() {
  const res = await fetch(`${API_BASE}/rulesets`);
  return res.json();
}

export async function assessProcurement(input: ProcurementInput): Promise<AssessmentResponse> {
  const res = await fetch(`${API_BASE}/assess`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || 'Assessment request failed');
  }
  return res.json();
}

export async function runEvaluation() {
  const res = await fetch(`${API_BASE}/eval`, { method: 'POST' });
  return res.json();
}

export async function comparePolicies(rulesetA: string, rulesetB: string) {
  const res = await fetch(`${API_BASE}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ruleset_a: rulesetA, ruleset_b: rulesetB })
  });
  return res.json();
}

export async function simulateWhatIf(baseInput: ProcurementInput, variations: Record<string, any>) {
  const res = await fetch(`${API_BASE}/what-if`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ base_input: baseInput, variations })
  });
  return res.json();
}

export async function fetchAuditTrail(limit = 20) {
  const res = await fetch(`${API_BASE}/audit?limit=${limit}`);
  return res.json();
}
