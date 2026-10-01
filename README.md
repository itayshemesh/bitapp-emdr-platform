# Bi-Tapp EMDR Generic Protocol Engine & Personal Treatment Companion

An open-source, two-layer clinical and software engineering system for operating the **[Bi-Tapp](https://bi-tapp.com/)** Bluetooth tactile bilateral stimulation (BLS) kit across **Online Non-Human** and **Online Human** EMDR treatment pathways.

## Architecture Overview

This repository is intentionally split into two decoupled layers:

1. **Layer 1 — Generic Bilateral Protocol Framework (`framework/bls_protocol_engine/`)**:
   - Domain-agnostic 8-Phase EMDR state machine (`ProtocolEngine`).
   - Deterministic clinical safety monitor (`SafetyCircuitBreaker`) enforcing Window-of-Tolerance pre-checks, 3-set SUD stagnation detection, and automatic Phase 7 Container grounding.
   - Pluggable hardware/sensory adapter interface (`StimulationAdapter`, `BiTappCompanionAdapter`, `AudioVisualSimulatedAdapter`).
   - Zero-repo-secret local JSONL and optional Google Workspace OAuth 2.0 session telemetry exporter (`GoogleWorkspaceSessionExporter`).

2. **Layer 2 — Specific Bi-Tapp Personal EMDR Application (`apps/bitapp_personal_emdr/`)**:
   - **Bi-Tapp Hardware Presets (`bitapp_presets.py`)**: Exact speed and intensity settings for Mode A (Acute Rumination Loop Interrupter), Mode B (Phase 2 RDI Resourcing), Mode C (Phase 4 Active Reprocessing), Mode D (Installation & Closure), and `remotEMDR` 5-character therapist control codes.
   - **Clinical Target Packs (`clinical_packs.py`)**:
     - *Pack 1*: **2.5-Year Ex-Partner Breakup Rumination** (R-TEP & 3-Pronged Protocol target nodes).
     - *Pack 2*: **Parental Separation & Fatherhood Resilience (Living Apart from 3 Children)** (Phase 2 RDI Connection Anchor & clinician handoff).
   - **Online Non-Human vs. Online Human Options & Cost Analyzer (`options_analyzer.py`)**.

## Documentation & Master Plan

- **[Master Plan & Clinical Manual (`docs/MASTER_PLAN.md`)](docs/MASTER_PLAN.md)**: Full evaluation of Bi-Tapp hardware, Online Non-Human vs. Online Human EMDR options, What to Expect, How to Do It, Costs, Frequency, and the 10-section execution blueprint.
- **[Architecture & Clinical RFC (`docs/ARCHITECTURE_RFC.md`)](docs/ARCHITECTURE_RFC.md)**: Narrative design document and protocol state-machine specification.

## Quickstart & Verification

```bash
# Run the full unit test suite (Generic Framework + Specific Application)
python3 -m unittest discover -s tests -p "test_*.py" -v

# View the Options, Cost & Weekly Schedule Summary
PYTHONPATH=. python3 apps/bitapp_personal_emdr/cli.py --mode=summary

# Trigger Mode A: On-Demand Acute Rumination Loop Interrupter
PYTHONPATH=. python3 apps/bitapp_personal_emdr/cli.py --mode=loop-interrupt

# Run a simulated 8-phase EMDR session on a discrete breakup target
PYTHONPATH=. python3 apps/bitapp_personal_emdr/cli.py --mode=simulate-session
```

## Security & Credential Isolation

OAuth 2.0 client credentials and personal session logs are strictly excluded from version control via `.gitignore` and stored in `~/.config/bitapp-emdr/oauth_client.json` (`chmod 600`) and `~/.local/share/bitapp-emdr/sessions/` (`chmod 700`).
