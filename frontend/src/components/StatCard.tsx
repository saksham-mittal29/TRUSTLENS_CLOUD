interface StatCardProps {
  label: string;
  value: string | number;
  description: string;
  highlight?: boolean;
  icon?: React.ReactNode;
}

function StatCard({
  label,
  value,
  description,
  highlight = false,
  icon,
}: StatCardProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 transition duration-200 hover:-translate-y-1 hover:border-slate-700">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          {label}
        </p>

        {icon && (
          <div className="text-slate-500">
            {icon}
          </div>
        )}
      </div>

      <p className="mt-3 text-4xl font-bold">
        {value}
      </p>

      <p className="mt-2 text-sm text-slate-400">
        {description}
      </p>

      {highlight && typeof value === "number" && (
        <div className="mt-4">
          <div className="h-1.5 overflow-hidden rounded-full bg-slate-800">
            <div
              className="h-full rounded-full bg-indigo-500 transition-all duration-500"
              style={{
                width: `${Math.min(Math.max(value, 0), 100)}%`,
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default StatCard;
