use std::sync::Mutex;

use tauri::{Manager, RunEvent};
use tauri_plugin_shell::{process::CommandEvent, ShellExt};

/// Handle to the running engine sidecar, so it can be killed when the app
/// exits. `None` until `setup()` spawns it.
struct EngineProcess(Mutex<Option<tauri_plugin_shell::process::CommandChild>>);

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(EngineProcess(Mutex::new(None)))
        .setup(|app| {
            let handle = app.handle().clone();

            // In dev, scripts/dev.sh drops a thin wrapper here that execs
            // the venv's `crossmith-engine`; in a release bundle this is
            // the real PyInstaller-frozen binary (see scripts/build_sidecar.py).
            // Either way, this code path never changes.
            let (mut rx, child) = handle
                .shell()
                .sidecar("crossmith-engine")
                .expect(
                    "crossmith-engine sidecar not found — run scripts/dev.sh \
                     (or scripts/dev.ps1 on Windows) instead of `tauri dev` directly",
                )
                .spawn()
                .expect("failed to start the Crossmith engine process");

            *app.state::<EngineProcess>().0.lock().unwrap() = Some(child);

            // Engine logs already go to ~/.crossmith/logs/engine.log (see
            // engine/src/crossmith/logging_config.py); mirroring them to the
            // Rust process' stdout/stderr too just helps while developing.
            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    match event {
                        CommandEvent::Stdout(line) => {
                            print!("[engine] {}", String::from_utf8_lossy(&line));
                        }
                        CommandEvent::Stderr(line) => {
                            eprint!("[engine] {}", String::from_utf8_lossy(&line));
                        }
                        CommandEvent::Error(err) => {
                            eprintln!("[engine] error: {err}");
                        }
                        CommandEvent::Terminated(payload) => {
                            eprintln!("[engine] exited: {:?}", payload.code);
                        }
                        _ => {}
                    }
                }
            });

            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building the Crossmith application")
        .run(|app_handle, event| {
            // The engine is a child process, not a daemon — it must never
            // outlive the window. Without this it would keep running,
            // holding port 8765, after the user thinks they've quit.
            if let RunEvent::ExitRequested { .. } = event {
                if let Some(child) = app_handle
                    .state::<EngineProcess>()
                    .0
                    .lock()
                    .unwrap()
                    .take()
                {
                    let _ = child.kill();
                }
            }
        });
}
