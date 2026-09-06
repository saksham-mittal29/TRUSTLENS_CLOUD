interface VerificationCardProps {
  response: string;
  trustScore: number;
  totalClaims: number;
  supportedClaims: number;
}

function VerificationCard({
  response,
  trustScore,
  totalClaims,
  supportedClaims,
}: VerificationCardProps) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950 p-5">
      <div>
        <p className="font-medium">
          {response}
        </p>

        <p className="mt-1 text-sm text-slate-500">
          {totalClaims} claim{totalClaims !== 1 ? "s" : ""} •{" "}
          {supportedClaims} supported
        </p>
      </div>

      <div className="text-right">
        <p className="text-2xl font-bold">
          {trustScore}
        </p>

        <p className="text-xs text-slate-500">
          Trust Score
        </p>
      </div>
    </div>
  );
}

export default VerificationCard;
