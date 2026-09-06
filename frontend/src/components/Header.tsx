import { User } from "lucide-react";

function Header() {
  return (
    <header className="flex h-20 items-center justify-between border-b border-slate-800 px-8">
      <div>
        <h2 className="text-xl font-semibold">
          Trust Overview
        </h2>

        <p className="text-sm text-slate-500">
          Monitor the reliability of your AI responses.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-800">
          <User className="h-4 w-4 text-slate-400" />
        </div>

        <span className="text-sm text-slate-300">
          User
        </span>
      </div>
    </header>
  );
}

export default Header;
