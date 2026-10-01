"""Deterministic Window-of-Tolerance & Stagnation Safety Circuit Breaker."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from framework.bls_protocol_engine.schemas import (
    EMDRPhase,
    StimulationSetRecord,
    TargetMemoryNode,
    WindowOfToleranceCheck,
)


@dataclass(frozen=True)
class SafetyEvaluation:
    """Result of a pre-session or post-set clinical safety evaluation."""

    safe_to_proceed: bool
    recommended_phase: EMDRPhase
    trigger_reason: Optional[str] = None
    interweave_or_grounding_prompt: Optional[str] = None
    route_to_human_clinician: bool = False


class SafetyCircuitBreaker:
    """Enforces clinical boundaries for self-guided vs clinician-assisted EMDR.

    Protects against:
    1. Dissociation or emotional flooding before or during bilateral sets.
    2. Unsupervised Phase 4 reprocessing of high-distress targets (SUD >= 7) or
       complex ongoing real-world stressors when no human clinician is present.
    3. 3-set SUD stagnation loops (rumination spinning without adaptive progress).
    """

    def __init__(
        self,
        max_self_guided_sud: int = 6,
        stagnation_set_limit: int = 3,
        max_dissociation_score: int = 4,
    ) -> None:
        self.max_self_guided_sud = max_self_guided_sud
        self.stagnation_set_limit = stagnation_set_limit
        self.max_dissociation_score = max_dissociation_score

    def evaluate_pre_session(
        self,
        target: TargetMemoryNode,
        wot: WindowOfToleranceCheck,
    ) -> SafetyEvaluation:
        """Evaluates whether Phase 4 reprocessing is safe or if Phase 2 resourcing is required."""
        if not wot.safe_place_established or not wot.container_exercise_ready:
            return SafetyEvaluation(
                safe_to_proceed=False,
                recommended_phase=EMDRPhase.PHASE_2_PREPARATION,
                trigger_reason="Phase 2 Safe Place and Container resources must be installed first.",
                interweave_or_grounding_prompt=(
                    "Install Safe Place and Container at slow bilateral speed (Speed 2-3) before "
                    "attempting target assessment."
                ),
                route_to_human_clinician=False,
            )

        if wot.dissociation_score > self.max_dissociation_score:
            return SafetyEvaluation(
                safe_to_proceed=False,
                recommended_phase=EMDRPhase.PHASE_2_PREPARATION,
                trigger_reason=(
                    f"Dissociation score ({wot.dissociation_score}/10) exceeds safe self-guided "
                    f"threshold ({self.max_dissociation_score}/10)."
                ),
                interweave_or_grounding_prompt=(
                    "Execute 5-4-3-2-1 sensory orienting and slow tactile tapping (Speed 2, "
                    "Intensity 3) with eyes open."
                ),
                route_to_human_clinician=True,
            )

        if not wot.human_clinician_present:
            if target.requires_human_clinician or target.is_ongoing_stressor:
                return SafetyEvaluation(
                    safe_to_proceed=False,
                    recommended_phase=EMDRPhase.PHASE_2_PREPARATION,
                    trigger_reason=(
                        f"Target '{target.title}' involves an ongoing attachment/life stressor "
                        "or requires clinician co-regulation; restricted to Phase 2 RDI in "
                        "non-human mode."
                    ),
                    interweave_or_grounding_prompt=(
                        "Use Resource Development & Installation (RDI) at Speed 2-3 to strengthen "
                        "connection anchors, and schedule this target with a remote EMDRIA "
                        "clinician via remotEMDR."
                    ),
                    route_to_human_clinician=True,
                )

            if target.initial_sud > self.max_self_guided_sud:
                return SafetyEvaluation(
                    safe_to_proceed=False,
                    recommended_phase=EMDRPhase.PHASE_2_PREPARATION,
                    trigger_reason=(
                        f"Initial SUD ({target.initial_sud}/10) exceeds non-human self-guided "
                        f"ceiling ({self.max_self_guided_sud}/10)."
                    ),
                    interweave_or_grounding_prompt=(
                        "Switch to Acute Loop Interruption / Containment (Speed 2) or titrate "
                        "into a smaller sub-target with a human telehealth therapist."
                    ),
                    route_to_human_clinician=True,
                )

        return SafetyEvaluation(
            safe_to_proceed=True,
            recommended_phase=EMDRPhase.PHASE_3_ASSESSMENT,
        )

    def evaluate_set_progression(
        self,
        sets: List[StimulationSetRecord],
        human_clinician_present: bool = False,
    ) -> SafetyEvaluation:
        """Evaluates post-set SUD trajectory for flooding or 3-set stagnation."""
        if not sets:
            return SafetyEvaluation(
                safe_to_proceed=True,
                recommended_phase=EMDRPhase.PHASE_4_DESENSITIZATION,
            )

        latest = sets[-1]
        if not human_clinician_present and latest.sud_rating >= 8:
            return SafetyEvaluation(
                safe_to_proceed=False,
                recommended_phase=EMDRPhase.PHASE_7_CLOSURE,
                trigger_reason=(
                    f"Emotional flooding risk detected: SUD spiked to {latest.sud_rating}/10 "
                    "during unsupervised session."
                ),
                interweave_or_grounding_prompt=(
                    "Immediately reduce Bi-Tapp speed to 2 (Intensity 3). Visualize placing the "
                    "target scene into your locked Container and perform 4-6 slow breaths."
                ),
                route_to_human_clinician=True,
            )

        desensitization_sets = [
            s for s in sets if s.phase == EMDRPhase.PHASE_4_DESENSITIZATION
        ]
        if len(desensitization_sets) >= self.stagnation_set_limit:
            window = desensitization_sets[-self.stagnation_set_limit :]
            first_sud = window[0].sud_rating
            last_sud = window[-1].sud_rating
            # If SUD has not decreased over stagnation_set_limit sets and remains > 1
            if last_sud > 1 and all(
                window[i].sud_rating >= window[i - 1].sud_rating
                for i in range(1, len(window))
            ) and last_sud >= first_sud:
                return SafetyEvaluation(
                    safe_to_proceed=False,
                    recommended_phase=EMDRPhase.PHASE_7_CLOSURE,
                    trigger_reason=(
                        f"SUD stagnation detected across {self.stagnation_set_limit} consecutive "
                        f"sets (SUD remained at {last_sud}/10)."
                    ),
                    interweave_or_grounding_prompt=(
                        "Cognitive Interweave / Containment: Ask 'What prevents this 2.5-year-old "
                        "event from being over today?' If still looping, switch Bi-Tapp to Speed 2, "
                        "close via Container exercise, and export session log for therapist review."
                    ),
                    route_to_human_clinician=not human_clinician_present,
                )

        if latest.sud_rating <= 1:
            return SafetyEvaluation(
                safe_to_proceed=True,
                recommended_phase=EMDRPhase.PHASE_5_INSTALLATION,
                interweave_or_grounding_prompt=(
                    "SUD reached 0-1. Transition to Phase 5 (Positive Cognition Installation) "
                    "at moderate Bi-Tapp speed (Speed 4, Intensity 4)."
                ),
            )

        return SafetyEvaluation(
            safe_to_proceed=True,
            recommended_phase=EMDRPhase.PHASE_4_DESENSITIZATION,
        )
