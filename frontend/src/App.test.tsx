import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";

const household = { id: 7, name: "Test Home", default_language: "English", created_at: "2026-09-12" };
const json = (payload: unknown) => new Response(JSON.stringify(payload), { status: 200, headers: { "Content-Type": "application/json" } });

describe("household UI", () => {
  afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

  it("renders the seeded household and its inventory screen", async () => {
    vi.stubGlobal("fetch", vi.fn((url: string) => {
      if (url.endsWith("/health")) return Promise.resolve(json({ status: "ok", database: { status: "available" }, ollama: { status: "available", model: "qwen3:4b", detail: null }, scheduler: { status: "available", detail: null } }));
      if (url.endsWith("/households")) return Promise.resolve(json([household]));
      if (url.includes("/members")) return Promise.resolve(json([]));
      if (url.includes("/cook-profile") || url.includes("/budget")) return Promise.resolve(json(null));
      if (url.includes("/inventory")) return Promise.resolve(json([{ id: 3, ingredient: "carrot", quantity: 2, unit: "piece", expiry_date: "2026-09-13", storage_location: "fridge", confirmed: true, expiry_status: "expiring_soon" }]));
      if (url.includes("/leftovers") || url.includes("/history") || url.includes("/preferences") || url.includes("/meal-loops") || url.includes("/audit") || url.includes("/approvals")) return Promise.resolve(json([]));
      return Promise.resolve(json({}));
    }));
    render(<App />);
    await screen.findByText("Persistent household memory is loaded.");
    fireEvent.click(screen.getByRole("button", { name: "inventory" }));
    await waitFor(() => expect(screen.getByText("carrot")).toBeTruthy());
    expect(screen.getByText("expiring soon")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Add inventory" })).toBeTruthy();
  });

  it("previews an uploaded fridge photo and requires an explicit confirmation", async () => {
    const fetchMock = vi.fn((url: string) => {
      if (url.endsWith("/health")) return Promise.resolve(json({ status: "ok", database: { status: "available" }, ollama: { status: "available", model: "qwen3:4b", detail: null }, scheduler: { status: "available", detail: null } }));
      if (url.endsWith("/households")) return Promise.resolve(json([household]));
      if (url.endsWith("/capture/image")) return Promise.resolve(json({ source: "image", transcript: null, language: null, candidates: [{ ingredient: "milk", quantity: 1, unit: "packet", expiry_date: null, storage_location: "fridge", readability_confidence: 0.2 }], requires_confirmation: true, fallback: null }));
      if (url.endsWith("/capture/confirm")) return Promise.resolve(json({ id: 9, ingredient: "milk", quantity: 1, unit: "packet", expiry_date: null, storage_location: "fridge", confirmed: true, expiry_status: "unknown" }));
      if (url.includes("/members")) return Promise.resolve(json([]));
      if (url.includes("/cook-profile") || url.includes("/budget")) return Promise.resolve(json(null));
      if (url.includes("/inventory")) return Promise.resolve(json([]));
      if (url.includes("/leftovers") || url.includes("/history") || url.includes("/preferences") || url.includes("/meal-loops") || url.includes("/audit") || url.includes("/approvals")) return Promise.resolve(json([]));
      return Promise.resolve(json({}));
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);
    await screen.findByText("Persistent household memory is loaded.");
    fireEvent.click(screen.getByRole("button", { name: "inventory" }));
    const photo = new File(["local-image"], "fridge.jpg", { type: "image/jpeg" });
    fireEvent.change(screen.getByLabelText("Fridge photo"), { target: { files: [photo] } });
    await screen.findByRole("region", { name: "Capture review" });
    expect(screen.getByText("readability confidence 20%")).toBeTruthy();
    const ingredient = screen.getByLabelText("Ingredient") as HTMLInputElement;
    expect(ingredient.value).toBe("milk");
    fireEvent.change(ingredient, { target: { value: "curd" } });
    expect(ingredient.value).toBe("curd");
    fireEvent.click(screen.getByRole("button", { name: "Confirm capture" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/capture/confirm"), expect.objectContaining({ method: "POST" })));
  });

  it("shows a voice transcript in an editable review field before any confirmation", async () => {
    vi.stubGlobal("fetch", vi.fn((url: string) => {
      if (url.endsWith("/health")) return Promise.resolve(json({ status: "ok", database: { status: "available" }, ollama: { status: "available", model: "qwen3:4b", detail: null }, scheduler: { status: "available", detail: null } }));
      if (url.endsWith("/households")) return Promise.resolve(json([household]));
      if (url.endsWith("/capture/audio")) return Promise.resolve(json({ source: "audio", transcript: "do tamatar fridge mein daalo", language: "hi", candidates: [], requires_confirmation: true, fallback: null, warning: null }));
      if (url.includes("/members")) return Promise.resolve(json([]));
      if (url.includes("/cook-profile") || url.includes("/budget")) return Promise.resolve(json(null));
      if (url.includes("/inventory") || url.includes("/leftovers") || url.includes("/history") || url.includes("/preferences") || url.includes("/meal-loops") || url.includes("/audit") || url.includes("/approvals")) return Promise.resolve(json([]));
      return Promise.resolve(json({}));
    }));
    render(<App />);
    await screen.findByText("Persistent household memory is loaded.");
    fireEvent.click(screen.getByRole("button", { name: "inventory" }));
    fireEvent.change(screen.getByLabelText("Voice note"), { target: { files: [new File(["voice"], "note.aac", { type: "audio/aac" })] } });
    const transcript = await screen.findByLabelText("Editable transcript") as HTMLTextAreaElement;
    expect(transcript.value).toBe("do tamatar fridge mein daalo");
    fireEvent.change(transcript, { target: { value: "add two tomatoes to the fridge" } });
    expect(transcript.value).toBe("add two tomatoes to the fridge");
    expect(screen.getByText("Detected language: hi")).toBeTruthy();
  });

  it("renders the exact API score, gap, and procurement explanation without recomputing it", async () => {
    vi.stubGlobal("fetch", vi.fn((url: string) => {
      const path = String(url);
      if (path.endsWith("/health")) return Promise.resolve(json({ status: "ok", database: { status: "available" }, ollama: { status: "available", model: "qwen3:4b", detail: null }, scheduler: { status: "available", detail: null } }));
      if (path.endsWith("/households")) return Promise.resolve(json([household]));
      if (path.endsWith("/plan")) return Promise.resolve(json({ context: { servings: 2, available_minutes: 45, urgency: "routine" }, recommendations: [{ dish: "Vegetable Khichdi", score: 54, prep_minutes: 35, score_explanation: { expiry_use: ["carrot"], leftover_use: ["Moong Dal"], novelty: "recently served penalty", gaps: 1 }, missing_ingredients: [{ ingredient: "moong dal", needed: 0.33, available: 0, shortfall: 0.33, unit: "cup", substitution: "masoor dal" }], procurement: { route: "simulated_order", estimated_cost_inr: 88, reason: "The seeded basket is within budget." } }], exclusions: [{ dish: "Peanut Noodles", reasons: ["allergen present: peanuts"] }] }));
      if (path.includes("/members") || path.includes("/inventory") || path.includes("/leftovers") || path.includes("/history") || path.includes("/preferences") || path.includes("/meal-loops") || path.includes("/audit") || path.includes("/approvals")) return Promise.resolve(json([]));
      if (path.includes("/cook-profile") || path.includes("/budget")) return Promise.resolve(json(null));
      return Promise.resolve(json({}));
    }));
    render(<App />);
    await screen.findByText("Persistent household memory is loaded.");
    fireEvent.click(screen.getByRole("button", { name: "Plan routine dinner" }));
    await screen.findByText("Vegetable Khichdi · score 54");
    const exactParagraph = (text: string) => screen.getByText((_, element) => element?.tagName === "P" && element.textContent === text);
    expect(exactParagraph("Why this score: expiry use: carrot; leftovers: Moong Dal; novelty: recently served penalty; ingredient gaps: 1.")).toBeTruthy();
    expect(exactParagraph("Gaps: moong dal (0.33 cup short; 0/0.33 available/needed; substitute masoor dal)")).toBeTruthy();
    expect(exactParagraph("Procurement rationale: The seeded basket is within budget.")).toBeTruthy();
  });

  it("visibly reports unavailable Ollama and scheduler services", async () => {
    vi.stubGlobal("fetch", vi.fn((url: string) => {
      const path = String(url);
      if (path.endsWith("/health")) return Promise.resolve(json({ status: "ok", database: { status: "available" }, ollama: { status: "unavailable", model: "qwen3:4b", detail: "Connection refused" }, scheduler: { status: "unavailable", detail: "Automatic local triggers are unavailable; use the manual trigger instead." } }));
      if (path.endsWith("/households")) return Promise.resolve(json([household]));
      if (path.includes("/cook-profile") || path.includes("/budget")) return Promise.resolve(json(null));
      if (path.includes("/members") || path.includes("/inventory") || path.includes("/leftovers") || path.includes("/history") || path.includes("/preferences") || path.includes("/meal-loops") || path.includes("/audit") || path.includes("/approvals")) return Promise.resolve(json([]));
      return Promise.resolve(json({}));
    }));
    render(<App />);
    await screen.findByText("Connection refused");
    expect(screen.getByText("Automatic local triggers are unavailable; use the manual trigger instead.")).toBeTruthy();
  });

  it("shows typed-entry fallbacks for unavailable Whisper and vision providers", async () => {
    vi.stubGlobal("fetch", vi.fn((url: string) => {
      const path = String(url);
      if (path.endsWith("/health")) return Promise.resolve(json({ status: "ok", database: { status: "available" }, ollama: { status: "available", model: "qwen3:4b", detail: null }, scheduler: { status: "available", detail: null } }));
      if (path.endsWith("/households")) return Promise.resolve(json([household]));
      if (path.endsWith("/capture/audio")) return Promise.resolve(json({ source: "audio", transcript: null, language: null, candidates: [], requires_confirmation: true, fallback: "faster-whisper is unavailable; use typed inventory entry", warning: null }));
      if (path.endsWith("/capture/image")) return Promise.resolve(json({ source: "image", transcript: null, language: null, candidates: [], requires_confirmation: true, fallback: "Local vision model is unavailable; use typed inventory entry", warning: null }));
      if (path.includes("/cook-profile") || path.includes("/budget")) return Promise.resolve(json(null));
      if (path.includes("/members") || path.includes("/inventory") || path.includes("/leftovers") || path.includes("/history") || path.includes("/preferences") || path.includes("/meal-loops") || path.includes("/audit") || path.includes("/approvals")) return Promise.resolve(json([]));
      return Promise.resolve(json({}));
    }));
    render(<App />);
    await screen.findByText("Persistent household memory is loaded.");
    fireEvent.click(screen.getByRole("button", { name: "inventory" }));
    fireEvent.change(screen.getByLabelText("Voice note"), { target: { files: [new File(["voice"], "note.aac", { type: "audio/aac" })] } });
    await screen.findByText("faster-whisper is unavailable; use typed inventory entry");
    fireEvent.change(screen.getByLabelText("Fridge photo"), { target: { files: [new File(["image"], "fridge.jpg", { type: "image/jpeg" })] } });
    await screen.findByText("Local vision model is unavailable; use typed inventory entry");
    expect(screen.getByRole("button", { name: "Add inventory" })).toBeTruthy();
  });
});
