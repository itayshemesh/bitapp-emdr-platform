# Bi-Tapp EMDR Platform (`bitapp-emdr-platform`)

A two-layer open-source architecture combining:
1. **Layer 1 — Generic Framework (`framework/bls_protocol_engine/`)**: A reusable, domain-agnostic 8-Phase Bilateral Stimulation (BLS) & EMDR state-machine engine with a **Two-Stage Safety Circuit Breaker** (Levels `1–6` normal solo mode, Level `7` caution prompt with user choice, Levels `8–10` or `3` stalled rounds automatic stop to calming mode), pluggable hardware adapters (Exact Starting Number + Comfortable Range), and zero-repo-secret Google OAuth 2.0 session journaling.
2. **Layer 2 — Specific Bi-Tapp Personal EMDR Application (`apps/bitapp_personal_emdr/`)**: A personal self-regulation and EMDR companion configured for the **[Bi-Tapp](https://bi-tapp.com/)** Bluetooth tactile tappers, implementing a **Solo-First (Weeks 1–4) $\rightarrow$ Human Backup If Stuck** roadmap for:
   - **2.5-Year Ex-Partner Breakup Rumination ("Mini-Trauma")**: On-demand loop interruption (`Start: Speed 2, Intensity 3, 10m | Range: Speed 1–3, Intensity 2–4, 5–15m`) and weekly memory processing (`Start: Speed 7, Intensity 6, 35s rounds | Range: Speed 6–8, Intensity 5–7, 30–45s rounds`).
   - **Living Apart From 3 Children**: Daily Phase 2 Resource Development & Installation (`Start: Speed 3, Intensity 3, 20s rounds | Range: Speed 2–4, Intensity 2–4, 15–20s rounds`) and optional `remotEMDR` 5-character provider code handoff.
   - **Session Installation & Closure (Modes D1 & D2)**: Positive belief installation (`Start: Speed 4, Intensity 4, 25s rounds | Range: Speed 4–5, Intensity 3–4, 20–30s rounds`) and mandatory calming session closure (`Start: Speed 2, Intensity 3, 60s | Range: Speed 1–3, Intensity 2–4, 60–120s`).

## Single Source of Truth — Unified Master Plan
* **[Unified Master Plan & Clinical Guide (`docs/MASTER_PLAN.md`)](docs/MASTER_PLAN.md)**: Complete plain-English explanation, Day-1 phone & buzzer setup, Bi-Tapp hardware & pricing breakdown, Solo-First vs. Human Telehealth comparison, exact Bi-Tapp settings + comfortable ranges, weekly schedule, and software architecture.

## Day-1 Setup FAQ (Phone & Website)
1. **Do I need a phone?** **Yes, for the physical Bi-Tapp buzzers.** The tappers only have a single power button on the casing; you pair them via Bluetooth to the free **Bi-Tapp** app on iOS/Android to adjust the **Speed (`1–10`)** and **Intensity (`1–10`)** sliders. Our Python companion app runs on your computer right next to your phone and tells you the exact slider numbers for each step.
2. **Do I need to register a website or account?** **No.** Zero websites, domains, or accounts are required (`VirtualEMDR.com` is not needed, and even if you hire a human therapist in Week 5+, only the therapist has a `remotEMDR.com` account — you just read them the 5-character code from your Bi-Tapp phone app).

## Quick Start & How to Run

```bash
# 1. LIVE INTERACTIVE COACH (Use this for your real weekly 35-45 min solo EMDR sessions):
PYTHONPATH=. python3 -m apps.bitapp_personal_emdr.cli --mode=interactive

# 2. ON-DEMAND RUMINATION INTERRUPTER (Immediate 3-step guide: Speed 2, Intensity 3, 10m):
PYTHONPATH=. python3 -m apps.bitapp_personal_emdr.cli --mode=loop-interrupt

# 3. FULL CHEAT SHEET & COST SUMMARY (All 5 Bi-Tapp presets, ranges, and Solo-First schedule):
PYTHONPATH=. python3 -m apps.bitapp_personal_emdr.cli --mode=summary

# 4. AUTOMATED DEMO SESSION (Runs a simulated 8-phase session end-to-end):
PYTHONPATH=. python3 -m apps.bitapp_personal_emdr.cli --mode=simulate-session

# 5. RUN AUTOMATED UNIT TESTS:
PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py" -v
```
