// @ts-check
import { defineConfig, devices } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

// The backend under test and the seed script must share ONE data root, and it
// must never be the live `.terrario`: that root holds locked preregistrations
// and real human decisions, and every E2E seed writes review requests, a lock
// and an execution. It is resolved to an absolute path (the API refuses a
// relative --data-root) and exported so worker processes and the seed script
// see the same value. `.sandbox/` is gitignored. Override for a container.
const E2E_DATA_ROOT = path.resolve(process.env.TERRARIO_E2E_DATA_ROOT || ".sandbox/e2e-data-root");
process.env.TERRARIO_E2E_DATA_ROOT = E2E_DATA_ROOT;
fs.mkdirSync(E2E_DATA_ROOT, { recursive: true });

/**
 * Playwright configuration for the Scientific Visual Workspace E2E suite.
 * A real Terrario backend is started before the tests and torn down after.
 */
export default defineConfig({
  testDir: "./tests_frontend/e2e",
  timeout: 30_000,
  fullyParallel: false,
  workers: 1,
  reporter: [["list"]],
  use: {
    baseURL: "http://127.0.0.1:8877",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    reducedMotion: "reduce",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        // Use the full chromium build (present in the local cache) rather than
        // the separate headless-shell build, which is not downloaded here.
        launchOptions: {
          executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH || undefined,
        },
      },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
      testIgnore: /visual-qa\.spec\.js/,
    },
  ],
  webServer: {
    command: `.venv/bin/python -m terrario.lab.api --root . --host 127.0.0.1 --port 8877 --data-root "${E2E_DATA_ROOT}"`,
    url: "http://127.0.0.1:8877/api/v1/cross-graph",
    reuseExistingServer: false,
    timeout: 30_000,
    env: { PYTHONPATH: ".", TERRARIO_E2E_DATA_ROOT: E2E_DATA_ROOT },
  },
});
