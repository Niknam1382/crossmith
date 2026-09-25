import { useEffect, useState } from "react";
import { useTheme, type ThemeMode } from "@/lib/theme";
import { engine, type EngineSettings } from "@/lib/engine";

export function Settings() {
  const { mode, setMode } = useTheme();
  const [settings, setSettings] = useState<EngineSettings | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    engine
      .getSettings()
      .then((s) => {
        setSettings(s);
        setMode(s.theme);
      })
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Unknown error"),
      );
    // Only load once on mount — subsequent writes update local state directly.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function updateAndPersist(patch: Partial<EngineSettings>) {
    if (!settings) return;
    const next = { ...settings, ...patch };
    setSettings(next); // optimistic
    try {
      await engine.updateSettings(patch);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  function handleThemeChange(next: ThemeMode) {
    setMode(next); // instant visual feedback
    void updateAndPersist({ theme: next });
  }

  if (error) {
    return (
      <div className="p-8 text-sm text-danger">
        Couldn't load settings: {error}
      </div>
    );
  }

  if (!settings) {
    return <div className="p-8 text-sm text-ink-muted">Loading…</div>;
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-8 p-8">
      <h1 className="text-2xl font-semibold text-ink">Settings</h1>

      <Section title="Appearance">
        <div className="flex gap-2">
          {(["light", "dark", "system"] as const).map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => handleThemeChange(option)}
              className={`rounded-lg border px-3 py-1.5 text-sm capitalize transition-colors ${
                mode === option
                  ? "border-accent bg-accent text-accent-ink"
                  : "border-border text-ink hover:bg-surface-raised"
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </Section>

      <Section
        title="Local AI assist"
        description="Optional, fully offline. Never sends your code anywhere. See docs/DECISIONS.md."
      >
        <Toggle
          checked={settings.ai_assist_enabled}
          onChange={(checked) => updateAndPersist({ ai_assist_enabled: checked })}
          label="Use local AI to help with ambiguous projects"
        />
      </Section>

      <Section title="Default packaging backend">
        <div className="flex gap-2">
          {(["nuitka", "pyinstaller"] as const).map((backend) => (
            <button
              key={backend}
              type="button"
              onClick={() => updateAndPersist({ default_packaging_backend: backend })}
              className={`rounded-lg border px-3 py-1.5 text-sm capitalize transition-colors ${
                settings.default_packaging_backend === backend
                  ? "border-accent bg-accent text-accent-ink"
                  : "border-border text-ink hover:bg-surface-raised"
              }`}
            >
              {backend}
            </button>
          ))}
        </div>
      </Section>
    </div>
  );
}

function Section({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section>
      <h2 className="text-sm font-semibold text-ink">{title}</h2>
      {description && (
        <p className="mt-0.5 text-sm text-ink-muted">{description}</p>
      )}
      <div className="mt-3">{children}</div>
    </section>
  );
}

function Toggle({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
}) {
  return (
    <label className="flex items-center gap-3 text-sm text-ink">
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative h-6 w-11 rounded-full transition-colors ${
          checked ? "bg-accent" : "bg-border"
        }`}
      >
        <span
          className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${
            checked ? "translate-x-5" : "translate-x-0.5"
          }`}
        />
      </button>
      {label}
    </label>
  );
}
