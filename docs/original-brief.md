You are an elite Principal Software Architect, Open-Source Growth Strategist, DevSecOps Engineer, Product Designer, Technical Writer, and Community Builder.

Your mission is to design and build, from 0 to 100, a world-class open-source developer-tools project intended to become unrivaled in its category on GitHub.

Project working name: AutoForge AI
You may propose a better name if it is stronger, more memorable, more brandable, and better for GitHub discoverability.

====================================================================
GLOBAL INSTRUCTIONS
====================================================================

1. Do not ask me many questions.
2. Make optimal, modern, evidence-based technical decisions yourself.
3. If information is missing, make sensible assumptions and document them.
4. Prefer open-source, cross-platform, maintainable, secure, and privacy-first solutions.
5. Do not depend on paid proprietary cloud services by default.
6. Do not use n8n as the main desktop app framework unless you can strongly prove it is optimal.
7. Python is preferred for the core engine unless you can justify a better alternative.
8. The final result must feel like a premium, polished, trustworthy developer tool.
9. Design for GitHub virality, community growth, long-term maintainability, and professional open-source excellence.
10. Proceed autonomously through all phases without waiting for approval unless you are completely blocked.

====================================================================
PROJECT VISION
====================================================================

Build a beautiful, professional, cross-platform desktop application that lets programmers turn their source code projects into ready-to-distribute executables and installers automatically.

The user should be able to do this:

1. Open the app.
2. Drag and drop a project folder, a single source file, or paste a Git repository URL.
3. Optionally provide an app icon.
4. Click one button.
5. The system automatically detects:
   - programming language
   - framework
   - entry point
   - dependencies
   - required system packages
   - assets
   - icon
   - metadata
   - target platforms
   - build tools
   - tests
   - packaging requirements
6. The system downloads whatever is needed.
7. The system builds the project inside a clean, isolated, reproducible environment.
8. The system runs checks and tests if available.
9. The system produces ready-to-run outputs such as:
   - Windows .exe, portable app, installer
   - macOS .app, .dmg, notarization-ready bundle
   - Linux AppImage, .deb, .rpm, Snap, Flatpak
   - Android APK/AAB
   - iOS IPA or best possible iOS packaging workflow
   - Web/WASM output where relevant
10. The final result should be as automatic, safe, and bug-free as possible.

The product must feel like a premium developer tool, not a simple script wrapper.

====================================================================
CORE PRODUCT PRINCIPLES
====================================================================

1. Zero-config first
   The app should work with minimal user input. Advanced options should exist but should not be required.

2. Privacy-first
   The user's source code must not be uploaded anywhere by default. All AI analysis should preferably run locally.

3. Offline-friendly
   The app should work offline as much as possible, except when downloading dependencies or build tools is required.

4. Reproducible builds
   Builds should happen in isolated environments such as containers, VMs, sandboxed environments, or clean toolchains.

5. Multi-language by design
   The system must not be hardcoded to Python only. It must use a plugin/adapter architecture.

6. Extensible by community
   Third-party developers should be able to add support for new languages, frameworks, packagers, compilers, AI models, and target platforms.

7. GitHub-ready
   The repository itself must be a model of open-source excellence: beautiful README, excellent docs, CI/CD, tests, examples, contribution guide, security policy, releases, and community infrastructure.

====================================================================
MANDATORY FEATURE SET
====================================================================

A. Desktop GUI

Create a modern, professional desktop GUI.

Requirements:
- beautiful, clean, premium design
- dark mode and light mode
- drag-and-drop project folder support
- file selection support
- Git URL import support
- icon selection and automatic icon detection
- build progress logs
- terminal-style output panel
- project settings screen
- platform target selection
- AI assistant panel
- error diagnosis panel
- settings page
- plugin manager page
- release/export page
- responsive layout
- accessible UI
- internationalization-ready, with English as default and Persian as a future language

B. Smart Project Detection

The app must automatically detect:
- language
- framework
- package manager
- dependency files
- entry point
- README metadata
- license
- version
- icon candidates
- assets
- tests
- environment variables
- required permissions
- possible target platforms
- possible build tools

Detection should be hybrid:
1. heuristic file scanning
2. AST/code parsing where useful
3. local AI extraction using cactus-compute/needle if feasible
4. fallback manual configuration if confidence is low

C. Local AI Integration

Use this project if useful:
https://github.com/cactus-compute/needle

Needle is a lightweight local foundation model designed for:
- tool calling
- structured extraction
- local text embedding

Use Needle for:
- reading messy project files and extracting structured config
- detecting app name, description, version, icon, dependencies, entrypoint
- deciding which build adapter should be used
- suggesting fixes for common build problems
- filling missing metadata
- natural-language command execution inside the app
- offline AI assistance without sending user code to cloud APIs

Important:
- Needle must not become a hard dependency if it breaks the app.
- The system should have a fallback deterministic engine.
- AI features should be optional and privacy-preserving.
- Do not send source code to external services by default.
- Use AI only where it adds real value. Do not use AI for tasks that deterministic tooling can do more reliably.

Design a tool registry for Needle such as:
- scan_project()
- detect_language()
- detect_entrypoint()
- detect_dependencies()
- detect_icon()
- detect_metadata()
- suggest_targets()
- run_tests()
- build_target()
- fix_common_error()
- open_logs()
- export_config()

Needle responses should include confidence.
If confidence is low, ask the user or fall back to manual mode.

D. Build Engine

The build engine must be robust and modular.

It should support:
- dependency installation
- virtual environments or isolated toolchains
- containerized builds if optimal
- cross-compilation where possible
- testing before release
- linting if configured
- asset optimization
- icon generation for all platforms
- version stamping
- metadata injection
- code signing hooks
- notarization hooks
- UPX or binary compression where safe
- reproducible build manifests
- SBOM generation
- checksum generation
- build caching
- incremental builds if feasible

E. Output Targets

Design the system to generate outputs for as many platforms as possible.

Priority targets:
1. Windows
   - .exe
   - portable executable
   - installer
   - optional Microsoft Store packaging if feasible

2. Linux
   - AppImage
   - .deb
   - .rpm
   - Snap
   - Flatpak

3. macOS
   - .app bundle
   - .dmg
   - notarization-ready output
   - universal binary if feasible

4. Android
   - APK
   - AAB
   - use appropriate tooling depending on source language/framework

5. iOS
   - IPA or best possible workflow
   - clearly document Apple limitations
   - provide signing guidance
   - do not promise impossible fully automated iOS signing if Apple restrictions prevent it

6. Web
   - WASM or static bundle where relevant

F. Multi-Language Plugin Architecture

The app must support multiple languages through adapters/plugins.

Initial focus:
- Python

Next adapters to design for:
- Node.js / TypeScript
- Go
- Rust
- Java / Kotlin
- C / C++
- Flutter
- React Native
- Electron
- Tauri
- Web apps
- Shell scripts
- .NET

Each adapter should define:
- detection rules
- dependency manager
- build command
- test command
- package command
- required tools
- sandbox requirements
- metadata schema
- icon handling
- platform restrictions
- common error fixes
- example projects

G. Self-Build and Self-Release

The repository itself must be built and released automatically using CI/CD.

The project must include:
- GitHub Actions workflows
- automatic builds for Windows, macOS, Linux
- release creation
- artifact upload
- checksums
- changelog generation
- semantic versioning
- conventional commits
- optional code signing if secrets are provided
- optional notarization if secrets are provided
- draft releases
- nightly builds if appropriate
- automatic documentation deployment

H. Security and Trust

This is critical because the app will build executables.

Include:
- secure handling of secrets
- no hidden telemetry by default
- opt-in telemetry only if absolutely necessary
- dependency pinning
- supply-chain security practices
- SBOM generation
- reproducible builds where possible
- signed releases where possible
- malware false-positive mitigation strategy
- safe execution sandboxing
- permission model for plugins
- warning before running arbitrary build commands
- audit logging
- secure update mechanism if auto-update is implemented

====================================================================
TECHNICAL DECISION AUTHORITY
====================================================================

You are authorized and required to make optimal technical decisions.

Choose the best technologies for:
- desktop GUI
- backend/core engine
- AI integration
- sandboxing
- build orchestration
- plugin system
- packaging
- testing
- documentation
- CI/CD
- release automation
- community tooling

Preferred constraints:
- open-source
- cross-platform
- maintainable
- performant
- developer-friendly
- easy to contribute to
- not dependent on proprietary cloud services
- suitable for GitHub public repository
- suitable for standalone binary distribution

If multiple good options exist:
- choose the one with best long-term maintainability
- explain why
- document rejected alternatives

If you believe Python is the best core language, use it.
If another stack is better, justify it.

====================================================================
GITHUB DOMINATION REQUIREMENTS
====================================================================

The repository must be engineered to become one of the best open-source developer tool repositories on GitHub.

It must include:

1. World-class README.md
   - powerful headline
   - project logo placeholder
   - hero section
   - badges
   - short demo GIF placeholder
   - feature list
   - screenshots section
   - quick start
   - installation instructions
   - usage instructions
   - supported languages
   - supported output platforms
   - plugin guide
   - AI privacy note
   - comparison with alternatives
   - architecture overview
   - roadmap
   - FAQ
   - troubleshooting
   - contribution section
   - license
   - star call-to-action

2. Branding package
   - project name
   - logo concept
   - favicon concept
   - social preview concept
   - color palette
   - typography suggestion
   - tagline
   - short description
   - GitHub topics

3. Documentation website
   Choose optimal docs system.
   Include:
   - getting started
   - installation
   - user guide
   - plugin development guide
   - adapter development guide
   - AI integration guide
   - security guide
   - release guide
   - troubleshooting
   - architecture docs
   - CLI docs if CLI exists

4. Community infrastructure
   - CONTRIBUTING.md
   - CODE_OF_CONDUCT.md
   - SECURITY.md
   - SUPPORT.md
   - issue templates
   - pull request template
   - discussion topics structure
   - good first issues
   - help wanted issues
   - roadmap milestones
   - community roadmap board
   - changelog
   - governance model
   - contributor recognition strategy

5. Examples
   Create example projects:
   - simple Python CLI
   - simple Python GUI
   - simple Node.js app
   - simple web app
   - minimal project with icon
   - project with tests
   - project with assets
   - broken project for AI fix demo

6. Testing and quality
   Include:
   - unit tests
   - integration tests
   - e2e tests if practical
   - linting
   - formatting
   - type checking if relevant
   - pre-commit hooks
   - code coverage
   - quality gates
   - automated dependency updates
   - security scanning

7. Release excellence
   Include:
   - semantic versioning
   - automated changelog
   - release notes
   - binary downloads
   - checksums
   - SBOM
   - install commands for package managers
   - future support for:
     - PyPI
     - npm
     - Homebrew
     - Scoop
     - Winget
     - Chocolatey
     - Snap
     - Flatpak
     - AUR if appropriate

8. Growth and discoverability
   Include a GitHub Domination Pack:
   - SEO-friendly project description
   - GitHub topics
   - comparison table
   - awesome-list readiness
   - demo script for GIF/video
   - launch checklist
   - Hacker News launch post draft
   - Reddit launch post draft
   - Twitter/X announcement draft
   - Product Hunt description draft
   - developer blog post draft
   - first 20 good-first-issue ideas
   - first 10 plugin ideas for community contributors

====================================================================
PRODUCT EXPERIENCE REQUIREMENTS
====================================================================

The app should feel magical.

Example user journey:

1. User opens AutoForge AI.
2. User drags a Python project folder into the window.
3. The app scans the project.
4. The AI says:
   - Detected Python project
   - Entry point: main.py
   - Dependencies: requests, flask
   - Icon candidate: assets/logo.png
   - Recommended targets: Windows, Linux, macOS
5. User clicks Build All.
6. The app downloads missing tools inside isolated environment.
7. Tests run.
8. Warnings are shown.
9. AI suggests fixes.
10. Final artifacts appear in dist folder.
11. User sees checksums, file sizes, and install instructions.

Error handling must be excellent.
Never show raw cryptic errors without explanation.
Always provide:
- what happened
- why it happened
- how to fix it
- automatic fix option if possible

====================================================================
ARCHITECTURE REQUIREMENTS
====================================================================

Design a clean architecture.

Suggested layers:
- UI layer
- App orchestration layer
- Core engine
- Detection engine
- AI engine
- Build engine
- Sandbox engine
- Adapter/plugin system
- Packaging engine
- Release engine
- Settings/config manager
- Logging/telemetry manager
- Update manager

The architecture must be modular, testable, and plugin-friendly.

Avoid spaghetti automation.
Avoid hardcoding language-specific logic in core.
Avoid making AI a single point of failure.

====================================================================
MVP STRATEGY
====================================================================

Do not try to build everything at once in a fragile way.

Define an MVP that is impressive but realistic.

MVP should include:
- professional desktop UI
- Python project detection
- automatic dependency installation
- isolated build environment
- Windows EXE output
- Linux output if possible
- macOS output if possible
- basic AI metadata extraction
- beautiful README
- GitHub Actions release pipeline
- example project
- plugin architecture skeleton

Post-MVP:
- Node.js adapter
- Go adapter
- Rust adapter
- Android output
- iOS output
- advanced AI auto-fixing
- plugin marketplace
- cloud build runners
- team features
- code signing automation
- notarization automation

====================================================================
EXECUTION PLAN
====================================================================

Proceed through the following phases automatically.

Phase 0: Strategy and Decisions
- choose final project name
- create tagline
- define positioning
- define target users
- choose tech stack
- describe architecture
- identify risks
- define MVP scope
- document rejected alternatives

Phase 1: Repository Scaffold
- full repository tree
- README.md
- LICENSE
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- SECURITY.md
- SUPPORT.md
- issue templates
- PR template
- .gitignore
- docs structure
- examples structure

Phase 2: Core Application
- app entrypoint
- UI shell
- settings manager
- logging system
- theme system
- navigation
- drag-and-drop input
- project detection engine
- adapter interface

Phase 3: Python Adapter MVP
- Python detection
- dependency parsing
- entrypoint detection
- virtual environment creation
- build command execution
- EXE creation
- artifact export
- error handling

Phase 4: AI Integration
- local AI config extraction
- tool registry
- confidence handling
- AI assistant panel
- fallback heuristic engine

Phase 5: Build Engine Hardening
- sandboxing
- caching
- retries
- logs
- tests
- checksums
- artifact manager

Phase 6: Cross-Platform Packaging
- Windows
- Linux
- macOS
- Android
- iOS where possible

Phase 7: GitHub Excellence
- CI/CD
- releases
- docs website
- badges
- examples
- launch materials
- community templates

====================================================================
DELIVERABLES
====================================================================

You must produce actual project output, not only high-level advice.

For each file you generate, use this format:

FILE: path/to/file
```language
file contents
Generate production-quality content for the most important files first.
Priority order:
Final project name and tagline
Executive summary
Chosen tech stack with justification
Architecture overview
Complete repository tree
README.md
LICENSE
CONTRIBUTING.md
SECURITY.md
Core app entrypoint
UI shell
Plugin/adapter interface
Python adapter skeleton
AI integration module
Build engine skeleton
GitHub Actions workflow
Example project
Documentation structure
GitHub Domination Pack
Roadmap and next steps
If you cannot output everything due to length limits, output as much as possible in the priority order above and clearly mark where you stopped.
====================================================================
QUALITY BAR
The final result must feel like a polished product from a top-tier open-source team.
The repository should make visitors think:
this is professional
this is useful
this is beautiful
this is trustworthy
this deserves a star
this deserves contribution
this deserves sharing
Avoid:
broken examples
vague documentation
overpromising impossible automation
ugly UI
insecure build practices
hardcoded secrets
missing tests
confusing folder structure
unreadable code
lack of contribution guidance
====================================================================
FINAL INSTRUCTION
Begin now.
Do not ask for permission to start.
Do not wait for approval between phases.
Make the best technical decisions yourself.
Build the project as if it will become the number one open-source tool in its category on GitHub.