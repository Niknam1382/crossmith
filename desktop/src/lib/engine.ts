/**
 * Typed client for the Crossmith engine — a loopback-only FastAPI sidecar
 * spawned by the Rust shell (see src-tauri/src/main.rs). The port is fixed
 * for now; Phase 3+ will read it from a Tauri command instead, so the Rust
 * side can pick a free port and pass it down.
 */
const ENGINE_BASE_URL = "http://127.0.0.1:8765";

export interface HealthResponse {
  status: string;
  version: string;
}

export interface DetectionMatch {
  matched: boolean;
  confidence: number;
  language: string;
  framework: string | null;
  entry_point: string | null;
  dependencies: string[];
  icon_candidate: string | null;
  metadata: Record<string, unknown>;
  reasons: string[];
}

export interface ScanResponse {
  matches: DetectionMatch[];
  needs_manual_review: boolean;
}

export interface BuildResponse {
  build_id: string;
  adapter_name: string;
  tests_ok: boolean;
  test_logs: string;
  success: boolean;
  artifact_paths: string[];
  logs: string;
  error: string | null;
  error_explanation: string | null;
}

export interface EngineSettings {
  theme: "light" | "dark" | "system";
  language: "en" | "fa";
  ai_assist_enabled: boolean;
  telemetry_enabled: boolean;
  default_packaging_backend: "nuitka" | "pyinstaller";
}

class EngineError extends Error {
  constructor(
    message: string,
    readonly status?: number,
    cause?: unknown,
  ) {
    super(message, { cause });
    this.name = "EngineError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${ENGINE_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch (cause) {
    throw new EngineError(
      "Can't reach the Crossmith engine. It may still be starting up.",
      undefined,
      cause,
    );
  }

  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new EngineError(body || response.statusText, response.status);
  }
  return response.json() as Promise<T>;
}

export const engine = {
  health: () => request<HealthResponse>("/health"),

  scanProject: (projectPath: string) =>
    request<ScanResponse>("/projects/scan", {
      method: "POST",
      body: JSON.stringify({ project_path: projectPath }),
    }),

  buildProject: (projectPath: string) =>
    request<BuildResponse>("/projects/build", {
      method: "POST",
      body: JSON.stringify({ project_path: projectPath }),
    }),

  getSettings: () => request<EngineSettings>("/settings"),

  updateSettings: (settings: Partial<EngineSettings>) =>
    request<EngineSettings>("/settings", {
      method: "PUT",
      body: JSON.stringify(settings),
    }),
};
