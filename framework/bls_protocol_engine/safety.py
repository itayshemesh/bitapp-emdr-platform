"""Deterministic Two-Stage Window-of-Tolerance & Stagnation Safety Circuit Breaker."""

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
    caution_warning: Optional[str] = None
    interweave_or_grounding_prompt: Optional[str] = None
    route_to_human_clinician: bool = False


class SafetyCircuitBreaker:
    """Enforces the Two-Stage Safety Gate for solo vs clinician-assisted EMDR:

    - Pain Levels 0-6 (SUD <= 6): Normal solo processing mode.
    - Pain Level 7 (SUD == 7): Caution Warning shown (`caution_warning` populated),
      but allows the user to choose to continue solo (`safe_to_proceed=True`).
    - Pain Levels 8-10 (SUD >= 8): Automatic Stop (`safe_to_proceed=False`),
      switches to calming mode (Speed 2) and routes to Phase 2/7 Containment.
    - 3-Set Stagnation: If pain level fails to drop across 3 consecutive rounds,
      automatically stops and switches to calming/container mode.
    """

    def __init__(
        self,
        caution_self_guided_sud: int = 7,
        auto_stop_self_guided_sud: int = 8,
        stagnation_set_limit: int = 3,
        max_dissociation_score: int = 4,
    ) -> None:
        self.caution_self_guided_sud = caution_self_guided_sud
        self.auto_stop_self_guided_sud = auto_stop_self_guided_sud
        self.stagnation_set_limit = stagnation_set_limit
        self.max_dissociation_score = max_dissociation_score

    def evaluate_pre_session(
        self,
        target: TargetMemoryNode,
        wot: WindowOfToleranceCheck,
    ) -> SafetyEvaluation:
        """Evaluates whether Phase 4 reprocessing is safe, needs a Level-7 caution, or auto-stops."""
        if not wot.safe_place_established or not wot.container_exercise_ready:
            return SafetyEvaluation(
                safe_to_proceed=False,
                recommended_phase=EMDRPhase.PHASE_2_PREPARATION,
                trigger_reason="Phase 2 Safe Place and Container resources must be installed first.",
                interweave_or_grounding_prompt=(
                    "Install Safe Place and Container at slow bilateral speed (Start at Speed 3, "
                    "Range 2-4) before attempting memory processing."
                ),
                route_to_human_clinician=False,
            )

        if wot.dissociation_score > self.max_dissociation_score:
            return SafetyEvaluation(
                safe_to_proceed=False,
                recommended_phase=EMDRPhase.PHASE_2_PREPARATION,
                trigger_reason=(
                    f"Dissociation score ({wot.dissociation_score}/10) exceeds safe solo "
                    f"threshold ({self.max_dissociation_score}/10)."
                ),
                interweave_or_grounding_prompt=(
                    "Execute 5-4-3-2-1 sensory orienting and slow tactile tapping (Start at "
                    "Speed 2, Intensity 3) with eyes open."
                ),
                route_to_human_clinician=True,
            )

        if not wot.human_clinician_present:
            if target.requires_human_clinician or target.is_ongoing_stressor:
                return SafetyEvaluation(
                    safe_to_proceed=False,
                    recommended_phase=EMDRPhase.PHASE_2_PREPARATION,
                    trigger_reason=(
                        f"Target '{target.title}' involves an ongoing life stressor or deep "
                        "attachment wound; restricted to calming/resourcing (Mode B) when solo."
                    ),
                    interweave_or_grounding_prompt=(
                        "Use Mode B (Start at Speed 3, Intensity 3, 20s sets) to strengthen "
                        "positive connection anchors, and save deep grief processing for a "
                        "human therapist if needed."
                    ),
                    route_to_human_clinician=True,
                )

            if target.initial_sud >= self.auto_stop_self_guided_sud:
                return SafetyEvaluation(
                    safe_to_proceed=False,
                    recommended_phase=EMDRPhase.PHASE_2_PREPARATION,
                    trigger_reason=(
                        f"Auto-Stop: Initial pain level ({target.initial_sud}/10) reached the "
                        f"automatic stop threshold ({self.auto_stop_self_guided_sud}+/10) for "
                        "solo sessions."
                    ),
                    interweave_or_grounding_prompt=(
                        "Switch to Mode A Calming (Start at Speed 2, Intensity 3) or break this "
                        "memory into a smaller piece before trying again."
                    ),
                    route_to_human_clinician=True,
                )

            if target.initial_sud == self.caution_self_guided_sud:
                return SafetyEvaluation(
                    safe_to_proceed=True,
                    recommended_phase=EMDRPhase.PHASE_3_ASSESSMENT,
                    caution_warning=(
                        "Caution (Pain Level 7/10): This memory is strong. You may continue solo "
                        "if you feel grounded, or switch to calming mode (Speed 2) at any time."
                    ),
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
        """Evaluates post-set pain levels for Level-7 caution, Level-8+ auto-stop, or 3-set stall."""
        if not sets:
            return SafetyEvaluation(
                safe_to_proceed=True,
                recommended_phase=EMDRPhase.PHASE_4_DESENSITIZATION,
            )

        latest = sets[-1]
        if not human_clinician_present and latest.sud_rating >= self.auto_stop_self_guided_sud:
            return SafetyEvaluation(
                safe_to_proceed=False,
                recommended_phase=EMDRPhase.PHASE_7_CLOSURE,
                trigger_reason=(
                    f"Auto-Stop: Pain level rose to {latest.sud_rating}/10 during solo session "
                    f"(auto-stop threshold is {self.auto_stop_self_guided_sud}/10)."
                ),
                interweave_or_grounding_prompt=(
                    "Immediately switch Bi-Tapp to Speed 2, Intensity 3. Visualize placing the "
                    "memory into your locked Container and take slow 4-second in / 6-second out breaths."
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
            if (
                last_sud > 1
                and all(
                    window[i].sud_rating >= window[i - 1].sud_rating
                    for i in range(1, len(window))
                )
                and last_sud >= first_sud
            ):
                return SafetyEvaluation(
                    safe_to_proceed=False,
                    recommended_phase=EMDRPhase.PHASE_7_CLOSURE,
                    trigger_reason=(
                        f"3-Round Stall Detected: Pain level stayed stuck at {last_sud}/10 across "
                        f"{self.stagnation_set_limit} rounds in a row."
                    ),
                    interweave_or_grounding_prompt=(
                        "Unstick Prompt: Ask yourself 'What stops this 2.5-year-old memory from "
                        "being over today?' Switch Bi-Tapp to Speed 2 (Intensity 3) for 60s to "
                        "calm down. If this memory stays stuck across sessions, consider booking "
                        "a human therapist."
                    ),
                    route_to_human_clinician=not human_clinician_present,
                )

        if latest.sud_rating <= 1:
            return SafetyEvaluation(
                safe_to_proceed=True,
                recommended_phase=EMDRPhase.PHASE_5_INSTALLATION,
                interweave_or_grounding_prompt=(
                    "Pain level dropped to 0-1! Move to Phase 5 (Locking in Positive Belief) "
                    "at Speed 4, Intensity 4 for 25s rounds (Range: Speed 4-5, 20-30s)."
                ),
            )

        caution_msg: Optional[str] = None
        if not human_clinician_present and latest.sud_rating == self.caution_self_guided_sud:
            caution_msg = (
                "Caution (Pain Level 7/10): You are at the upper edge of solo processing. "
                "You may continue to the next round if you feel steady, or switch to Speed 2 to calm down."
            )

        return SafetyEvaluation(
            safe_to_proceed=True,
            recommended_phase=EMDRPhase.PHASE_4_DESENSITIZATION,
            caution_warning=caution_msg,
        )
