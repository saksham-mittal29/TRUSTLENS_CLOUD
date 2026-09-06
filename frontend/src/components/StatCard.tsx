interface StatCardProps {
  label: string;
  value: string | number;
  description: string;
}

function StatCard({
  label,
  value,
  description,
}: StatCardProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-sm text-slate-500">{label}</p>

      <p className="mt-3 text-4xl font-bold">
        {value}
      </p>

      <p className="mt-2 text-sm text-slate-400">
        {description}
      </p>
    </div>
  );
}

export default StatCard;
