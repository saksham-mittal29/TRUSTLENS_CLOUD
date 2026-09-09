export interface VerificationHistoryItem {
  id: number;
  original_response: string;
  trust_score: number;
  total_claims: number;
  supported_claims: number;
  contradicted_claims: number;
  uncertain_claims: number;
  created_at: string;
}

export interface VerificationHistoryResponse {
  total: number;
  verifications: VerificationHistoryItem[];
}
