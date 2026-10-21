import { useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";

import {
  getVerificationHistory,
  getVerificationDetail,
} from "../services/api";
import type { VerificationHistoryItem } from "../types/history";
import type { VerificationDetailResponse } from "../types/verification";

function History() {
  const [history, setHistory] = useState<VerificationHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedVerification, setSelectedVerification] =
    useState<number | null>(null);
  const [detail, setDetail] =
    useState<VerificationDetailResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await getVerificationHistory();
        setHistory(data.verifications);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load verification history."
        );
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, []);

  async function handleSelectVerification(id: number) {
    setSelectedVerification(id);
    setDetailLoading(true);
    setDetail(null);

    try {
      const data = await getVerificationDetail(id);
      setDetail(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load verification details."
      );
    } finally {
      setDetailLoading(false);
    }
  }

  return (
    <section className="space-y-6 p-8">
      {/* History List */}
      <div className="rounded-xl border border-zinc-200 bg-white shadow-xs">
        <div className="border-b border-zinc-200 px-6 py-4">
          <h3 className="text-sm font-semibold text-zinc-900">Verified Queries</h3>
          <p className="text-xs text-zinc-500">
            Log of previously verified texts and statements.
          </p>
        </div>

        {/* Loading */}
        {loading && (
          <div className="p-10 text-center text-xs text-zinc-500">
            Loading verification history...
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="p-6">
            <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-xs text-rose-700">
              {error}
            </div>
          </div>
        )}

        {/* Empty */}
        {!loading && !error && history.length === 0 && (
          <div className="p-12 text-center">
            <ShieldCheck className="mx-auto h-8 w-8 text-zinc-300" />
            <p className="mt-3 text-sm font-medium text-zinc-700">
              No verifications recorded
            </p>
            <p className="mt-1 text-xs text-zinc-500">
              Run a verification to populate the historical log.
            </p>
          </div>
        )}

        {/* History Rows */}
        {!loading && !error && history.length > 0 && (
          <div className="divide-y divide-zinc-200">
            {history.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => handleSelectVerification(item.id)}
                className="block w-full p-5 text-left transition hover:bg-zinc-50/70"
              >
                <div className="flex items-start justify-between gap-6">
                  {/* Verification Info */}
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-zinc-900 line-clamp-2">
                      {item.original_response}
                    </p>

                    <div className="mt-2.5 flex flex-wrap items-center gap-2 text-xs">
                      <span className="text-zinc-500 font-mono">
                        {item.total_claims} claims
                      </span>
                      <span className="text-zinc-300">•</span>
                      <span className="rounded bg-emerald-50 px-1.5 py-0.5 font-medium text-emerald-700 border border-emerald-200/60">
                        {item.supported_claims} supported
                      </span>
                      <span className="rounded bg-rose-50 px-1.5 py-0.5 font-medium text-rose-700 border border-rose-200/60">
                        {item.contradicted_claims} contradicted
                      </span>
                      <span className="rounded bg-amber-50 px-1.5 py-0.5 font-medium text-amber-800 border border-amber-200/60">
                        {item.uncertain_claims} uncertain
                      </span>
                      <span className="text-zinc-300">•</span>
                      <span className="text-zinc-400">
                        {new Date(item.created_at).toLocaleString(undefined, {
                          dateStyle: "medium",
                          timeStyle: "short",
                        })}
                      </span>
                    </div>
                  </div>

                  {/* Trust Score */}
                  <div className="shrink-0 text-right">
                    <p className="text-xl font-bold text-zinc-900">
                      {item.trust_score}
                      <span className="text-xs font-normal text-zinc-400"> / 100</span>
                    </p>
                    <p className="text-[11px] font-medium text-zinc-500">
                      Trust Score
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selected Verification Modal / Expanded Card */}
      {selectedVerification && (
        <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-xs">
          <div className="flex items-center justify-between border-b border-zinc-200 pb-4">
            <div>
              <h3 className="text-sm font-semibold text-zinc-900">
                Verification Details
              </h3>
              <p className="text-xs text-zinc-500">
                Record #{selectedVerification}
              </p>
            </div>

            <button
              type="button"
              onClick={() => {
                setSelectedVerification(null);
                setDetail(null);
              }}
              className="rounded-md border border-zinc-200 px-3 py-1.5 text-xs font-medium text-zinc-600 transition hover:bg-zinc-50"
            >
              Close
            </button>
          </div>

          {detailLoading && (
            <p className="mt-6 text-xs text-zinc-500">
              Loading verification details...
            </p>
          )}

          {!detailLoading && detail && (
            <div className="mt-6 space-y-6">
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <div className="rounded-lg border border-zinc-200 bg-zinc-50/50 p-4">
                  <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                    Total Claims
                  </p>
                  <p className="mt-1.5 text-xl font-bold text-zinc-900">
                    {detail.total_claims}
                  </p>
                </div>

                <div className="rounded-lg border border-zinc-200 bg-zinc-50/50 p-4">
                  <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                    Supported
                  </p>
                  <p className="mt-1.5 text-xl font-bold text-emerald-700">
                    {detail.supported_claims}
                  </p>
                </div>

                <div className="rounded-lg border border-zinc-200 bg-zinc-50/50 p-4">
                  <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                    Contradicted
                  </p>
                  <p className="mt-1.5 text-xl font-bold text-rose-700">
                    {detail.contradicted_claims}
                  </p>
                </div>

                <div className="rounded-lg border border-zinc-200 bg-zinc-50/50 p-4">
                  <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                    Uncertain
                  </p>
                  <p className="mt-1.5 text-xl font-bold text-amber-800">
                    {detail.uncertain_claims}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                  Original Text
                </p>
                <div className="mt-2 rounded-lg border border-zinc-200 bg-zinc-50/40 p-4 text-xs leading-relaxed text-zinc-800">
                  {detail.original_response}
                </div>
              </div>

              <div>
                <div className="flex items-baseline gap-2">
                  <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                    Trust Score:
                  </p>
                  <p className="text-lg font-bold text-zinc-900">
                    {detail.trust_score} <span className="text-xs font-normal text-zinc-400">/ 100</span>
                  </p>
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-zinc-700 mb-3">
                  Individual Claims
                </p>

                <div className="space-y-3">
                  {detail.claims.map((claim, index) => {
                    const badgeClass =
                      claim.verdict === "SUPPORTED"
                        ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                        : claim.verdict === "CONTRADICTED"
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : "bg-amber-50 text-amber-800 border-amber-200";

                    return (
                      <div
                        key={index}
                        className="rounded-lg border border-zinc-200 bg-zinc-50/30 p-4"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <p className="text-xs font-medium text-zinc-900 leading-snug">
                            {claim.claim}
                          </p>

                          <span
                            className={`inline-block shrink-0 rounded px-2 py-0.5 text-[11px] font-semibold border ${badgeClass}`}
                          >
                            {claim.verdict}
                          </span>
                        </div>

                        <p className="mt-2 text-xs leading-relaxed text-zinc-600">
                          {claim.reason}
                        </p>

                        <div className="mt-3 flex gap-4 text-[11px] text-zinc-500">
                          <span>Confidence: <strong className="text-zinc-700">{claim.confidence}%</strong></span>
                        </div>

                        {claim.evidence && claim.evidence.length > 0 && (
                          <div className="mt-4 border-t border-zinc-200 pt-3">
                            <p className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
                              Evidence Sources ({claim.evidence.length})
                            </p>

                            <div className="mt-2 space-y-2">
                              {claim.evidence.map((evidence, evidenceIndex) => (
                                <a
                                  key={evidence.id ?? evidenceIndex}
                                  href={evidence.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="block rounded-md border border-zinc-200 bg-white p-3 transition hover:border-zinc-300"
                                >
                                  <p className="text-xs font-medium text-blue-600 hover:underline">
                                    {evidence.title}
                                  </p>

                                  <p className="mt-1 text-xs leading-relaxed text-zinc-600">
                                    {evidence.snippet}
                                  </p>

                                  <p className="mt-1.5 truncate text-[11px] font-mono text-zinc-400">
                                    {evidence.url}
                                  </p>
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

export default History;
