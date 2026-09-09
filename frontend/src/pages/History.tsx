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
    <section className="space-y-8 p-8">
      {/* History List */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 p-6">
          <h3 className="font-semibold">Recent Analyses</h3>

          <p className="mt-1 text-sm text-slate-500">
            Your previously verified AI responses.
          </p>
        </div>

        {/* Loading */}
        {loading && (
          <div className="p-10 text-center text-sm text-slate-500">
            Loading verification history...
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="p-6">
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-400">
              {error}
            </div>
          </div>
        )}

        {/* Empty */}
        {!loading && !error && history.length === 0 && (
          <div className="p-10 text-center">
            <ShieldCheck className="mx-auto h-10 w-10 text-slate-700" />

            <p className="mt-4 text-sm text-slate-500">
              No verifications yet.
            </p>

            <p className="mt-1 text-xs text-slate-600">
              Your completed TrustLens analyses will appear here.
            </p>
          </div>
        )}

        {/* History */}
        {!loading && !error && history.length > 0 && (
          <div className="divide-y divide-slate-800">
            {history.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => handleSelectVerification(item.id)}
                className="block w-full p-6 text-left transition hover:bg-slate-950"
              >
                <div className="flex items-start justify-between gap-6">
                  {/* Verification Info */}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="h-4 w-4 text-indigo-400" />

                      <p className="font-medium text-white">
                        {item.original_response}
                      </p>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs text-slate-500">
                      <span>{item.total_claims} claims</span>

                      <span className="text-emerald-400">
                        {item.supported_claims} supported
                      </span>

                      <span className="text-red-400">
                        {item.contradicted_claims} contradicted
                      </span>

                      <span className="text-amber-400">
                        {item.uncertain_claims} uncertain
                      </span>

                      <span>
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>

                  {/* Trust Score */}
                  <div className="shrink-0 text-right">
                    <p className="text-2xl font-bold text-white">
                      {item.trust_score}
                    </p>

                    <p className="text-xs text-slate-500">
                      Trust Score
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {selectedVerification && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="font-semibold text-white">
                Verification Details
              </h3>
              <p className="mt-1 text-sm text-slate-500">
                Verification #{selectedVerification}
              </p>
            </div>

            <button
              type="button"
              onClick={() => {
                setSelectedVerification(null);
                setDetail(null);
              }}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-400 transition hover:border-slate-600 hover:text-white"
            >
              Close
            </button>
          </div>

          {detailLoading && (
            <p className="mt-6 text-sm text-slate-500">
              Loading verification details...
            </p>
          )}

          {!detailLoading && detail && (
            <div className="mt-6 space-y-6">
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                  <p className="text-xs text-slate-500">
                    Total Claims
                  </p>
                  <p className="mt-2 text-2xl font-bold text-white">
                    {detail.total_claims}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                  <p className="text-xs text-slate-500">
                    Supported
                  </p>
                  <p className="mt-2 text-2xl font-bold text-emerald-400">
                    {detail.supported_claims}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                  <p className="text-xs text-slate-500">
                    Contradicted
                  </p>
                  <p className="mt-2 text-2xl font-bold text-red-400">
                    {detail.contradicted_claims}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
                  <p className="text-xs text-slate-500">
                    Uncertain
                  </p>
                  <p className="mt-2 text-2xl font-bold text-amber-400">
                    {detail.uncertain_claims}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm text-slate-500">
                  Verified On
                </p>
                <p className="mt-1 text-sm text-slate-300">
                  {new Date(detail.created_at).toLocaleString()}
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-500">
                  Original Response
                </p>
                <p className="mt-2 text-white">
                  {detail.original_response}
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-500">
                  Trust Score
                </p>
                <p className="mt-2 text-3xl font-bold text-white">
                  {detail.trust_score} / 100
                </p>
              </div>

              <div>
                <p className="font-semibold text-white">
                  Claims
                </p>

                <div className="mt-4 space-y-4">
                  {detail.claims.map((claim, index) => (
                    <div
                      key={index}
                      className="rounded-xl border border-slate-800 bg-slate-950 p-5"
                    >
                      <p className="font-medium text-white">
                        {claim.claim}
                      </p>

                      <p className="mt-3 text-sm text-slate-400">
                        Verdict: {claim.verdict}
                      </p>

                      <p className="mt-2 text-sm text-slate-400">
                        Confidence: {claim.confidence}%
                      </p>

                      <p className="mt-2 text-sm leading-6 text-slate-400">
                        {claim.reason}
                      </p>

                      {claim.evidence && claim.evidence.length > 0 && (
                        <div className="mt-5 border-t border-slate-800 pt-4">
                          <p className="text-sm font-medium text-slate-300">
                            Evidence
                          </p>

                          <div className="mt-3 space-y-3">
                            {claim.evidence.map((evidence, evidenceIndex) => (
                              <a
                                key={evidence.id ?? evidenceIndex}
                                href={evidence.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block rounded-lg border border-slate-800 bg-slate-900 p-4 transition hover:border-indigo-500/50"
                              >
                                <p className="font-medium text-indigo-400">
                                  {evidence.title}
                                </p>

                                <p className="mt-2 text-sm leading-6 text-slate-400">
                                  {evidence.snippet}
                                </p>

                                <p className="mt-2 truncate text-xs text-slate-600">
                                  {evidence.url}
                                </p>
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
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
