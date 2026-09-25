import { useEffect, useState } from "react";
import { Sidebar, type Page } from "@/components/Sidebar";
import { Home } from "@/pages/Home";
import { Settings } from "@/pages/Settings";
import { ThemeProvider } from "@/lib/theme";
import { engine } from "@/lib/engine";

type EngineStatus = "connecting" | "connected" | "unreachable";

function useEngineStatus(): EngineStatus {
  const [status, setStatus] = useState<EngineStatus>("connecting");

  useEffect(() => {
    let cancelled = false;
    let attempts = 0;

    // The Rust shell spawns the sidecar and this window at roughly the same
    // time, so the first health check or two failing is expected, not an
    // error — retry briefly before reporting unreachable.
    async function poll() {
      try {
        await engine.health();
        if (!cancelled) setStatus("connected");
      } catch {
        attempts += 1;
        if (cancelled) return;
        if (attempts >= 10) {
          setStatus("unreachable");
        } else {
          setTimeout(poll, 500);
        }
      }
    }

    poll();
    return () => {
      cancelled = true;
    };
  }, []);

  return status;
}

function App() {
  const [page, setPage] = useState<Page>("home");
  const engineStatus = useEngineStatus();

  return (
    <ThemeProvider>
      <div className="flex h-screen overflow-hidden bg-surface text-ink">
        <Sidebar current={page} onNavigate={setPage} />

        <main className="flex-1 overflow-y-auto">
          {engineStatus === "unreachable" && (
            <div className="border-b border-danger/30 bg-danger/5 px-4 py-2 text-sm text-danger">
              Can't reach the Crossmith engine. Try restarting the app.
            </div>
          )}

          {page === "home" && <Home />}
          {page === "settings" && <Settings />}
        </main>
      </div>
    </ThemeProvider>
  );
}

export default App;
