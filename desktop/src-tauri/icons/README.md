Real icon files go here before running `npm run tauri build` (not required
for `npm run tauri dev`).

Once `docs/assets/logo.png` exists (see the README's placeholder note),
generate the full set with the Tauri CLI instead of hand-crafting each size:

```bash
cd desktop
npx tauri icon ../docs/assets/logo.png
```

That fills in `32x32.png`, `128x128.png`, `128x128@2x.png`, `icon.icns`, and
`icon.ico` — exactly the files `tauri.conf.json`'s `bundle.icon` list expects.
