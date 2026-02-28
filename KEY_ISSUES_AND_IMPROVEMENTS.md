# Key Issues & Improvements (Remaining)

This file captures the remaining high-impact issues identified during MCP server review (excluding the already-addressed `batch_generate` parity gap).

## 1) Server config values are not applied
- `transport`, `host`, `port`, `log_level`, and `log_format` are defined but not used when starting the server.
- `app.run()` currently ignores these settings.

## 2) Versioning and product naming are inconsistent
- Version values conflict across code and packaging (for example, `__version__`, server version string, and package version).
- Naming is mixed across "Gemini 3 Pro" vs "Gemini 3.1 Flash" in places.

## 3) `output_format` is effectively a no-op
- The parameter is validated but not actually used in generation/output conversion.
- Saved output pathing/encoding behavior still defaults to PNG behavior.

## 4) Validation and safety checks are incomplete
- Existing size/file validation helpers are not consistently enforced on reference inputs.
- Reference images are only weakly validated (e.g., existence/count), which can allow oversized or invalid files.

## 5) Filename collision risk
- Generated filenames rely on prompt slug + second-level timestamp.
- Concurrent requests can collide and overwrite files.

## 6) Async loop call pattern is outdated
- `asyncio.get_event_loop()` is used inside async flows.
- Prefer `asyncio.get_running_loop()` or `asyncio.to_thread()` patterns.

## 7) Prompt policy inconsistency
- Prompt-enhancement guidance forbids hex colors, but at least one template includes a hex color literal.
- This creates conflicting behavior and weaker policy adherence.

## Suggested next implementation order
1. Wire server runtime/logging config into startup path.
2. Resolve version + naming consistency in all exported surfaces.
3. Implement true `output_format` handling end-to-end.
4. Enforce strict reference image validation (type/size/content).
5. Make filenames collision-safe (UUID or higher-resolution timestamp).
6. Modernize async execution helpers.
7. Align prompt templates with enhancement policy.
