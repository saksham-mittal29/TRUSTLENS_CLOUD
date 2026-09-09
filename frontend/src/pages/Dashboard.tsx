import StatCard from "../components/StatCard";
import VerificationCard from "../components/VerificationCard";

function Dashboard() {
  return (
    <section className="space-y-8 p-8">
      {/* Stats */}
      <div className="grid gap-5 md:grid-cols-3">
        <StatCard
          label="Trust Score"
          value="98.5"
          description="Excellent reliability"
        />

        <StatCard
          label="Supported Claims"
          value="1"
          description="Verified claims"
        />

        <StatCard
          label="Contradicted Claims"
          value="0"
          description="No contradictions detected"
        />
      </div>

      {/* Recent Verifications */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 p-6">
          <h3 className="font-semibold">Recent Verifications</h3>

          <p className="mt-1 text-sm text-slate-500">
            Your latest TrustLens analyses.
          </p>
        </div>

        <div className="space-y-4 p-6">
          <VerificationCard
            response="The Eiffel Tower is in Paris."
            trustScore={98.5}
            totalClaims={1}
            supportedClaims={1}
          />

          <VerificationCard
            response="Python was first released in 1991."
            trustScore={96.2}
            totalClaims={2}
            supportedClaims={2}
          />

          <VerificationCard
            response="The Earth is approximately 4.5 billion years old."
            trustScore={91.7}
            totalClaims={2}
            supportedClaims={1}
          />
        </div>
      </div>
    </section>
  );
}

export default Dashboard;
