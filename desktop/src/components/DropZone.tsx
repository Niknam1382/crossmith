import { useEffect, useState } from "react";
import { getCurrentWebview } from "@tauri-apps/api/webview";

interface DropZoneProps {
  onProjectDropped: (path: string) => void;
}

/**
 * Listens for native OS drag-and-drop onto the window. This deliberately
 * uses Tauri's webview-level onDragDropEvent rather than plain HTML5 drop
 * events: browser File objects don't expose a real filesystem path, and
 * scanning a project needs one.
 */
export function DropZone({ onProjectDropped }: DropZoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    const unlistenPromise = getCurrentWebview().onDragDropEvent((event) => {
      switch (event.payload.type) {
        case "enter":
        case "over":
          setIsDragging(true);
          break;
        case "drop": {
          setIsDragging(false);
          const [firstPath] = event.payload.paths;
          if (firstPath) onProjectDropped(firstPath);
          break;
        }
        default:
          setIsDragging(false);
      }
    });

    return () => {
      unlistenPromise.then((unlisten) => unlisten());
    };
  }, [onProjectDropped]);

  return (
    <div
      className={`flex h-64 flex-col items-center justify-center rounded-2xl border-2 border-dashed text-center transition-colors ${
        isDragging
          ? "border-accent bg-accent/10"
          : "border-border bg-surface-raised"
      }`}
    >
      <p className="text-lg font-medium text-ink">
        Drop a project folder here
      </p>
      <p className="mt-1 text-sm text-ink-muted">
        Crossmith will figure out what it is
      </p>
    </div>
  );
}
