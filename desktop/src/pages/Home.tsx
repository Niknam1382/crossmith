import { useState } from "react";
import { DropZone } from "@/components/DropZone";
import { engine, type ScanResponse } from "@/lib/engine";

type ScanState =
  | { status: "idle" }
  | { status: "scanning"; path: string }
  | { status: "done"; path: string; result: ScanResponse }
  | { status: "error"; path: string; message: string };

export function Home() {
  const [scan, setScan] = useState<ScanState>({ status: "idle" });

  async function handleProjectDropped(path: string) {
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
        <ScanResultPanel path={scan.path} result={scan.result} />
      )}
    </div>
  );
}

function ScanResultPanel({
  path,
  result,
}: {
  path: string;
  result: ScanResponse;
}) {
  if (result.matches.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-surface-raised p-4">
        <p className="text-sm font-medium text-ink">
          Nothing matched yet for <span className="font-mono">{path}</span>
        </p>
        <p className="mt-1 text-sm text-ink-muted">
          No adapter recognized this project. Language adapters land in
          Phase 3 — the Python adapter is first.
        </p>
      </div>
    );
  }

  const [top] = result.matches;
  return (
    <div className="rounded-xl border border-border bg-surface-raised p-4">
      <p className="text-sm font-medium text-ink">
        Detected: {top.language}
        {top.framework ? ` (${top.framework})` : ""}
      </p>
      <p className="mt-1 text-sm text-ink-muted">
        Confidence: {Math.round(top.confidence * 100)}%
        {result.needs_manual_review ? " — please confirm below" : ""}
      </p>
    </div>
  );
}
