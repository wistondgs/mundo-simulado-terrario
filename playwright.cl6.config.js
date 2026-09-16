import { defineConfig, devices } from "@playwright/test";

// CL-6 runs against an explicitly started Lab instance with a temporary data-root.
export default defineConfig({
  testDir: "./tests_frontend/e2e",
  timeout: 30_000,
  workers: 1,
  reporter: [["list"]],
  use: { baseURL: process.env.CL6_BASE_URL || "http://127.0.0.1:8877", screenshot: "only-on-failure" },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
  ],
});
