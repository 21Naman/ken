import { expect, test, type Page } from "@playwright/test";
import { spawn, type ChildProcess } from "node:child_process";
import { rm } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const frontendRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = resolve(frontendRoot, "..");
const databasePath = "/tmp/household-agent-playwright-e2e.db";
const backendPort = 8001;
let backend: ChildProcess | undefined;

async function waitForBackend(): Promise<void> {
  const deadline = Date.now() + 30_000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${backendPort}/api/health`);
      if (response.ok) return;
    } catch { /* server is still starting */ }
    await new Promise((resolveDelay) => setTimeout(resolveDelay, 150));
  }
  throw new Error("Timed out waiting for the Playwright backend");
}

async function startBackend(): Promise<void> {
  backend = spawn(join(repositoryRoot, ".venv/bin/uvicorn"), ["app.main:app", "--app-dir", join(repositoryRoot, "backend"), "--host", "127.0.0.1", "--port", String(backendPort)], {
    cwd: repositoryRoot,
    env: { ...process.env, HOUSEHOLD_DATABASE_URL: `sqlite:///${databasePath}`, HF_HUB_OFFLINE: "1" },
    stdio: "pipe",
  });
  await waitForBackend();
}

async function stopBackend(): Promise<void> {
  if (!backend || backend.exitCode !== null) return;
  const exited = new Promise<void>((resolveExit) => backend?.once("exit", () => resolveExit()));
  backend.kill("SIGTERM");
  await exited;
}

const labels = {
  expiry_routine: "expiry routine",
  preference_conflict: "preference conflict",
  guests: "guests",
  cook_mishap: "cook mishap",
  feedback_learning: "feedback learning",
  budget_constraint: "budget constraint",
} as const;

async function resetScenario(page: Page, scenario: keyof typeof labels): Promise<void> {
  await page.goto("/");
  await page.getByLabel("Demo scenario").selectOption(scenario);
  await page.getByRole("button", { name: "Reset selected demo" }).click();
  await expect(page.getByRole("status")).toContainText(`${labels[scenario]} demo fixture was reset.`);
}

test.describe.configure({ mode: "serial" });
test.beforeAll(async () => {
  await rm(databasePath, { force: true });
  await startBackend();
});
test.afterAll(async () => {
  await stopBackend();
  await rm(databasePath, { force: true });
});

test("expiry: UI shows carrot-led recommendation and green audited completion", async ({ page }) => {
  await resetScenario(page, "expiry_routine");
  await page.getByRole("button", { name: "Plan routine dinner" }).click();
  await expect(page.getByText(/Why this score:.*expiry use: carrot/)).toBeVisible();
  const loop = page.getByRole("article", { name: /timeline/ });
  await expect(loop).toContainText("local task created");
  await expect(loop).toContainText("Autonomy: green");
  await expect(loop).toContainText("completed");
});

test("preference conflict: UI surfaces safety exclusion and red approval", async ({ page }) => {
  await resetScenario(page, "preference_conflict");
  await page.getByRole("button", { name: "Plan routine dinner" }).click();
  await expect(page.getByText(/Excluded:.*Paneer Bhurji \(allergen present: paneer\)/)).toBeVisible();
  const loop = page.getByRole("article", { name: /timeline/ });
  await expect(loop).toContainText("approval requested");
  await expect(loop).toContainText("Autonomy: red");
  await expect(loop).toContainText("pending");
});

test("guests: UI renders the guest-arrival trigger", async ({ page }) => {
  await resetScenario(page, "guests");
  const loop = page.getByRole("article", { name: /timeline/ });
  await expect(loop).toContainText("Trigger: guest arrival");
  await expect(loop).toContainText("triggered — guest_arrival");
});

test("mishap recovery: UI renders the stocked recovery path in progress", async ({ page }) => {
  await resetScenario(page, "cook_mishap");
  await page.getByRole("button", { name: "Plan routine dinner" }).click();
  await expect(page.getByText(/Vegetable Khichdi.*route: use stock/)).toBeVisible();
  const loop = page.getByRole("article", { name: /timeline/ });
  await expect(loop).toContainText("recovery plan");
  await expect(loop).toContainText("recovery in progress");
});

test("feedback learning: UI renders completed feedback memory with the later plan", async ({ page }) => {
  await resetScenario(page, "feedback_learning");
  await page.getByRole("button", { name: "Plan routine dinner" }).click();
  const loop = page.getByRole("article", { name: /timeline/ });
  await expect(loop).toContainText("Paneer Bhurji — Too heavy");
  await expect(loop).toContainText("Prefer light dinners after paneer felt too heavy");
  await expect(page.getByText(/Vegetable Khichdi · score/)).toBeVisible();
});

test("budget constraint: UI displays the over-cap manual basket and lower-cost route", async ({ page }) => {
  await resetScenario(page, "budget_constraint");
  await page.getByRole("button", { name: "Plan routine dinner" }).click();
  await expect(page.getByText(/Paneer Bhurji · score.*route: manual purchase · ₹137/)).toBeVisible();
  await expect(page.getByText(/Vegetable Khichdi · score.*route: simulated order · ₹88/)).toBeVisible();
  await expect(page.getByRole("article", { name: /timeline/ })).toContainText("Autonomy: yellow");
});

test("failure states: UI keeps local fallbacks visible during an expiry scenario", async ({ page }) => {
  await page.route("**/api/health", (route) => route.fulfill({ json: { status: "ok", database: { status: "available" }, ollama: { status: "unavailable", model: "qwen3:4b", detail: "Ollama intentionally disabled" }, scheduler: { status: "unavailable", detail: "Scheduler intentionally disabled; use the manual trigger instead." } } }));
  await resetScenario(page, "expiry_routine");
  await expect(page.getByText("Ollama intentionally disabled")).toBeVisible();
  await expect(page.getByText("Scheduler intentionally disabled; use the manual trigger instead.")).toBeVisible();
  await page.getByRole("button", { name: "inventory" }).click();
  await page.route("**/capture/audio", (route) => route.fulfill({ json: { source: "audio", transcript: null, language: null, candidates: [], requires_confirmation: true, fallback: "faster-whisper intentionally disabled; use typed inventory entry", warning: null } }));
  await page.route("**/capture/image", (route) => route.fulfill({ json: { source: "image", transcript: null, language: null, candidates: [], requires_confirmation: true, fallback: "Vision provider intentionally disabled; use typed inventory entry", warning: null } }));
  await page.getByLabel("Voice note").setInputFiles({ name: "note.aac", mimeType: "audio/aac", buffer: Buffer.from("voice") });
  await expect(page.getByText("faster-whisper intentionally disabled; use typed inventory entry")).toBeVisible();
  await page.getByLabel("Fridge photo").setInputFiles({ name: "fridge.jpg", mimeType: "image/jpeg", buffer: Buffer.from("photo") });
  await expect(page.getByText("Vision provider intentionally disabled; use typed inventory entry")).toBeVisible();
  await expect(page.getByRole("button", { name: "Add inventory" })).toBeVisible();
});

test("restart persistence: feedback memory survives a backend restart", async ({ page }) => {
  await resetScenario(page, "feedback_learning");
  await page.getByRole("button", { name: "memory" }).click();
  await expect(page.getByRole("listitem").filter({ hasText: "Paneer Bhurji" })).toContainText("Too heavy");
  await stopBackend();
  await startBackend();
  await page.reload();
  await expect(page.getByRole("status")).toHaveText("Persistent household memory is loaded.");
  await page.getByRole("button", { name: "memory" }).click();
  await expect(page.getByRole("listitem").filter({ hasText: "Paneer Bhurji" })).toContainText("Too heavy");
  await expect(page.getByText("Prefer light dinners after paneer felt too heavy")).toBeVisible();
});
