// @ts-check
import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";

/**
 * SCIENTIFIC-LIVE-OBSERVABILITY-01 golden path.
 * Real backend, real dispatcher, real ScientificTrialRuntime; no mocked transport.
 */
function seed() {
  const out = execFileSync(".venv/bin/python", ["scripts/seed_scientific_live_e2e.py", ".terrario"],
    { encoding: "utf8", env: { ...process.env, PYTHONPATH: "." } });
  return JSON.parse(out.trim().split("\n").pop());
}

async function startAndDispatch(request, exec) {
  const session = await (await request.get("/api/v1/session")).json();
  const auth = { "X-CSRF-Token": session.data.csrf_token };
  const started = await request.post(`/api/v1/scientific-executions/${exec.execution_id}/commands`, {
    headers: auth, data: { command: "START", command_id: "e2e-golden-start", expected_revision: exec.revision } });
  expect(started.ok()).toBeTruthy();
  const dispatched = await request.post(`/api/v1/scientific-executions/${exec.execution_id}/dispatch`, {
    headers: auth, data: { worker_id: "e2e-worker" } });
  expect(dispatched.ok()).toBeTruthy();
  return auth;
}

async function attemptOf(request, executionId) {
  const response = await (await request.get(`/api/v1/scientific-executions/${executionId}`)).json();
  const artifacts = response.data.artifacts.filter((a) => a.artifact_type === "SCIENTIFIC_TRACE");
  expect(artifacts.length).toBeGreaterThan(0);
  return artifacts[0];
}

test.describe("Scientific live observability", () => {
  test("golden: live frames -> SSE -> reconnect -> terminal -> durable CAS playback", async ({ page, request }) => {
    const exec = seed();
    const auth = await startAndDispatch(request, exec);
    const trace = await attemptOf(request, exec.execution_id);
    const trialId = trace.trial_intent_id, attemptId = trace.attempt_id;

    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1200);
    const panel = page.locator('[data-panel="scientific-world"]');
    await panel.locator("#swExec").fill(exec.execution_id);
    await panel.locator("#swTrial").fill(trialId);
    await panel.locator("#swAttempt").fill(attemptId);
    await panel.locator("#swLive").click();

    // Terminal attempt attaches as TERMINAL with authoritative provenance.
    await expect(panel.locator("#swMode")).toHaveText("SCIENTIFIC · TERMINAL", { timeout: 10_000 });
    const provenance = await panel.locator("#swProv").textContent();
    expect(provenance).toContain(exec.execution_id);
    expect(provenance).toContain(attemptId);
    expect(provenance).toContain(exec.plan_hash);
    expect(provenance).toContain("CAS_SEALED");
    await expect(panel.locator("#swViews")).toContainText("frame 100 · COMPLETED");

    // Durable CAS playback with seek; provenance remains identical.
    await panel.locator("#swOpen").click();
    await expect(panel.locator("#swMode")).toHaveText("SCIENTIFIC · PLAYBACK", { timeout: 10_000 });
    await expect(panel.locator("#swSeekLabel")).toContainText("frame 0");
    await expect(panel.locator("#swViews")).toContainText("Tick 0");
    await panel.locator("#swNext").click();
    await expect(panel.locator("#swSeekLabel")).toContainText("frame 1");
    const playbackProvenance = await panel.locator("#swProv").textContent();
    expect(playbackProvenance).toContain(exec.plan_hash);
    expect(playbackProvenance).toContain(attemptId);

    // Read-only: no experimental-control surface.
    for (const name of ["Start", "Step", "Pause", "Resume", "Reset", "Seed", "Intervention"]) {
      await expect(panel.getByRole("button", { name: new RegExp(`^${name}$`, "i") })).toHaveCount(0);
    }
    // Engineering sandbox remains separately labeled.
    const worldPanel = page.locator('[data-panel="world"]');
    await expect(worldPanel.locator(".ws-sandbox-badge")).toContainText("ENGINEERING_SANDBOX · NOT EVIDENCE");
  });

  test("live SSE stream delivers tick 0, later frames, and terminal event", async ({ page, request }) => {
    const exec = seed();
    const auth = await startAndDispatch(request, exec);
    const trace = await attemptOf(request, exec.execution_id);
    await page.goto("/workspace/index.html");
    const result = await page.evaluate(async ({ url, csrf }) => {
      const response = await fetch(url, { headers: { "X-CSRF-Token": csrf } });
      const reader = response.body.getReader(), decoder = new TextDecoder();
      let buffer = "", frames = 0, sawTick0 = false, terminal = null, contentType = response.headers.get("content-type");
      const deadline = Date.now() + 10000;
      while (Date.now() < deadline) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let boundary;
        while ((boundary = buffer.indexOf("\n\n")) >= 0) {
          const block = buffer.slice(0, boundary); buffer = buffer.slice(boundary + 2);
          const eventLine = block.split("\n").find((l) => l.startsWith("event: "));
          const dataLine = block.split("\n").find((l) => l.startsWith("data: "));
          if (!dataLine) continue;
          const kind = eventLine ? eventLine.slice(7).trim() : "FRAME";
          const payload = JSON.parse(dataLine.slice(6));
          if (kind === "FRAME") { frames++; if (payload.frame_sequence === 0 && payload.tick === 0) sawTick0 = true; }
          if (kind === "TERMINAL") terminal = payload;
        }
        if (terminal) break;
      }
      return { contentType, frames, sawTick0, terminal };
    }, { url: `/api/v1/scientific-executions/${exec.execution_id}/trials/${trace.trial_intent_id}/live/stream?attempt_id=${trace.attempt_id}&after_sequence=-1`, csrf: auth["X-CSRF-Token"] });
    expect(result.contentType).toContain("text/event-stream");
    expect(result.sawTick0).toBeTruthy();
    expect(result.frames).toBeGreaterThan(1);
    expect(result.terminal).toBeTruthy();
    expect(result.terminal.artifact_state).toBe("CAS_SEALED");
  });

  test("stale cursor yields explicit RESYNC_REQUIRED, never a silent jump", async ({ request }) => {
    const exec = seed();
    const auth = await startAndDispatch(request, exec);
    const trace = await attemptOf(request, exec.execution_id);
    // A cursor bound to a different attempt is rejected closed before streaming.
    const wrongAttempt = await request.get(
      `/api/v1/scientific-executions/${exec.execution_id}/trials/${trace.trial_intent_id}/live/stream?attempt_id=${trace.attempt_id}&after_sequence=0&cursor_attempt_id=forged`,
      { headers: auth });
    expect(wrongAttempt.status()).toBe(400);
    expect(await wrongAttempt.text()).toContain("CURSOR_WRONG_ATTEMPT");
  });

  test("cross-trial isolation is enforced on the live route", async ({ request }) => {
    const exec = seed();
    const auth = await startAndDispatch(request, exec);
    const trace = await attemptOf(request, exec.execution_id);
    const response = await request.get(
      `/api/v1/scientific-executions/${exec.execution_id}/trials/${trace.trial_intent_id}/live?attempt_id=forged-attempt`,
      { headers: auth });
    expect(response.status()).toBe(404);
  });
});
