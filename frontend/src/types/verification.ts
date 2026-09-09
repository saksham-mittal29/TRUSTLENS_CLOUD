export interface Evidence {
  id?: number;
  title: string;
  url: string;
  snippet: string;
}

export interface ClaimResult {
  claim: string;
  verdict: "SUPPORTED" | "CONTRADICTED" | "UNCERTAIN";
  confidence: number;
  reason: string;
  evidence_quality: number;
  evidence?: Evidence[];
}

export interface VerificationResponse {
  verification_id: number;
  trust_score: number;
  total_claims: number;
  supported_claims: number;
  contradicted_claims: number;
  uncertain_claims: number;
  claims: ClaimResult[];
}

export interface VerificationDetailResponse {
  id: number;
  original_response: string;
  trust_score: number;
  total_claims: number;
  supported_claims: number;
  contradicted_claims: number;
  uncertain_claims: number;
  created_at: string;
  claims: ClaimResult[];
}
