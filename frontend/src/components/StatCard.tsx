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
    <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-xs">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
          {label}
        </p>

        {icon && (
          <div className="text-zinc-400">
            {icon}
          </div>
        )}
      </div>

      <p className="mt-2.5 text-2xl font-bold tracking-tight text-zinc-900">
        {value}
      </p>

      <p className="mt-1 text-xs text-zinc-500">
        {description}
      </p>

      {highlight && typeof value === "number" && (
        <div className="mt-3">
          <div className="h-1.5 overflow-hidden rounded-full bg-zinc-100">
            <div
              className="h-full rounded-full bg-zinc-900 transition-all duration-300"
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
