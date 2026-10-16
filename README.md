# Bi-Tapp EMDR Platform (`bitapp-emdr-platform`)

A simple, local two-layer Python toolkit combining:
1. **Layer 1 — Generic Framework (`framework/bls_protocol_engine/`)**: A reusable 8-Phase Bilateral Stimulation (BLS) & EMDR state-machine engine with a **Two-Stage Safety Circuit Breaker** (`Pain 1–6` normal solo mode, `Pain 7` caution prompt with your choice, `Pain 8–10` or `3` stalled rounds automatic stop to calming mode), pluggable hardware adapters (Exact Starting Number + Comfortable Range), and private local JSONL session logging.
2. **Layer 2 — Specific Bi-Tapp Personal EMDR Application (`apps/bitapp_personal_emdr/`)**: A personal self-regulation and EMDR coach configured for the **[Bi-Tapp](https://bi-tapp.com/)** Bluetooth tactile tappers, implementing a **Solo-First (Weeks 1–4, `$0`/mo) $\rightarrow$ Human Backup If Stuck** roadmap for:
   - **2.5-Year Ex-Partner Breakup Rumination ("Mini-Trauma")**: On-demand loop interruption (`Start: Speed 2, Intensity 3, 10m | Range: Speed 1–3, Intensity 2–4, 5–15m`) and weekly memory processing (`Start: Speed 7, Intensity 6, 35s rounds | Range: Speed 6–8, Intensity 5–7, 30–45s rounds`).
   - **Living Apart From 3 Children**: Daily Phase 2 Resource Development & Installation (`Start: Speed 3, Intensity 3, 20s rounds | Range: Speed 2–4, Intensity 2–4, 15–20s rounds`) and optional `remotEMDR` 5-character provider code handoff.
   - **Session Installation & Closure (Modes D1 & D2)**: Positive belief installation (`Start: Speed 4, Intensity 4, 25s rounds | Range: Speed 4–5, Intensity 3–4, 20–30s rounds`) and mandatory calming session closure (`Start: Speed 2, Intensity 3, 60s | Range: Speed 1–3, Intensity 2–4, 60–120s`).

## Single Source of Truth — Unified Master Plan
* **[Unified Master Plan & Clinical Guide (`docs/MASTER_PLAN.md`)](docs/MASTER_PLAN.md)**: Complete plain-English explanation, Day-1 phone & buzzer setup, Bi-Tapp hardware & pricing breakdown, Solo-First vs. Human Telehealth comparison, exact Bi-Tapp settings + comfortable ranges, meditation video & bedtime sleep rules, weekly schedule, and software architecture.

## Day-1 Setup, Meditation & Sleep FAQ
1. **Do I need a phone?** **Yes, for the physical Bi-Tapp buzzers.** The tappers only have a single power button on the casing; you pair them via Bluetooth to the free **Bi-Tapp** app on iOS/Android to adjust the **Speed (`1–10`)** and **Intensity (`1–10`)** sliders. Our Python companion app runs on your computer right next to your phone and tells you the exact slider numbers for each step.
2. **Do I need to register a website or account?** **No.** Zero websites, domains, or accounts are required (`VirtualEMDR.com` is not needed, and even if you hire a human therapist in Week 5+, only the therapist has a `remotEMDR.com` account — you just read them the 5-character code from your Bi-Tapp phone app).
3. **Can I combine Bi-Tapp with meditation videos?** **Yes for slow calming modes (`Modes A, B, D2`)** — pairing slow pulses (`Speed 2–3`) with a breathing pacer, nature video, Safe-Place visualization, or 5-minute body scan prevents your mind from jumping back to your ex. **Turn meditation videos OFF during active fast memory rounds (`Mode C`, `Speed 7`) and belief installation (`Mode D1`, `Speed 4`)** so the video doesn't distract your brain from processing the memory.
4. **Can I fall asleep with it or wear it for many hours?** **Yes — 100% safe.** For sleep, place one buzzer in each **loose sock** at **Speed `1–2`, Intensity `1–2`** for a `20–30 minute` wind-down with a sleep meditation or rain track (turn YouTube **Autoplay OFF**, and never run fast `Mode C` right before bed). Wearing them for many hours at low speed/intensity causes zero harm, though your brain tunes out a constant pulse after `30–60 minutes` (`15–30 minute` bouts work best).

## Quick Start & How to Run

```bash
# 1. LIVE INTERACTIVE COACH (Use this for your real weekly 60-75 min solo EMDR sessions):
PYTHONPATH=. python3 -m apps.bitapp_personal_emdr.cli --mode=interactive

# 2. ON-DEMAND RUMINATION INTERRUPTER (Immediate 3-step guide: Speed 2, Intensity 3, 10m):
PYTHONPATH=. python3 -m apps.bitapp_personal_emdr.cli --mode=loop-interrupt

# 3. FULL CHEAT SHEET, MEDITATION/SLEEP GUIDE & COST SUMMARY:
PYTHONPATH=. python3 -m apps.bitapp_personal_emdr.cli --mode=summary

# 4. AUTOMATED DEMO SESSION (Runs a simulated 8-phase session end-to-end):
PYTHONPATH=. python3 -m apps.bitapp_personal_emdr.cli --mode=simulate-session

# 5. RUN AUTOMATED UNIT TESTS:
PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py" -v
```
