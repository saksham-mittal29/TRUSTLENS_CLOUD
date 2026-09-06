import { History as HistoryIcon, ShieldCheck } from "lucide-react";

const history = [
  {
    id: 1,
    response: "The Eiffel Tower is located in Paris.",
    trustScore: 98.5,
    claims: 1,
    supported: 1,
    contradicted: 0,
    uncertain: 0,
    date: "Today, 10:42 AM",
  },
  {
    id: 2,
    response: "Python was first released in 1991.",
    trustScore: 96.2,
    claims: 2,
    supported: 2,
    contradicted: 0,
    uncertain: 0,
    date: "Yesterday, 6:18 PM",
  },
  {
    id: 3,
    response: "The Earth is approximately 4.5 billion years old.",
    trustScore: 91.7,
    claims: 2,
    supported: 1,
    contradicted: 0,
    uncertain: 1,
    date: "Sep 4, 2026",
  },
];

function History() {
  return (
    <section className="space-y-8 p-8">
      {/* Page Header */}
      <div>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/20">
            <HistoryIcon className="h-5 w-5 text-indigo-400" />
          </div>

          <div>
            <h2 className="text-2xl font-semibold">
              Verification History
            </h2>

            <p className="text-sm text-slate-500">
              Review your previous TrustLens analyses.
            </p>
          </div>
        </div>
      </div>

      {/* History List */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 p-6">
          <h3 className="font-semibold">Recent Analyses</h3>

          <p className="mt-1 text-sm text-slate-500">
            Your previously verified AI responses.
          </p>
        </div>

        <div className="divide-y divide-slate-800">
          {history.map((item) => (
            <div
              key={item.id}
              className="p-6 transition hover:bg-slate-950"
            >
              <div className="flex items-start justify-between gap-6">
                {/* Response */}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="h-4 w-4 text-indigo-400" />

                    <p className="truncate font-medium text-white">
                      {item.response}
                    </p>
                  </div>

                  <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs text-slate-500">
                    <span>{item.claims} claims</span>

                    <span className="text-emerald-400">
                      {item.supported} supported
                    </span>

                    <span className="text-red-400">
                      {item.contradicted} contradicted
                    </span>

                    <span className="text-amber-400">
                      {item.uncertain} uncertain
                    </span>

                    <span>{item.date}</span>
                  </div>
                </div>

                {/* Trust Score */}
                <div className="shrink-0 text-right">
                  <p className="text-2xl font-bold text-white">
                    {item.trustScore}
                  </p>

                  <p className="text-xs text-slate-500">
                    Trust Score
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default History;
