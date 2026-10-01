# Bi-Tapp EMDR Platform (`bitapp-emdr-platform`)

A two-layer open-source architecture combining:
1. **Layer 1 — Generic Framework (`framework/bls_protocol_engine/`)**: A reusable, domain-agnostic 8-Phase Bilateral Stimulation (BLS) & EMDR state-machine engine with a **Two-Stage Safety Circuit Breaker** (Levels `1–6` normal solo mode, Level `7` caution prompt with user choice, Levels `8–10` or `3` stalled rounds automatic stop to calming mode), pluggable hardware adapters (Exact Starting Number + Comfortable Range), and zero-repo-secret Google OAuth 2.0 session journaling.
2. **Layer 2 — Specific Bi-Tapp Personal EMDR Application (`apps/bitapp_personal_emdr/`)**: A personal self-regulation and EMDR companion configured for the **[Bi-Tapp](https://bi-tapp.com/)** Bluetooth tactile tappers, implementing a **Solo-First (Weeks 1–4) $\rightarrow$ Human Backup If Stuck** roadmap for:
   - **2.5-Year Ex-Partner Breakup Rumination ("Mini-Trauma")**: On-demand loop interruption (`Start: Speed 2, Intensity 3, 10m | Range: Speed 1–3, Intensity 2–4, 5–15m`) and weekly memory processing (`Start: Speed 7, Intensity 6, 35s rounds | Range: Speed 6–8, Intensity 5–7, 30–45s rounds`).
   - **Living Apart From 3 Children**: Daily Phase 2 Resource Development & Installation (`Start: Speed 3, Intensity 3, 20s rounds | Range: Speed 2–4, Intensity 2–4, 15–20s rounds`) and optional `remotEMDR` 5-character provider code handoff.

## Single Source of Truth — Unified Master Plan
* **[Unified Master Plan & Clinical Guide (`docs/MASTER_PLAN.md`)](docs/MASTER_PLAN.md)**: Complete plain-English explanation, Bi-Tapp hardware & pricing breakdown, Solo-First vs. Human Telehealth comparison, exact Bi-Tapp settings + comfortable ranges, weekly schedule, and software architecture.

## Quick Start

```bash
# Run all unit tests
PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py" -v

# View the complete Bi-Tapp clinical roadmap, settings, and cost summary
PYTHONPATH=. python3 -m apps.bitapp_personal_emdr.cli --mode=summary

# Trigger the on-demand 3-step Rumination Loop Interrupter (Start: Speed 2, Intensity 3)
PYTHONPATH=. python3 -m apps.bitapp_personal_emdr.cli --mode=loop-interrupt

# Run an end-to-end simulated 8-phase EMDR session
PYTHONPATH=. python3 -m apps.bitapp_personal_emdr.cli --mode=simulate-session
```
