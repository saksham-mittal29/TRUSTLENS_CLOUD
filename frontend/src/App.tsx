import { BrowserRouter, Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import ProtectedRoute from "./components/ProtectedRoute";

import Dashboard from "./pages/Dashboard";
import Verify from "./pages/Verify";
import History from "./pages/History";
import Login from "./pages/Login";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public route */}
        <Route path="/login" element={<Login />} />

        {/* Protected application */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <div className="min-h-screen bg-zinc-50 text-zinc-900">
                <div className="flex min-h-screen">
                  <Sidebar />

                  <main className="flex-1 min-w-0">
                    <Header />

                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/verify" element={<Verify />} />
                      <Route path="/history" element={<History />} />
                    </Routes>
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;