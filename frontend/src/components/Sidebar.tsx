import {
  ShieldCheck,
  LayoutDashboard,
  SearchCheck,
  History,
} from "lucide-react";
import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside className="w-64 shrink-0 border-r border-slate-800 bg-slate-950 p-6">
      <div className="mb-10 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/20">
          <ShieldCheck className="h-6 w-6 text-indigo-400" />
        </div>

        <div>
          <h1 className="text-lg font-semibold">TrustLens</h1>
          <p className="text-xs text-slate-500">AI Trust Verification</p>
        </div>
      </div>

      <nav className="space-y-2">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm transition ${
              isActive
                ? "bg-indigo-500/10 text-indigo-400"
                : "text-slate-400 hover:bg-slate-900 hover:text-white"
            }`
          }
        >
          <LayoutDashboard className="h-4 w-4" />
          Dashboard
        </NavLink>

        <NavLink
          to="/verify"
          className={({ isActive }) =>
            `flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm transition ${
              isActive
                ? "bg-indigo-500/10 text-indigo-400"
                : "text-slate-400 hover:bg-slate-900 hover:text-white"
            }`
          }
        >
          <SearchCheck className="h-4 w-4" />
          Verify
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) =>
            `flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm transition ${
              isActive
                ? "bg-indigo-500/10 text-indigo-400"
                : "text-slate-400 hover:bg-slate-900 hover:text-white"
            }`
          }
        >
          <History className="h-4 w-4" />
          History
        </NavLink>
      </nav>
    </aside>
  );
}

export default Sidebar;
