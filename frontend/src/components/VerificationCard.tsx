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
    <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950 p-5">
      <div>
        <p className="font-medium">
          {response}
        </p>

        <p className="mt-1 text-sm text-slate-500">
          {totalClaims} claim{totalClaims !== 1 ? "s" : ""} •{" "}
          <span className="text-emerald-400">
            {supportedClaims} supported
          </span>{" "}
          •{" "}
          <span className="text-red-400">
            {contradictedClaims} contradicted
          </span>{" "}
          •{" "}
          <span className="text-amber-400">
            {uncertainClaims} uncertain
          </span>
        </p>

        <p className="mt-2 text-xs text-slate-600">
          {new Date(createdAt).toLocaleString()}
        </p>
      </div>

      <div className="text-right">
        <p className="text-2xl font-bold">
          {trustScore} / 100
        </p>

        <p className="text-xs text-slate-500">
          Trust Score
        </p>

        <p className="mt-1 text-xs text-slate-600">
          {trustScore >= 90
            ? "Excellent reliability"
            : trustScore >= 75
              ? "Good reliability"
              : trustScore >= 50
                ? "Moderate reliability"
                : "Low reliability"}
        </p>
      </div>
    </div>
  );
}

export default VerificationCard;
