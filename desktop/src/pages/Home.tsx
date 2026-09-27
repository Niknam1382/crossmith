import { useState } from "react";
import { DropZone } from "@/components/DropZone";
import { engine, type BuildResponse, type ScanResponse } from "@/lib/engine";

type ScanState =
  | { status: "idle" }
  | { status: "scanning"; path: string }
  | { status: "done"; path: string; result: ScanResponse }
  | { status: "error"; path: string; message: string };

type BuildState =
  | { status: "idle" }
  | { status: "building" }
  | { status: "done"; result: BuildResponse }
  | { status: "error"; message: string };

export function Home() {
  const [scan, setScan] = useState<ScanState>({ status: "idle" });
  const [build, setBuild] = useState<BuildState>({ status: "idle" });

  async function handleProjectDropped(path: string) {
    setBuild({ status: "idle" });
    setScan({ status: "scanning", path });
    try {
      const result = await engine.scanProject(path);
      setScan({ status: "done", path, result });
    } catch (err) {
      setScan({
        status: "error",
        path,
        message: err instanceof Error ? err.message : "Unknown error",
      });
    }
  }

  async function handleBuild(path: string) {
    setBuild({ status: "building" });
    try {
      const result = await engine.buildProject(path);
      setBuild({ status: "done", result });
    } catch (err) {
      setBuild({
        status: "error",
        message: err instanceof Error ? err.message : "Unknown error",
      });
    }
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6 p-8">
      <div>
        <h1 className="text-2xl font-semibold text-ink">Build a project</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Any codebase. Every platform. Zero config.
        </p>
      </div>

      <DropZone onProjectDropped={handleProjectDropped} />

      {scan.status === "scanning" && (
        <div className="rounded-xl border border-border bg-surface-raised p-4 text-sm text-ink-muted">
          Scanning <span className="font-mono">{scan.path}</span>…
        </div>
      )}

      {scan.status === "error" && (
        <div className="rounded-xl border border-danger/30 bg-danger/5 p-4 text-sm text-danger">
          Couldn't scan that project: {scan.message}
        </div>
      )}

      {scan.status === "done" && (
        <ScanResultPanel
          path={scan.path}
          result={scan.result}
          onBuild={() => handleBuild(scan.path)}
          buildDisabled={build.status === "building"}
        />
      )}

      {build.status === "building" && (
        <div className="rounded-xl border border-border bg-surface-raised p-4 text-sm text-ink-muted">
          Building — installing dependencies, running tests, then packaging.
          This can take anywhere from a few seconds to a minute or two.
        </div>
      )}

      {build.status === "error" && (
        <div className="rounded-xl border border-danger/30 bg-danger/5 p-4 text-sm text-danger">
          Couldn't reach the engine to build: {build.message}
        </div>
      )}

      {build.status === "done" && <BuildResultPanel result={build.result} />}
    </div>
  );
}

function ScanResultPanel({
  path,
  result,
  onBuild,
  buildDisabled,
}: {
  path: string;
  result: ScanResponse;
  onBuild: () => void;
  buildDisabled: boolean;
}) {
  if (result.matches.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-surface-raised p-4">
        <p className="text-sm font-medium text-ink">
          Nothing matched yet for <span className="font-mono">{path}</span>
        </p>
        <p className="mt-1 text-sm text-ink-muted">
          No installed adapter recognized this project. Only Python is
          supported so far — see the README's roadmap for what's next.
        </p>
      </div>
    );
  }

  const [top] = result.matches;
  const isAiAssisted = top.metadata?.source === "ai-assist";
  return (
    <div className="rounded-xl border border-border bg-surface-raised p-4">
      <p className="text-sm font-medium text-ink">
        Detected: {top.language}
        {top.framework ? ` (${top.framework})` : ""}
        {isAiAssisted && (
          <span className="ml-2 rounded-full bg-accent/10 px-2 py-0.5 text-xs font-normal text-accent">
            AI-assisted guess
          </span>
        )}
      </p>
      <p className="mt-1 text-sm text-ink-muted">
        Confidence: {Math.round(top.confidence * 100)}%
        {result.needs_manual_review ? " — please confirm below" : ""}
      </p>
      {top.reasons.length > 0 && (
        <ul className="mt-2 list-inside list-disc text-xs text-ink-muted">
          {top.reasons.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      )}

      <button
        type="button"
        onClick={onBuild}
        disabled={buildDisabled}
        className="mt-4 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-ink transition-opacity disabled:opacity-50"
      >
        Build
      </button>
    </div>
  );
}

function BuildResultPanel({ result }: { result: BuildResponse }) {
  if (!result.tests_ok) {
    return (
      <div className="rounded-xl border border-danger/30 bg-danger/5 p-4">
        <p className="text-sm font-medium text-danger">Tests failed</p>
        <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap text-xs text-ink-muted">
          {result.test_logs}
        </pre>
      </div>
    );
  }

  if (!result.success) {
    return (
      <div className="rounded-xl border border-danger/30 bg-danger/5 p-4">
        <p className="text-sm font-medium text-danger">
          Build failed: {result.error}
        </p>
        {result.error_explanation && (
          <p className="mt-1 text-sm text-ink">{result.error_explanation}</p>
        )}
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-success/30 bg-success/5 p-4">
      <p className="text-sm font-medium text-success">Build succeeded</p>
      {result.artifact_paths.map((path) => (
        <p key={path} className="mt-1 font-mono text-xs text-ink-muted">
          {path}
        </p>
      ))}
    </div>
  );
}
