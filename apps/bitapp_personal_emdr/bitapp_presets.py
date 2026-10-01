"""Bi-Tapp Hardware Presets (https://bi-tapp.com/) — Exact Starting Numbers + Comfortable Ranges."""

from __future__ import annotations

from framework.bls_protocol_engine.schemas import BilateralStimulationConfig, ModalityType

# Mode A: Stop Looping Thoughts on the Spot (ex-girlfriend thought loops)
# Start at Speed 2, Intensity 3, 10 mins (600s) | Comfortable Range: Speed 1-3, Intensity 2-4, 5-15 mins (300-900s)
BITAPP_LOOP_INTERRUPTER_PRESET = BilateralStimulationConfig(
    modality=ModalityType.TACTILE_BITAPP,
    speed_level=2,
    intensity_level=3,
    set_duration_seconds=300,
    speed_range=(1, 3),
    intensity_range=(2, 4),
    duration_range_seconds=(180, 900),
    mode_label="Mode A: Acute Rumination Loop Interrupter (Start: Speed 2, Int 3, 5m | Range: Speed 1-3, Int 2-4, 3-15m)",
)

# Mode B: Phase 2 Calming & Positive Resource Installation (Safe Place & 3-Kids Connection Anchor)
# Start at Speed 3, Intensity 3, 20s rounds | Comfortable Range: Speed 2-4, Intensity 2-4, 15-20s rounds
BITAPP_PHASE2_RDI_PRESET = BilateralStimulationConfig(
    modality=ModalityType.TACTILE_BITAPP,
    speed_level=3,
    intensity_level=3,
    set_duration_seconds=20,
    speed_range=(2, 4),
    intensity_range=(2, 4),
    duration_range_seconds=(15, 20),
    mode_label="Mode B: Phase 2 RDI Resourcing (Start: Speed 3, Int 3, 20s | Range: Speed 2-4, Int 2-4, 15-20s)",
)

# Mode C: Phase 4 Active Memory Processing (Discrete 2.5-Year Breakup Scenes)
# Start at Speed 7, Intensity 6, 35s rounds | Comfortable Range: Speed 6-8, Intensity 5-7, 30-45s rounds
BITAPP_PHASE4_REPROCESSING_PRESET = BilateralStimulationConfig(
    modality=ModalityType.TACTILE_BITAPP,
    speed_level=7,
    intensity_level=6,
    set_duration_seconds=35,
    speed_range=(6, 8),
    intensity_range=(5, 7),
    duration_range_seconds=(30, 45),
    mode_label="Mode C: Phase 4 Active Desensitization (Start: Speed 7, Int 6, 35s | Range: Speed 6-8, Int 5-7, 30-45s)",
)

# Mode D1: Phase 5 Locking In Positive Belief (Installation)
# Start at Speed 4, Intensity 4, 25s rounds | Comfortable Range: Speed 4-5, Intensity 3-4, 20-30s rounds
BITAPP_INSTALLATION_PRESET = BilateralStimulationConfig(
    modality=ModalityType.TACTILE_BITAPP,
    speed_level=4,
    intensity_level=4,
    set_duration_seconds=25,
    speed_range=(4, 5),
    intensity_range=(3, 4),
    duration_range_seconds=(20, 30),
    mode_label="Mode D1: Phase 5 Positive Cognition Installation (Start: Speed 4, Int 4, 25s | Range: Speed 4-5, Int 3-4, 20-30s)",
)

# Mode D2: Phase 7 Calming Closure & Container Grounding
# Start at Speed 2, Intensity 3, 60s | Comfortable Range: Speed 1-3, Intensity 2-4, 60-120s
BITAPP_CLOSURE_CONTAINMENT_PRESET = BilateralStimulationConfig(
    modality=ModalityType.TACTILE_BITAPP,
    speed_level=2,
    intensity_level=3,
    set_duration_seconds=60,
    speed_range=(1, 3),
    intensity_range=(2, 4),
    duration_range_seconds=(60, 120),
    mode_label="Mode D2: Phase 7 Closure & Containment (Start: Speed 2, Int 3, 60s | Range: Speed 1-3, Int 2-4, 60-120s)",
)


def create_remotemdr_telehealth_config(
    provider_code: str,
    speed_level: int = 7,
    intensity_level: int = 6,
    set_duration_seconds: int = 35,
) -> BilateralStimulationConfig:
    """Creates a Bi-Tapp configuration bridged to a remote human therapist via remotEMDR."""
    return BilateralStimulationConfig(
        modality=ModalityType.TACTILE_BITAPP,
        speed_level=speed_level,
        intensity_level=intensity_level,
        set_duration_seconds=set_duration_seconds,
        speed_range=(1, 10),
        intensity_range=(1, 10),
        duration_range_seconds=(10, 120),
        mode_label="Telehealth Human Clinician Bridge (remotEMDR)",
        provider_control_code=provider_code.strip().upper(),
    )
