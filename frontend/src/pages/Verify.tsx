import { useState } from "react";
import { SearchCheck, ShieldCheck, Sparkles } from "lucide-react";
import VerificationResult from "../components/VerificationResult";

function Verify() {
  const [response, setResponse] = useState("");

  const mockClaims = [
    {
      claim: "The Eiffel Tower is located in Paris, France.",
      verdict: "SUPPORTED" as const,
      confidence: 98,
      reason:
        "Multiple reliable sources confirm that the Eiffel Tower is located in Paris, France.",
      evidenceQuality: 96,
    },
    {
      claim: "The Eiffel Tower was completed in 1889.",
      verdict: "SUPPORTED" as const,
      confidence: 97,
      reason:
        "Historical sources consistently identify 1889 as the year the Eiffel Tower was completed.",
      evidenceQuality: 95,
    },
    {
      claim: "The Eiffel Tower is 500 meters tall.",
      verdict: "CONTRADICTED" as const,
      confidence: 94,
      reason:
        "Reliable sources report a height significantly lower than 500 meters.",
      evidenceQuality: 93,
    },
  ];

  return (
    <section className="space-y-8 p-8">
      {/* Page Header */}
      <div>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/20">
            <SearchCheck className="h-5 w-5 text-indigo-400" />
          </div>

          <div>
            <h2 className="text-2xl font-semibold">Verify AI Response</h2>
            <p className="text-sm text-slate-500">
              Analyze an AI response for factual reliability and trustworthiness.
            </p>
          </div>
        </div>
      </div>

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
            disabled={!response.trim()}
            className="flex items-center gap-2 rounded-xl bg-indigo-500 px-5 py-3 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ShieldCheck className="h-4 w-4" />
            Verify Response
          </button>
        </div>
      </div>

      {/* Verification Results */}
      <VerificationResult
        trustScore={82.4}
        claims={mockClaims}
      />
    </section>
  );
}

export default Verify;
