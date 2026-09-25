export type Page = "home" | "settings";

interface SidebarProps {
  current: Page;
  onNavigate: (page: Page) => void;
}

const NAV_ITEMS: { id: Page; label: string; icon: string }[] = [
  { id: "home", label: "Build", icon: "\u{1F528}" }, // 🔨
  { id: "settings", label: "Settings", icon: "\u2699\uFE0F" }, // ⚙️
];

export function Sidebar({ current, onNavigate }: SidebarProps) {
  return (
    <nav className="flex w-56 shrink-0 flex-col border-r border-border bg-surface-raised">
      <div className="titlebar-drag flex h-10 items-center px-4">
        <span className="text-sm font-semibold tracking-wide text-ink-muted">
          CROSSMITH
        </span>
      </div>

      <ul className="flex flex-col gap-1 p-2">
        {NAV_ITEMS.map((item) => {
          const isActive = item.id === current;
          return (
            <li key={item.id}>
              <button
                type="button"
                onClick={() => onNavigate(item.id)}
                aria-current={isActive ? "page" : undefined}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                  isActive
                    ? "bg-accent text-accent-ink font-medium"
                    : "text-ink hover:bg-surface"
                }`}
              >
                <span aria-hidden>{item.icon}</span>
                {item.label}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
