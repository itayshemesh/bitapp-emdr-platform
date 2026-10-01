"""Bi-Tapp Hardware Presets (https://bi-tapp.com/) for Resourcing and EMDR Reprocessing."""

from __future__ import annotations

from framework.bls_protocol_engine.schemas import BilateralStimulationConfig, ModalityType

# Mode A: On-demand acute rumination loop interrupter (ex-girlfriend looping thoughts)
# Slow, gentle tactile tapping for 5-10 minutes to down-regulate amygdala hyperarousal.
BITAPP_LOOP_INTERRUPTER_PRESET = BilateralStimulationConfig(
    modality=ModalityType.TACTILE_BITAPP,
    speed_level=2,
    intensity_level=3,
    set_duration_seconds=300,
    mode_label="Mode A: Acute Rumination Loop Interrupter",
)

# Mode B: Phase 2 Resource Development & Installation (RDI) (Safe Place & 3-Kids Connection Anchor)
# Short 20-second slow sets to install positive somatic resources without triggering negative associations.
BITAPP_PHASE2_RDI_PRESET = BilateralStimulationConfig(
    modality=ModalityType.TACTILE_BITAPP,
    speed_level=3,
    intensity_level=3,
    set_duration_seconds=20,
    mode_label="Mode B: Phase 2 RDI Resourcing",
)

# Mode C: Phase 4 Active Desensitization / Reprocessing (Discrete 2.5-Year Breakup Targets)
# Fast, distinct 35-second tactile sets to tax working memory and reconsolidate stuck memories.
BITAPP_PHASE4_REPROCESSING_PRESET = BilateralStimulationConfig(
    modality=ModalityType.TACTILE_BITAPP,
    speed_level=7,
    intensity_level=6,
    set_duration_seconds=35,
    mode_label="Mode C: Phase 4 Active Desensitization",
)

# Mode D1: Phase 5 Positive Cognition Installation
BITAPP_INSTALLATION_PRESET = BilateralStimulationConfig(
    modality=ModalityType.TACTILE_BITAPP,
    speed_level=4,
    intensity_level=4,
    set_duration_seconds=25,
    mode_label="Mode D1: Phase 5 Positive Cognition Installation",
)

# Mode D2: Phase 7 Closure & Container Grounding
BITAPP_CLOSURE_CONTAINMENT_PRESET = BilateralStimulationConfig(
    modality=ModalityType.TACTILE_BITAPP,
    speed_level=2,
    intensity_level=3,
    set_duration_seconds=60,
    mode_label="Mode D2: Phase 7 Closure & Containment",
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
        mode_label="Telehealth Human Clinician Bridge (remotEMDR)",
        provider_control_code=provider_code.strip().upper(),
    )
