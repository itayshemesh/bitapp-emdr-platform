"""Deterministic 8-Phase Bilateral Stimulation State Machine Engine."""

from __future__ import annotations

from typing import List, Optional
import uuid

from framework.bls_protocol_engine.adapters import AdapterDispatchReceipt, StimulationAdapter
from framework.bls_protocol_engine.safety import SafetyCircuitBreaker, SafetyEvaluation
from framework.bls_protocol_engine.schemas import (
    BilateralStimulationConfig,
    EMDRPhase,
    SessionSummary,
    StimulationSetRecord,
    TargetMemoryNode,
    WindowOfToleranceCheck,
)


class ProtocolEngine:
    """Executes the 8-phase EMDR protocol with safety gates and mandatory closure."""

    def __init__(
        self,
        adapter: StimulationAdapter,
        safety_breaker: Optional[SafetyCircuitBreaker] = None,
    ) -> None:
        self.adapter = adapter
        self.safety_breaker = safety_breaker or SafetyCircuitBreaker()
        self.session_id = f"emdr_{uuid.uuid4().hex[:10]}"
        self.current_phase = EMDRPhase.PHASE_1_HISTORY
        self.completed_phases: List[EMDRPhase] = [EMDRPhase.PHASE_1_HISTORY]
        self.sets: List[StimulationSetRecord] = []
        self.circuit_breaker_tripped = False
        self.closure_achieved = False
        self.handoff_notes: List[str] = []

    def _record_phase(self, phase: EMDRPhase) -> None:
        self.current_phase = phase
        if phase not in self.completed_phases:
            self.completed_phases.append(phase)

    def start_session(
        self,
        target: TargetMemoryNode,
        wot: WindowOfToleranceCheck,
    ) -> SafetyEvaluation:
        """Runs Phase 2/3 pre-flight safety check and transitions to recommended phase."""
        self.target = target
        self.wot = wot
        self.current_sud = target.initial_sud
        self.current_voc = target.initial_voc

        evaluation = self.safety_breaker.evaluate_pre_session(target, wot)
        self._record_phase(EMDRPhase.PHASE_2_PREPARATION)

        if not evaluation.safe_to_proceed:
            self.circuit_breaker_tripped = True
            if evaluation.trigger_reason:
                self.handoff_notes.append(evaluation.trigger_reason)
            return evaluation

        self._record_phase(EMDRPhase.PHASE_3_ASSESSMENT)
        return evaluation

    def execute_stimulation_set(
        self,
        bls_config: BilateralStimulationConfig,
        post_set_observation: str,
        new_sud: int,
        new_voc: Optional[int] = None,
        somatic_tension_clear: bool = False,
    ) -> tuple[AdapterDispatchReceipt, SafetyEvaluation]:
        """Executes a single bilateral stimulation set and evaluates safety progression."""
        if self.circuit_breaker_tripped:
            raise RuntimeError(
                "Cannot execute Phase 4/5 stimulation sets when SafetyCircuitBreaker has tripped; "
                "call complete_closure() instead."
            )

        if self.current_phase == EMDRPhase.PHASE_3_ASSESSMENT:
            self._record_phase(EMDRPhase.PHASE_4_DESENSITIZATION)

        receipt = self.adapter.configure_and_prompt(bls_config)
        effective_voc = new_voc if new_voc is not None else self.current_voc

        record = StimulationSetRecord(
            set_index=len(self.sets) + 1,
            phase=self.current_phase,
            bls_config=bls_config,
            post_set_observation=post_set_observation,
            sud_rating=new_sud,
            voc_rating=effective_voc,
            somatic_tension_clear=somatic_tension_clear,
        )
        self.sets.append(record)
        self.current_sud = new_sud
        self.current_voc = effective_voc

        evaluation = self.safety_breaker.evaluate_set_progression(
            self.sets,
            human_clinician_present=self.wot.human_clinician_present,
            initial_sud=self.target.initial_sud,
        )

        if not evaluation.safe_to_proceed:
            self.circuit_breaker_tripped = True
            record.circuit_breaker_triggered = True
            record.circuit_breaker_reason = evaluation.trigger_reason
            if evaluation.trigger_reason:
                self.handoff_notes.append(evaluation.trigger_reason)
            self._record_phase(EMDRPhase.PHASE_7_CLOSURE)
            return receipt, evaluation

        if (
            self.current_phase == EMDRPhase.PHASE_4_DESENSITIZATION
            and evaluation.recommended_phase == EMDRPhase.PHASE_5_INSTALLATION
        ):
            self._record_phase(EMDRPhase.PHASE_5_INSTALLATION)
        elif (
            self.current_phase == EMDRPhase.PHASE_5_INSTALLATION
            and effective_voc >= 7
        ):
            self._record_phase(EMDRPhase.PHASE_6_BODY_SCAN)
            if somatic_tension_clear:
                self._record_phase(EMDRPhase.PHASE_7_CLOSURE)
        elif (
            self.current_phase == EMDRPhase.PHASE_6_BODY_SCAN
            and somatic_tension_clear
        ):
            self._record_phase(EMDRPhase.PHASE_7_CLOSURE)

        return receipt, evaluation

    def complete_closure(self, closing_config: BilateralStimulationConfig, note: str) -> SessionSummary:
        """Executes mandatory Phase 7 Closure (Safe Place / Container) and returns summary."""
        self._record_phase(EMDRPhase.PHASE_7_CLOSURE)
        self.last_closure_receipt: Optional[AdapterDispatchReceipt] = (
            self.adapter.configure_and_prompt(closing_config)
        )
        self.closure_achieved = True
        if note:
            self.handoff_notes.append(f"Closure Note: {note}")

        return SessionSummary(
            session_id=self.session_id,
            target_node_id=self.target.node_id,
            cluster_name=self.target.cluster_name,
            human_clinician_present=self.wot.human_clinician_present,
            initial_sud=self.target.initial_sud,
            final_sud=self.current_sud,
            initial_voc=self.target.initial_voc,
            final_voc=self.current_voc,
            total_sets=len(self.sets),
            completed_phases=list(self.completed_phases),
            circuit_breaker_tripped=self.circuit_breaker_tripped,
            closure_achieved=self.closure_achieved,
            handoff_notes_for_clinician=list(self.handoff_notes),
        )
