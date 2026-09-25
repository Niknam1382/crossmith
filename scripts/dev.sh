#!/usr/bin/env bash
# Sets up the engine venv (if needed), drops a dev-mode sidecar wrapper so
# the Rust shell can spawn the engine the same way it will in production,
# and starts `tauri dev`.
#
# Why a wrapper instead of freezing a real binary for every dev run: the
# sidecar mechanism (see src-tauri/src/lib.rs) always execs a binary named
# `crossmith-engine-<target-triple>` — it has no idea whether that's a
# PyInstaller-frozen executable (production, see build_sidecar.py) or a
# one-line script that just execs the venv's console entrypoint (dev). This
# keeps Rust's code identical in both cases and keeps dev iteration instant
# (no freeze step on every change).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENGINE_DIR="$REPO_ROOT/engine"
DESKTOP_DIR="$REPO_ROOT/desktop"
BIN_DIR="$DESKTOP_DIR/src-tauri/binaries"

echo "==> Engine: virtualenv"
if [ ! -d "$ENGINE_DIR/.venv" ]; then
  python3 -m venv "$ENGINE_DIR/.venv"
fi
"$ENGINE_DIR/.venv/bin/pip" install --quiet -e "$ENGINE_DIR"

echo "==> Engine: dev sidecar wrapper"
mkdir -p "$BIN_DIR"
TARGET_TRIPLE="$(rustc -vV | sed -n 's/^host: //p')"
if [ -z "$TARGET_TRIPLE" ]; then
  echo "error: couldn't determine your Rust target triple (is Rust installed? see rustup.rs)" >&2
  exit 1
fi
WRAPPER="$BIN_DIR/crossmith-engine-$TARGET_TRIPLE"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
exec "$ENGINE_DIR/.venv/bin/crossmith-engine" "\$@"
EOF
chmod +x "$WRAPPER"
echo "    wrote $WRAPPER"

echo "==> Starting Tauri dev shell"
cd "$DESKTOP_DIR"
npm run tauri dev
