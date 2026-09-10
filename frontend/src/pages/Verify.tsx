import { useState, useEffect } from "react";
import { ShieldCheck, Sparkles } from "lucide-react";

import VerificationResult from "../components/VerificationResult";
import { verifyResponse } from "../services/api";
import type { VerificationResponse } from "../types/verification";

function Verify() {
  const [response, setResponse] = useState("");
  const [result, setResult] = useState<VerificationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [verificationStage, setVerificationStage] = useState(0);

  async function handleVerify() {
    if (!response.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setVerificationStage(1);

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

  useEffect(() => {
    if (!loading) {
      setVerificationStage(0);
      return;
    }

    const timer = setInterval(() => {
      setVerificationStage((current) =>
        current < 4 ? current + 1 : current
      );
    }, 2000);

    return () => clearInterval(timer);
  }, [loading]);

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
          maxLength={20000}
          placeholder="Paste an AI-generated response here..."
          className="min-h-56 w-full resize-y rounded-xl border border-slate-800 bg-slate-950 p-4 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-indigo-500"
        />

        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <p className="text-xs text-slate-600">
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
                className="text-xs text-slate-500 transition hover:text-white"
              >
                Clear
              </button>
            )}
          </div>

          <button
            onClick={handleVerify}
            disabled={!response.trim() || loading}
            className="flex items-center gap-2 rounded-xl bg-indigo-500 px-5 py-3 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {loading ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Verifying...
              </>
            ) : (
              <>
                <ShieldCheck className="h-4 w-4" />
                Verify Response
              </>
            )}
          </button>
        </div>
      </div>

      {/* Verification Stages */}
      {loading && (
        <div className="rounded-2xl border border-indigo-500/20 bg-indigo-500/5 p-6">
          <div className="flex items-center gap-3">
            <div className="h-2 w-2 animate-pulse rounded-full bg-indigo-400" />

            <div>
              <p className="font-medium text-white">
                Analyzing your response
              </p>

              <p className="mt-1 text-sm text-slate-500">
                TrustLens is verifying the information.
              </p>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            {[
              "Extracting claims",
              "Searching for evidence",
              "Evaluating claims",
              "Calculating trust score",
            ].map((stage, index) => {
              const stageNumber = index + 1;
              const completed = verificationStage > stageNumber;
              const active = verificationStage === stageNumber;

              return (
                <div
                  key={stage}
                  className="flex items-center gap-3"
                >
                  <div
                    className={`flex h-6 w-6 items-center justify-center rounded-full text-xs ${
                      completed
                        ? "bg-emerald-500/20 text-emerald-400"
                        : active
                          ? "bg-indigo-500/20 text-indigo-400"
                          : "bg-slate-800 text-slate-600"
                    }`}
                  >
                    {completed ? "✓" : stageNumber}
                  </div>

                  <p
                    className={`text-sm ${
                      active || completed
                        ? "text-slate-300"
                        : "text-slate-600"
                    }`}
                  >
                    {stage}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-5">
          <p className="font-medium text-red-400">
            Verification failed
          </p>

          <p className="mt-2 text-sm leading-6 text-red-300/70">
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
