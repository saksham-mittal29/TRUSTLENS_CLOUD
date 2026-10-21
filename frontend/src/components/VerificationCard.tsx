interface VerificationCardProps {
  response: string;
  trustScore: number;
  totalClaims: number;
  supportedClaims: number;
  contradictedClaims: number;
  uncertainClaims: number;
  createdAt: string;
}

function VerificationCard({
  response,
  trustScore,
  totalClaims,
  supportedClaims,
  contradictedClaims,
  uncertainClaims,
  createdAt,
}: VerificationCardProps) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-zinc-200 bg-white p-4.5 transition hover:border-zinc-300">
      <div className="min-w-0 flex-1 pr-6">
        <p className="text-sm font-medium text-zinc-900 line-clamp-2">
          {response}
        </p>

        <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
          <span className="text-zinc-500">
            {totalClaims} claim{totalClaims !== 1 ? "s" : ""}
          </span>
          <span className="text-zinc-300">•</span>
          <span className="rounded bg-emerald-50 px-1.5 py-0.5 font-medium text-emerald-700 border border-emerald-200/60">
            {supportedClaims} supported
          </span>
          <span className="rounded bg-rose-50 px-1.5 py-0.5 font-medium text-rose-700 border border-rose-200/60">
            {contradictedClaims} contradicted
          </span>
          <span className="rounded bg-amber-50 px-1.5 py-0.5 font-medium text-amber-800 border border-amber-200/60">
            {uncertainClaims} uncertain
          </span>
        </div>

        <p className="mt-2 text-xs text-zinc-400">
          {new Date(createdAt).toLocaleString(undefined, {
            dateStyle: "medium",
            timeStyle: "short",
          })}
        </p>
      </div>

      <div className="shrink-0 text-right">
        <p className="text-xl font-bold text-zinc-900">
          {trustScore} <span className="text-xs font-normal text-zinc-400">/ 100</span>
        </p>

        <p className="text-xs text-zinc-500">
          Trust Score
        </p>

        <p className="mt-0.5 text-xs font-medium text-zinc-600">
          {trustScore >= 90
            ? "High Reliability"
            : trustScore >= 75
              ? "Good Reliability"
              : trustScore >= 50
                ? "Moderate"
                : "Low Reliability"}
        </p>
      </div>
    </div>
  );
}

export default VerificationCard;
