import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import StatCard from "../components/StatCard";
import VerificationCard from "../components/VerificationCard";
import { getVerificationHistory } from "../services/api";
import type { VerificationHistoryItem } from "../types/history";

function Dashboard() {
  const navigate = useNavigate();
  const [history, setHistory] = useState<VerificationHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await getVerificationHistory();
        setHistory(data.verifications);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load dashboard data."
        );
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, []);

  const totalVerifications = history.length;

  const totalSupported = history.reduce(
    (sum, item) => sum + item.supported_claims,
    0
  );

  const totalContradicted = history.reduce(
    (sum, item) => sum + item.contradicted_claims,
    0
  );

  const totalUncertain = history.reduce(
    (sum, item) => sum + item.uncertain_claims,
    0
  );

  const averageTrustScore =
    totalVerifications > 0
      ? (
          history.reduce(
            (sum, item) => sum + item.trust_score,
            0
          ) / totalVerifications
        ).toFixed(1)
      : "—";

  return (
    <section className="space-y-8 p-8">
      {/* Dashboard Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">
          Trust Overview
        </h2>

        <p className="mt-2 text-sm text-slate-500">
          Monitor the reliability of the AI responses you have verified.
        </p>
      </div>

      {/* Stats */}
      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard
          label="Total Verifications"
          value={loading ? "..." : totalVerifications}
          description="Responses analyzed"
        />

        <StatCard
          label="Average Trust Score"
          value={loading ? "..." : averageTrustScore}
          description="Across your verifications"
        />

        <StatCard
          label="Supported Claims"
          value={loading ? "..." : totalSupported}
          description="Verified claims"
        />

        <StatCard
          label="Contradicted Claims"
          value={loading ? "..." : totalContradicted}
          description="Contradictions detected"
        />

        <StatCard
          label="Uncertain Claims"
          value={loading ? "..." : totalUncertain}
          description="Claims requiring caution"
        />
      </div>

      {/* Recent Verifications */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900">
        <div className="flex items-center justify-between border-b border-slate-800 p-6">
          <div>
            <h3 className="font-semibold text-white">
              Recent Verifications
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Your latest TrustLens analyses.
            </p>
          </div>

          {history.length > 0 && (
            <button
              type="button"
              onClick={() => navigate("/history")}
              className="rounded-lg border border-slate-800 px-3 py-2 text-xs text-slate-400 transition hover:border-slate-700 hover:text-white"
            >
              View All
            </button>
          )}
        </div>

        <div className="space-y-4 p-6">
          {loading && (
            <p className="text-sm text-slate-500">
              Loading recent verifications...
            </p>
          )}

          {!loading && error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-400">
              {error}
            </div>
          )}

          {!loading && !error && history.length === 0 && (
            <p className="text-sm text-slate-500">
              No verifications yet.
            </p>
          )}

          {!loading &&
            !error &&
            history.slice(0, 5).map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => navigate("/history")}
                className="block w-full rounded-xl text-left transition hover:opacity-90"
              >
                <VerificationCard
                  response={item.original_response}
                  trustScore={item.trust_score}
                  totalClaims={item.total_claims}
                  supportedClaims={item.supported_claims}
                  contradictedClaims={item.contradicted_claims}
                  uncertainClaims={item.uncertain_claims}
                  createdAt={item.created_at}
                />
              </button>
            ))}
        </div>
      </div>

      {/* How TrustLens Works */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div>
          <h3 className="font-semibold text-white">
            How TrustLens Works
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Every AI response passes through a multi-stage verification pipeline.
          </p>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-sm font-medium text-white">
              01 · Claims
            </p>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              AI responses are broken into individual claims.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-sm font-medium text-white">
              02 · Evidence
            </p>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              Relevant external sources are retrieved for each claim.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-sm font-medium text-white">
              03 · Verification
            </p>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              Claims are evaluated against the retrieved evidence.
            </p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-sm font-medium text-white">
              04 · Trust Score
            </p>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              Results are aggregated into an overall trust assessment.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Dashboard;
