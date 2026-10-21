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
    <section className="space-y-6 p-8">
      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard
          label="Total Verifications"
          value={loading ? "..." : totalVerifications}
          description="Statements analyzed"
        />

        <StatCard
          label="Average Trust Score"
          value={loading ? "..." : averageTrustScore}
          description="Mean accuracy score"
          highlight={typeof averageTrustScore === "number"}
        />

        <StatCard
          label="Supported Claims"
          value={loading ? "..." : totalSupported}
          description="Confirmed with evidence"
        />

        <StatCard
          label="Contradicted Claims"
          value={loading ? "..." : totalContradicted}
          description="Contradicted by evidence"
        />

        <StatCard
          label="Uncertain Claims"
          value={loading ? "..." : totalUncertain}
          description="Unverifiable or ambiguous"
        />
      </div>

      {/* Recent Verifications */}
      <div className="rounded-xl border border-zinc-200 bg-white shadow-xs">
        <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4">
          <div>
            <h3 className="text-sm font-semibold text-zinc-900">
              Recent Verifications
            </h3>
            <p className="text-xs text-zinc-500">
              Latest analyzed claims and evidence findings.
            </p>
          </div>

          {history.length > 0 && (
            <button
              type="button"
              onClick={() => navigate("/history")}
              className="rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-xs font-medium text-zinc-700 transition hover:bg-zinc-50"
            >
              View all
            </button>
          )}
        </div>

        <div className="space-y-3 p-6">
          {loading && (
            <p className="text-xs text-zinc-500">
              Loading recent verifications...
            </p>
          )}

          {!loading && error && (
            <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-xs text-rose-700">
              {error}
            </div>
          )}

          {!loading && !error && history.length === 0 && (
            <p className="text-xs text-zinc-500">
              No verifications recorded yet.
            </p>
          )}

          {!loading &&
            !error &&
            history.slice(0, 5).map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => navigate("/history")}
                className="block w-full text-left transition hover:opacity-95"
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
    </section>
  );
}

export default Dashboard;
