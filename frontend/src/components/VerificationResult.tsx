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
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <p className="text-sm text-slate-500">Overall Trust Score</p>

        <div className="mt-3 flex items-end gap-3">
          <span className="text-5xl font-bold">{trustScore}</span>
          <span className="mb-2 text-sm text-slate-500">/ 100</span>
        </div>

        <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-indigo-500"
            style={{ width: `${trustScore}%` }}
          />
        </div>
      </div>

      {/* Claim Summary */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-500">Supported</p>
          <p className="mt-2 text-3xl font-bold text-emerald-400">
            {supportedClaims}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-500">Contradicted</p>
          <p className="mt-2 text-3xl font-bold text-red-400">
            {contradictedClaims}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-500">Uncertain</p>
          <p className="mt-2 text-3xl font-bold text-amber-400">
            {uncertainClaims}
          </p>
        </div>
      </div>

      {/* Claims */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 p-6">
          <h3 className="font-semibold">Claim Analysis</h3>
          <p className="mt-1 text-sm text-slate-500">
            Detailed analysis of each extracted claim.
          </p>
        </div>

        <div className="divide-y divide-slate-800">
          {claims.map((claim, index) => (
            <div key={index} className="p-6">
              <div className="flex items-start justify-between gap-6">
                <div>
                  <p className="font-medium text-white">{claim.claim}</p>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    {claim.reason}
                  </p>
                </div>

                <span
                  className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium ${
                    claim.verdict === "SUPPORTED"
                      ? "bg-emerald-500/10 text-emerald-400"
                      : claim.verdict === "CONTRADICTED"
                        ? "bg-red-500/10 text-red-400"
                        : "bg-amber-500/10 text-amber-400"
                  }`}
                >
                  {claim.verdict}
                </span>
              </div>

              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-xs text-slate-600">Confidence</p>
                  <p className="mt-1 text-sm text-slate-300">
                    {claim.confidence}%
                  </p>
                </div>

                <div>
                  <p className="text-xs text-slate-600">
                    Evidence Quality
                  </p>
                  <p className="mt-1 text-sm text-slate-300">
                    {claim.evidence_quality}%
                  </p>
                </div>
              </div>

              {claim.evidence && claim.evidence.length > 0 && (
                <div className="mt-6 border-t border-slate-800 pt-5">
                  <p className="text-sm font-medium text-slate-300">
                    Evidence
                  </p>

                  <div className="mt-3 space-y-3">
                    {claim.evidence.map((evidence, evidenceIndex) => (
                      <a
                        key={evidence.id ?? evidenceIndex}
                        href={evidence.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block rounded-xl border border-slate-800 bg-slate-950 p-4 transition hover:border-indigo-500/50"
                      >
                        <p className="font-medium text-indigo-400">
                          {evidence.title}
                        </p>

                        <p className="mt-2 text-sm leading-6 text-slate-400">
                          {evidence.snippet}
                        </p>

                        <p className="mt-3 truncate text-xs text-slate-600">
                          {evidence.url}
                        </p>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default VerificationResult;
