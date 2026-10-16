---
name: build-simple-durable-systems
description: Design, implement, or refactor software toward the simplest durable architecture for current requirements. Use when building a feature or system, evaluating architecture, removing obsolete behavior, avoiding speculative complexity, choosing between custom code and dependencies, or planning incremental end-to-end delivery without backward-compatibility layers.
---

# Build Simple Durable Systems

Apply these principles to architecture, planning, implementation, and review:

- Do not preserve backward compatibility. Remove obsolete paths instead of adding compatibility layers, fallbacks, or migrations.
- Choose the simplest implementation that fully meets the current requirements. Avoid speculative abstractions, configuration, and indirection.
- Grow the system in layers. Start with the smallest version that works end to end, then add each capability on top of a working product. Never trade a working product for unfinished complexity.
- Keep components modular and concerns clearly separated.
- Prefer established, well-maintained libraries when they reduce overall complexity or improve reliability. Do not reimplement common functionality without a clear reason.
- Inspect the project's existing dependencies, their documentation, and their types before writing custom code or adding packages. Do not assume a dependency lacks a capability without checking.
- Make architectural decisions for the long term. Reject stopgaps intended to be replaced later.
- Study how established products solve the problem before designing a solution. Adopt proven patterns and conventions instead of inventing an approach from scratch.

State any conflict between these principles and an explicit user requirement before proceeding. Treat the explicit requirement as authoritative.
