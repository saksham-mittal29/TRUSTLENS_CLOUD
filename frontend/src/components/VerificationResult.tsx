import { CheckCircle2, XCircle, AlertTriangle } from "lucide-react";
import type { ClaimResult } from "../types/verification";

interface VerificationResultProps {
  trustScore: number;
  supportedClaims: number;
  contradictedClaims: number;
  uncertainClaims: number;
  claims: ClaimResult[];
}

function VerificationResult({
  trustScore,
  supportedClaims,
  contradictedClaims,
  uncertainClaims,
  claims,
}: VerificationResultProps) {
  return (
    <div className="space-y-6">
      {/* Trust Score */}
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-xs">
        <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
          Overall Trust Score
        </p>

        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-4xl font-bold tracking-tight text-zinc-900">{trustScore}</span>
          <span className="text-sm font-medium text-zinc-400">/ 100</span>
        </div>

        <div className="mt-4 h-2 overflow-hidden rounded-full bg-zinc-100">
          <div
            className="h-full rounded-full bg-zinc-900 transition-all duration-300"
            style={{ width: `${Math.min(Math.max(trustScore, 0), 100)}%` }}
          />
        </div>
      </div>

      {/* Claim Summary */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-xs">
          <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">Supported Claims</p>
          <p className="mt-2 text-2xl font-bold text-emerald-700">
            {supportedClaims}
          </p>
        </div>

        <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-xs">
          <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">Contradicted Claims</p>
          <p className="mt-2 text-2xl font-bold text-rose-700">
            {contradictedClaims}
          </p>
        </div>

        <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-xs">
          <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">Uncertain Claims</p>
          <p className="mt-2 text-2xl font-bold text-amber-800">
            {uncertainClaims}
          </p>
        </div>
      </div>

      {/* Claims */}
      <div className="rounded-xl border border-zinc-200 bg-white shadow-xs">
        <div className="border-b border-zinc-200 px-6 py-4">
          <h3 className="text-sm font-semibold text-zinc-900">Claim Analysis</h3>
          <p className="text-xs text-zinc-500">
            Factual breakdown and evidence cross-references for each statement.
          </p>
        </div>

        <div className="divide-y divide-zinc-200">
          {claims.map((claim, index) => {
            const verdictConfig = {
              SUPPORTED: {
                label: "SUPPORTED",
                icon: CheckCircle2,
                className: "text-emerald-700 bg-emerald-50 border-emerald-200",
              },
              CONTRADICTED: {
                label: "CONTRADICTED",
                icon: XCircle,
                className: "text-rose-700 bg-rose-50 border-rose-200",
              },
              UNCERTAIN: {
                label: "UNCERTAIN",
                icon: AlertTriangle,
                className: "text-amber-800 bg-amber-50 border-amber-200",
              },
            }[claim.verdict];

            const VerdictIcon = verdictConfig.icon;

            return (
              <div key={index} className="p-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-zinc-900 leading-snug">{claim.claim}</p>

                    <p className="mt-2 text-xs leading-relaxed text-zinc-600">
                      {claim.reason}
                    </p>
                  </div>

                  <div
                    className={`inline-flex shrink-0 items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-medium ${verdictConfig.className}`}
                  >
                    <VerdictIcon className="h-3.5 w-3.5" />
                    {verdictConfig.label}
                  </div>
                </div>

                <div className="mt-4 flex flex-wrap gap-6 text-xs text-zinc-500">
                  <div>
                    <span className="text-zinc-400">Confidence: </span>
                    <span className="font-medium text-zinc-700">{claim.confidence}%</span>
                  </div>

                  <div>
                    <span className="text-zinc-400">Evidence Quality: </span>
                    <span className="font-medium text-zinc-700">{claim.evidence_quality}%</span>
                  </div>
                </div>

                {claim.evidence && claim.evidence.length > 0 && (
                  <div className="mt-5 border-t border-zinc-100 pt-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                      Sources & Evidence ({claim.evidence.length})
                    </p>

                    <div className="mt-3 space-y-2.5">
                      {claim.evidence.map((evidence, evidenceIndex) => (
                        <a
                          key={evidence.id ?? evidenceIndex}
                          href={evidence.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block rounded-lg border border-zinc-200 bg-zinc-50/50 p-3.5 transition hover:border-zinc-300 hover:bg-zinc-50"
                        >
                          <p className="text-xs font-medium text-blue-600 hover:underline">
                            {evidence.title}
                          </p>

                          <p className="mt-1.5 text-xs leading-relaxed text-zinc-600">
                            {evidence.snippet}
                          </p>

                          <p className="mt-2 truncate text-[11px] font-mono text-zinc-400">
                            {evidence.url}
                          </p>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default VerificationResult;
