"""Domain-agnostic data schemas for the 8-Phase Bilateral Stimulation Protocol Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple


class EMDRPhase(str, Enum):
    """Canonical 8 phases of EMDR therapy (Shapiro Adaptive Information Processing)."""

    PHASE_1_HISTORY = "PHASE_1_HISTORY"
    PHASE_2_PREPARATION = "PHASE_2_PREPARATION"
    PHASE_3_ASSESSMENT = "PHASE_3_ASSESSMENT"
    PHASE_4_DESENSITIZATION = "PHASE_4_DESENSITIZATION"
    PHASE_5_INSTALLATION = "PHASE_5_INSTALLATION"
    PHASE_6_BODY_SCAN = "PHASE_6_BODY_SCAN"
    PHASE_7_CLOSURE = "PHASE_7_CLOSURE"
    PHASE_8_REEVALUATION = "PHASE_8_REEVALUATION"


class ModalityType(str, Enum):
    """Supported bilateral stimulation hardware and sensory modalities."""

    TACTILE_BITAPP = "tactile_bitapp"
    AUDIO_BINAURAL = "audio_binaural"
    VISUAL_SACCADE = "visual_saccade"


@dataclass(frozen=True)
class BilateralStimulationConfig:
    """Hardware-agnostic bilateral stimulation configuration (Exact Start + Comfortable Range)."""

    modality: ModalityType
    speed_level: int  # Exact starting speed: 1 (slowest) to 10 (fastest)
    intensity_level: int  # Exact starting intensity: 1 (gentle) to 10 (strong)
    set_duration_seconds: int  # Exact starting duration: 5s to 1800s
    speed_range: Tuple[int, int] = (1, 10)  # Comfortable adjustment range (min, max)
    intensity_range: Tuple[int, int] = (1, 10)  # Comfortable adjustment range (min, max)
    duration_range_seconds: Tuple[int, int] = (5, 1800)  # Comfortable adjustment range (min, max)
    mode_label: str = "standard"
    provider_control_code: Optional[str] = None

    def __post_init__(self) -> None:
        if not 1 <= self.speed_level <= 10:
            raise ValueError(f"speed_level must be in [1, 10], got {self.speed_level}")
        if not 1 <= self.intensity_level <= 10:
            raise ValueError(f"intensity_level must be in [1, 10], got {self.intensity_level}")
        if not 5 <= self.set_duration_seconds <= 1800:
            raise ValueError(
                f"set_duration_seconds must be in [5, 1800], got {self.set_duration_seconds}"
            )
        if not (1 <= self.speed_range[0] <= self.speed_level <= self.speed_range[1] <= 10):
            raise ValueError(
                f"speed_level {self.speed_level} must lie within speed_range {self.speed_range}"
            )
        if not (
            1 <= self.intensity_range[0] <= self.intensity_level <= self.intensity_range[1] <= 10
        ):
            raise ValueError(
                f"intensity_level {self.intensity_level} must lie within "
                f"intensity_range {self.intensity_range}"
            )
        if not (
            5
            <= self.duration_range_seconds[0]
            <= self.set_duration_seconds
            <= self.duration_range_seconds[1]
            <= 1800
        ):
            raise ValueError(
                f"set_duration_seconds {self.set_duration_seconds} must lie within "
                f"duration_range_seconds {self.duration_range_seconds}"
            )
        if self.provider_control_code is not None and len(self.provider_control_code.strip()) != 5:
            raise ValueError(
                "provider_control_code must be a 5-character remotEMDR setup code when provided."
            )


@dataclass
class WindowOfToleranceCheck:
    """Pre-session and in-session clinical safety and grounding screening."""

    dissociation_score: int  # 0 (present/grounded) to 10 (severe detachment)
    emotional_overwhelm_score: int  # 0 (calm) to 10 (flooding)
    safe_place_established: bool = True
    container_exercise_ready: bool = True
    human_clinician_present: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.dissociation_score <= 10:
            raise ValueError("dissociation_score must be in [0, 10]")
        if not 0 <= self.emotional_overwhelm_score <= 10:
            raise ValueError("emotional_overwhelm_score must be in [0, 10]")


@dataclass
class TargetMemoryNode:
    """Represents a discrete clinical target memory or trigger node."""

    node_id: str
    cluster_name: str
    title: str
    worst_image_cue: str
    negative_cognition: str
    positive_cognition: str
    initial_voc: int  # Validity of Cognition: 1 (completely false) to 7 (completely true)
    initial_sud: int  # Subjective Units of Disturbance: 0 (no pain) to 10 (worst pain)
    emotions: List[str] = field(default_factory=list)
    somatic_location: str = "chest"
    is_ongoing_stressor: bool = False
    requires_human_clinician: bool = False

    def __post_init__(self) -> None:
        if not 1 <= self.initial_voc <= 7:
            raise ValueError(f"initial_voc must be in [1, 7], got {self.initial_voc}")
        if not 0 <= self.initial_sud <= 10:
            raise ValueError(f"initial_sud must be in [0, 10], got {self.initial_sud}")


@dataclass
class StimulationSetRecord:
    """Telemetry record for a single bilateral stimulation set."""

    set_index: int
    phase: EMDRPhase
    bls_config: BilateralStimulationConfig
    post_set_observation: str
    sud_rating: int
    voc_rating: int
    somatic_tension_clear: bool = False
    circuit_breaker_triggered: bool = False
    circuit_breaker_reason: Optional[str] = None
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )

    def __post_init__(self) -> None:
        if not 0 <= self.sud_rating <= 10:
            raise ValueError(f"sud_rating must be in [0, 10], got {self.sud_rating}")
        if not 1 <= self.voc_rating <= 7:
            raise ValueError(f"voc_rating must be in [1, 7], got {self.voc_rating}")


@dataclass
class SessionSummary:
    """Structured summary of a completed or contained bilateral session."""

    session_id: str
    target_node_id: str
    cluster_name: str
    human_clinician_present: bool
    initial_sud: int
    final_sud: int
    initial_voc: int
    final_voc: int
    total_sets: int
    completed_phases: List[EMDRPhase]
    circuit_breaker_tripped: bool
    closure_achieved: bool
    handoff_notes_for_clinician: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
