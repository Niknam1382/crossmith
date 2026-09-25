import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath } from "node:url";

const srcDir = fileURLToPath(new URL("./src", import.meta.url));

// Tauri expects a fixed dev server port and a relative base so the
// production build works when loaded from the bundled app, not a domain.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "./",
  resolve: {
    // Mirrors the "@/*" path in tsconfig.json — tsconfig only affects
    // type-checking, so Rollup needs its own copy of the alias to resolve
    // imports at build time.
    alias: { "@": srcDir },
  },

  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    watch: {
      // Don't rebuild the frontend because Rust/Python source changed.
      ignored: ["**/src-tauri/**", "**/../engine/**"],
    },
  },
  envPrefix: ["VITE_", "TAURI_"],
  build: {
    target: process.env.TAURI_ENV_PLATFORM === "windows" ? "chrome105" : "safari13",
    minify: !process.env.TAURI_ENV_DEBUG ? "esbuild" : false,
    sourcemap: !!process.env.TAURI_ENV_DEBUG,
  },
});
