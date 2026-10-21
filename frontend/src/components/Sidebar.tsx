import {
  ShieldCheck,
  LayoutDashboard,
  SearchCheck,
  History,
} from "lucide-react";
import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside className="w-64 shrink-0 border-r border-zinc-200 bg-white p-6">
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-zinc-900 text-white">
          <ShieldCheck className="h-5 w-5" />
        </div>

        <div>
          <h1 className="text-base font-semibold text-zinc-900 tracking-tight">TrustLens</h1>
          <p className="text-xs text-zinc-500">Verification Engine</p>
        </div>
      </div>

      <nav className="space-y-1">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition ${
              isActive
                ? "bg-zinc-100 text-zinc-900"
                : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900"
            }`
          }
        >
          <LayoutDashboard className="h-4 w-4 text-zinc-500" />
          Dashboard
        </NavLink>

        <NavLink
          to="/verify"
          className={({ isActive }) =>
            `flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition ${
              isActive
                ? "bg-zinc-100 text-zinc-900"
                : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900"
            }`
          }
        >
          <SearchCheck className="h-4 w-4 text-zinc-500" />
          Verify
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) =>
            `flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition ${
              isActive
                ? "bg-zinc-100 text-zinc-900"
                : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900"
            }`
          }
        >
          <History className="h-4 w-4 text-zinc-500" />
          History
        </NavLink>
      </nav>
    </aside>
  );
}

export default Sidebar;
