import { User, LogOut } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { signOut } from "firebase/auth";

import { auth } from "../firebase";
import { useAuth } from "../context/AuthContext";

function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  const pageInfo = {
    "/": {
      title: "Trust Overview",
      description: "Monitor the reliability of your AI responses.",
    },
    "/verify": {
      title: "Verify Response",
      description: "Analyze an AI response for factual reliability.",
    },
    "/history": {
      title: "Verification History",
      description: "Review your previous TrustLens analyses.",
    },
  };

  const currentPage =
    pageInfo[location.pathname as keyof typeof pageInfo] ?? pageInfo["/"];

  async function handleSignOut() {
    await signOut(auth);
    navigate("/login");
  }

  return (
    <header className="flex h-20 items-center justify-between border-b border-slate-800 px-8">
      <div>
        <h2 className="text-xl font-semibold">{currentPage.title}</h2>

        <p className="text-sm text-slate-500">
          {currentPage.description}
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-800">
            <User className="h-4 w-4 text-slate-400" />
          </div>

          <span className="max-w-48 truncate text-sm text-slate-300">
            {user?.email ?? "User"}
          </span>
        </div>

        <button
          onClick={handleSignOut}
          title="Sign out"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-900 hover:text-white"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}

export default Header;
