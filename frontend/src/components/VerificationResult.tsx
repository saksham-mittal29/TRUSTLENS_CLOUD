interface ClaimResult {
  claim: string;
  verdict: "SUPPORTED" | "CONTRADICTED" | "UNCERTAIN";
  confidence: number;
  reason: string;
  evidenceQuality: number;
}

interface VerificationResultProps {
  trustScore: number;
  claims: ClaimResult[];
}

function VerificationResult({
  trustScore,
  claims,
}: VerificationResultProps) {
  const supported = claims.filter(
    (claim) => claim.verdict === "SUPPORTED"
  ).length;

  const contradicted = claims.filter(
    (claim) => claim.verdict === "CONTRADICTED"
  ).length;

  const uncertain = claims.filter(
    (claim) => claim.verdict === "UNCERTAIN"
  ).length;

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
            {supported}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-500">Contradicted</p>
          <p className="mt-2 text-3xl font-bold text-red-400">
            {contradicted}
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-500">Uncertain</p>
          <p className="mt-2 text-3xl font-bold text-amber-400">
            {uncertain}
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
                    {claim.evidenceQuality}%
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default VerificationResult;
