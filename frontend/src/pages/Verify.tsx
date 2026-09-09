import { useState } from "react";
import { ShieldCheck, Sparkles } from "lucide-react";

import VerificationResult from "../components/VerificationResult";
import { verifyResponse } from "../services/api";
import type { VerificationResponse } from "../types/verification";

function Verify() {
  const [response, setResponse] = useState("");
  const [result, setResult] = useState<VerificationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleVerify() {
    if (!response.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await verifyResponse(response);
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Verification failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-8 p-8">

      {/* Verification Input */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="font-semibold">AI Response</h3>
            <p className="mt-1 text-sm text-slate-500">
              Paste the response you want TrustLens to analyze.
            </p>
          </div>

          <Sparkles className="h-5 w-5 text-indigo-400" />
        </div>

        <textarea
          value={response}
          onChange={(event) => setResponse(event.target.value)}
          placeholder="Paste an AI-generated response here..."
          className="min-h-56 w-full resize-y rounded-xl border border-slate-800 bg-slate-950 p-4 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-indigo-500"
        />

        <div className="mt-4 flex items-center justify-between">
          <p className="text-xs text-slate-600">
            {response.length} characters
          </p>

          <button
            onClick={handleVerify}
            disabled={!response.trim() || loading}
            className="flex items-center gap-2 rounded-xl bg-indigo-500 px-5 py-3 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ShieldCheck className="h-4 w-4" />

            {loading ? "Verifying..." : "Verify Response"}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Verification Results */}
      {result && (
        <VerificationResult
          trustScore={result.trust_score}
          supportedClaims={result.supported_claims}
          contradictedClaims={result.contradicted_claims}
          uncertainClaims={result.uncertain_claims}
          claims={result.claims}
        />
      )}
    </section>
  );
}

export default Verify;
