import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
} from "firebase/auth";
import { ShieldCheck } from "lucide-react";

import { auth } from "../firebase";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignup, setIsSignup] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      if (isSignup) {
        await createUserWithEmailAndPassword(
          auth,
          email,
          password
        );
      } else {
        await signInWithEmailAndPassword(
          auth,
          email,
          password
        );
      }

      navigate("/");
    } catch {
      setError("Authentication failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 px-6 py-12 text-zinc-900">
      <div className="w-full max-w-sm">
        {/* Branding */}
        <div className="mb-6 text-center">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-900 text-white">
            <ShieldCheck className="h-5 w-5" />
          </div>

          <h1 className="mt-4 text-xl font-bold tracking-tight text-zinc-900">
            TrustLens
          </h1>

          <p className="mt-1 text-xs text-zinc-500">
            Claim Verification Engine
          </p>
        </div>

        {/* Card */}
        <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-xs">
          <h2 className="text-base font-semibold text-zinc-900">
            {isSignup ? "Create an account" : "Sign in to TrustLens"}
          </h2>

          <p className="mt-1 text-xs text-zinc-500">
            {isSignup
              ? "Register to start analyzing claims."
              : "Enter your credentials to continue."}
          </p>

          <form
            onSubmit={handleSubmit}
            className="mt-5 space-y-4"
          >
            {/* Email */}
            <div>
              <label className="mb-1.5 block text-xs font-medium text-zinc-700">
                Email
              </label>

              <input
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                placeholder="name@example.com"
                required
                className="w-full rounded-lg border border-zinc-200 bg-zinc-50/50 px-3.5 py-2 text-sm text-zinc-900 outline-none transition placeholder:text-zinc-400 focus:bg-white focus:border-zinc-900 focus:ring-1 focus:ring-zinc-900"
              />
            </div>

            {/* Password */}
            <div>
              <label className="mb-1.5 block text-xs font-medium text-zinc-700">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="••••••••"
                required
                minLength={6}
                className="w-full rounded-lg border border-zinc-200 bg-zinc-50/50 px-3.5 py-2 text-sm text-zinc-900 outline-none transition placeholder:text-zinc-400 focus:bg-white focus:border-zinc-900 focus:ring-1 focus:ring-zinc-900"
              />
            </div>

            {/* Error */}
            {error && (
              <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-zinc-900 px-4 py-2.5 text-xs font-medium text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Please wait..."
                : isSignup
                  ? "Create Account"
                  : "Sign In"}
            </button>
          </form>

          {/* Toggle */}
          <div className="mt-5 text-center text-xs text-zinc-500">
            {isSignup
              ? "Already have an account?"
              : "Don't have an account?"}{" "}
            <button
              type="button"
              onClick={() => {
                setIsSignup(!isSignup);
                setError("");
              }}
              className="font-medium text-zinc-900 hover:underline"
            >
              {isSignup ? "Sign in" : "Sign up"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
