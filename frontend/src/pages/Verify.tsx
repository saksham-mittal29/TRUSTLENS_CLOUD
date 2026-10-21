import { useState } from "react";
import { ShieldCheck } from "lucide-react";

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
    <section className="space-y-6 p-8">
      {/* Verification Input */}
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-xs">
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-zinc-900">Content to Verify</h3>
          <p className="mt-0.5 text-xs text-zinc-500">
            Paste or type any statement, claim, or report to verify against evidence sources.
          </p>
        </div>

        <textarea
          value={response}
          onChange={(event) => setResponse(event.target.value)}
          maxLength={20000}
          placeholder="Paste or write statement here to verify..."
          className="min-h-48 w-full resize-y rounded-lg border border-zinc-200 bg-zinc-50/40 p-4 text-sm text-zinc-900 outline-none transition placeholder:text-zinc-400 focus:bg-white focus:border-zinc-900 focus:ring-1 focus:ring-zinc-900"
        />

        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <p className="text-xs text-zinc-400 font-mono">
              {response.length.toLocaleString()} / 20,000 characters
            </p>

            {response && !loading && (
              <button
                type="button"
                onClick={() => {
                  setResponse("");
                  setResult(null);
                  setError("");
                }}
                className="text-xs text-zinc-500 hover:text-zinc-900 transition"
              >
                Clear text
              </button>
            )}
          </div>

          <button
            onClick={handleVerify}
            disabled={!response.trim() || loading}
            className="flex items-center gap-2 rounded-lg bg-zinc-900 px-4 py-2.5 text-xs font-medium text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {loading ? (
              <>
                <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Verifying...
              </>
            ) : (
              <>
                <ShieldCheck className="h-4 w-4" />
                Run Verification
              </>
            )}
          </button>
        </div>
      </div>

      {/* Verification Progress */}
      {loading && (
        <div className="flex items-center gap-3 rounded-xl border border-zinc-200 bg-white p-5 shadow-xs">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-zinc-300 border-t-zinc-900" />
          <div>
            <p className="text-xs font-semibold text-zinc-900">
              Verifying claims
            </p>
            <p className="text-xs text-zinc-500">
              Extracting statements and searching relevant external sources...
            </p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4">
          <p className="text-xs font-semibold text-rose-800">
            Verification error
          </p>

          <p className="mt-1 text-xs text-rose-700">
            {error.includes("503") || error.includes("UNAVAILABLE")
              ? "The verification service is temporarily unavailable. Please try again shortly."
              : error}
          </p>
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
