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
      title: "Dashboard",
      description: "Overview of verified statements and claim accuracy.",
    },
    "/verify": {
      title: "Verify",
      description: "Analyze and cross-reference claims against external sources.",
    },
    "/history": {
      title: "History",
      description: "Archive of previously processed verifications.",
    },
  };

  const currentPage =
    pageInfo[location.pathname as keyof typeof pageInfo] ?? pageInfo["/"];

  async function handleSignOut() {
    await signOut(auth);
    navigate("/login");
  }

  return (
    <header className="flex h-16 items-center justify-between border-b border-zinc-200 bg-white px-8">
      <div>
        <h2 className="text-base font-semibold text-zinc-900">{currentPage.title}</h2>
        <p className="text-xs text-zinc-500">
          {currentPage.description}
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-100 border border-zinc-200 text-zinc-600">
            <User className="h-4 w-4" />
          </div>

          <span className="max-w-48 truncate text-xs font-medium text-zinc-700">
            {user?.email ?? "User"}
          </span>
        </div>

        <button
          onClick={handleSignOut}
          title="Sign out"
          className="flex h-8 w-8 items-center justify-center rounded-md text-zinc-400 transition hover:bg-zinc-100 hover:text-zinc-700"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}

export default Header;
