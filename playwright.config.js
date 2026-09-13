// @ts-check
import { defineConfig, devices } from "@playwright/test";

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
  ],
  webServer: {
    command: ".venv/bin/python -m terrario.lab.api --root . --host 127.0.0.1 --port 8877",
    url: "http://127.0.0.1:8877/api/v1/cross-graph",
    reuseExistingServer: false,
    timeout: 30_000,
    env: { PYTHONPATH: "." },
  },
});
