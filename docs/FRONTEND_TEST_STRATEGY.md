# Frontend test strategy

The workspace is tested at four levels, each with a distinct purpose. This phase resolves the historical visual-QA parking by running real browser tests.

## Frontend unit tests (`node --test`)

Fast, browser-free tests of pure logic: state model (store immutability, subscribe/unsubscribe), command journal (undo/redo, canonical rejection), domain visual language (shape+icon+label, never color-only), claim-type labels, operating-mode distinction, error-class coverage, and GraphSlice merge transforms (dedup of nodes/edges/hyperedges, key parsing). Run with `npm run test:unit`.

## API contract tests (Playwright request)

Verify the backend responses match the frontend typed contracts (`core/contracts.js`): cross-graph status envelope, GraphSlice typedef, ReferenceRecord typedef, TraceBreak typedef, and typed error envelopes (no plain "Error"). These catch backend/frontend drift automatically.

## Browser E2E (Playwright + real Terrario backend)

Real browser tests against a live backend (started by the Playwright `webServer`): workspace launch, panel mounting, canvas render, command palette, zoom/selection, composition save, D2 trace-break layer, World2D three-view labelling and sandbox badge, operating-mode toggle, and reload/recovery. Run with `npm run test:e2e`.

## Visual QA + accessibility QA

- **Visual QA** — stable screenshot baselines for the workspace shell, World2D panel, and D2 Studio (structural baselines; not all tests rely on screenshots).
- **Accessibility QA** — semantic panel labels, canvas accessible label, keyboard-focusable controls, non-color-only domain distinctions (icons/shapes), and `prefers-reduced-motion` honored.

## Render benchmarks

A Playwright benchmark drives the canvas renderer with synthetic 1k and 10k visible-node graphs and reports render duration, pan latency, approximate FPS, and JS heap. Real numbers are reported; there is no fixed "feels fast" threshold.

## Backend integrity firewalls

Python tests (`tests/test_workspace_firewall.py`) verify before/after that workspace read paths and composition saves never modify the TheoryGraph, ReferenceGraph, EvidenceGraph, or locked preregistrations, never create canonical links from composition-local ones, and never expose an execution/evidence route.
