"""Unit tests for the Generic Bilateral Stimulation Protocol Engine (framework/)."""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest

from framework.bls_protocol_engine.adapters import (
    AdapterDispatchReceipt,
    AudioVisualSimulatedAdapter,
    BiTappCompanionAdapter,
    StimulationAdapter,
)
from framework.bls_protocol_engine.engine import ProtocolEngine
from framework.bls_protocol_engine.safety import SafetyCircuitBreaker, SafetyEvaluation
from framework.bls_protocol_engine.schemas import (
    BilateralStimulationConfig,
    EMDRPhase,
    ModalityType,
    SessionSummary,
    StimulationSetRecord,
    TargetMemoryNode,
    WindowOfToleranceCheck,
)
from framework.bls_protocol_engine.workspace_sync import GoogleWorkspaceSessionExporter


class TestGenericFrameworkEngine(unittest.TestCase):
    """Tests the domain-agnostic 8-phase protocol engine and Two-Stage Safety Gate."""

    def setUp(self) -> None:
        self.adapter = BiTappCompanionAdapter()
        self.safe_target = TargetMemoryNode(
            node_id="TEST-NODE-1",
            cluster_name="Test Cluster",
            title="Moderate Discrete Memory",
            worst_image_cue="Test image",
            negative_cognition="I am stuck",
            positive_cognition="I am free",
            initial_voc=3,
            initial_sud=5,
        )
        self.safe_wot = WindowOfToleranceCheck(
            dissociation_score=1,
            emotional_overwhelm_score=2,
            safe_place_established=True,
            container_exercise_ready=True,
            human_clinician_present=False,
        )
        self.fast_config = BilateralStimulationConfig(
            modality=ModalityType.TACTILE_BITAPP,
            speed_level=7,
            intensity_level=6,
            set_duration_seconds=35,
            speed_range=(6, 8),
            intensity_range=(5, 7),
            duration_range_seconds=(30, 45),
        )
        self.slow_config = BilateralStimulationConfig(
            modality=ModalityType.TACTILE_BITAPP,
            speed_level=2,
            intensity_level=3,
            set_duration_seconds=30,
            speed_range=(1, 3),
            intensity_range=(2, 4),
            duration_range_seconds=(15, 60),
        )

    def test_happy_path_desensitization_to_closure(self) -> None:
        self.assertIsInstance(self.adapter, StimulationAdapter)
        engine = ProtocolEngine(adapter=self.adapter)
        eval_start = engine.start_session(self.safe_target, self.safe_wot)
        self.assertIsInstance(eval_start, SafetyEvaluation)
        self.assertTrue(eval_start.safe_to_proceed)
        self.assertIsNone(eval_start.caution_warning)
        self.assertEqual(engine.current_phase, EMDRPhase.PHASE_3_ASSESSMENT)

        receipt_1, eval_s1 = engine.execute_stimulation_set(self.fast_config, "Shift 1", new_sud=3)
        self.assertIsInstance(receipt_1, AdapterDispatchReceipt)
        self.assertTrue(eval_s1.safe_to_proceed)
        self.assertIn("Comfortable Range: Speed 6-8, Intensity 5-7, Duration 30-45s", receipt_1.user_action_instruction)
        self.assertEqual(engine.current_phase, EMDRPhase.PHASE_4_DESENSITIZATION)

        _, eval_s2 = engine.execute_stimulation_set(self.fast_config, "Shift 2", new_sud=1)
        self.assertTrue(eval_s2.safe_to_proceed)
        self.assertEqual(eval_s2.recommended_phase, EMDRPhase.PHASE_5_INSTALLATION)
        self.assertEqual(engine.current_phase, EMDRPhase.PHASE_5_INSTALLATION)

        _, eval_s3 = engine.execute_stimulation_set(
            self.slow_config, "Installed", new_sud=0, new_voc=7, somatic_tension_clear=False
        )
        self.assertTrue(eval_s3.safe_to_proceed)
        self.assertEqual(eval_s3.recommended_phase, EMDRPhase.PHASE_6_BODY_SCAN)
        self.assertEqual(engine.current_phase, EMDRPhase.PHASE_6_BODY_SCAN)

        _, eval_s4 = engine.execute_stimulation_set(
            self.slow_config, "Body scan clear", new_sud=0, new_voc=7, somatic_tension_clear=True
        )
        self.assertTrue(eval_s4.safe_to_proceed)
        self.assertEqual(eval_s4.recommended_phase, EMDRPhase.PHASE_7_CLOSURE)
        self.assertEqual(engine.current_phase, EMDRPhase.PHASE_7_CLOSURE)
        self.assertIsInstance(engine.sets[-1], StimulationSetRecord)
        self.assertTrue(engine.sets[-1].somatic_tension_clear)
        self.assertFalse(engine.closure_achieved)

        summary = engine.complete_closure(self.slow_config, "Completed safely")
        self.assertIsInstance(summary, SessionSummary)
        self.assertEqual(summary.final_sud, 0)
        self.assertEqual(summary.final_voc, 7)
        self.assertFalse(summary.circuit_breaker_tripped)
        self.assertTrue(summary.closure_achieved)
        self.assertIsNotNone(engine.last_closure_receipt)

    def test_two_stage_safety_gate_caution_at_7_and_autostop_at_8(self) -> None:
        level_7_target = TargetMemoryNode(
            node_id="LEVEL-7",
            cluster_name="Attachment",
            title="Level 7 Memory (Caution Allowed)",
            worst_image_cue="Cue",
            negative_cognition="NC",
            positive_cognition="PC",
            initial_voc=2,
            initial_sud=7,
        )
        engine = ProtocolEngine(adapter=self.adapter)
        eval_7 = engine.start_session(level_7_target, self.safe_wot)
        self.assertTrue(eval_7.safe_to_proceed)
        self.assertIsNotNone(eval_7.caution_warning)
        self.assertIn("7/10", eval_7.caution_warning or "")

        # Pre-session emotional_overwhelm_score == 7 also emits Level-7 caution warning
        caution_wot = WindowOfToleranceCheck(
            dissociation_score=1,
            emotional_overwhelm_score=7,
            safe_place_established=True,
            container_exercise_ready=True,
            human_clinician_present=False,
        )
        engine_caution_wot = ProtocolEngine(adapter=self.adapter)
        eval_caution_wot = engine_caution_wot.start_session(self.safe_target, caution_wot)
        self.assertTrue(eval_caution_wot.safe_to_proceed)
        self.assertIsNotNone(eval_caution_wot.caution_warning)
        self.assertIn("7/10", eval_caution_wot.caution_warning or "")

        # Mid-session spike to 8 triggers Auto-Stop
        _, eval_spike_8 = engine.execute_stimulation_set(
            self.fast_config, "Pain spiked to 8", new_sud=8
        )
        self.assertFalse(eval_spike_8.safe_to_proceed)
        self.assertEqual(eval_spike_8.recommended_phase, EMDRPhase.PHASE_7_CLOSURE)

        # Attempting another set after circuit breaker tripped raises RuntimeError
        with self.assertRaises(RuntimeError):
            engine.execute_stimulation_set(self.fast_config, "Blocked after trip", new_sud=7)

        # Pre-session Level 8 triggers Auto-Stop immediately
        level_8_target = TargetMemoryNode(
            node_id="LEVEL-8",
            cluster_name="Attachment",
            title="Level 8 Memory (Auto-Stop)",
            worst_image_cue="Cue",
            negative_cognition="NC",
            positive_cognition="PC",
            initial_voc=2,
            initial_sud=8,
        )
        engine2 = ProtocolEngine(adapter=self.adapter)
        eval_8 = engine2.start_session(level_8_target, self.safe_wot)
        self.assertFalse(eval_8.safe_to_proceed)
        self.assertTrue(eval_8.route_to_human_clinician)
        self.assertEqual(eval_8.recommended_phase, EMDRPhase.PHASE_2_PREPARATION)
        with self.assertRaises(RuntimeError):
            engine2.execute_stimulation_set(self.fast_config, "Blocked pre-session trip", new_sud=7)

        # Pre-session emotional_overwhelm_score >= 8 triggers Auto-Stop in solo mode
        overwhelmed_wot = WindowOfToleranceCheck(
            dissociation_score=1,
            emotional_overwhelm_score=8,
            safe_place_established=True,
            container_exercise_ready=True,
            human_clinician_present=False,
        )
        engine3 = ProtocolEngine(adapter=self.adapter)
        eval_overwhelm = engine3.start_session(self.safe_target, overwhelmed_wot)
        self.assertFalse(eval_overwhelm.safe_to_proceed)
        self.assertIn("overwhelm", (eval_overwhelm.trigger_reason or "").lower())

    def test_stagnation_circuit_breaker_trips_after_3_flat_sets_and_respects_round1_drop(self) -> None:
        # Case 1: Initial SUD=5, sets [5, 5, 5] -> 3 rounds in a row with no drop -> trips on Set 3
        engine = ProtocolEngine(
            adapter=self.adapter,
            safety_breaker=SafetyCircuitBreaker(stagnation_set_limit=3),
        )
        engine.start_session(self.safe_target, self.safe_wot)
        engine.execute_stimulation_set(self.fast_config, "Loop 1", new_sud=5)
        engine.execute_stimulation_set(self.fast_config, "Loop 2", new_sud=5)
        _, eval_s3 = engine.execute_stimulation_set(self.fast_config, "Loop 3", new_sud=5)

        self.assertFalse(eval_s3.safe_to_proceed)
        self.assertEqual(eval_s3.recommended_phase, EMDRPhase.PHASE_7_CLOSURE)
        self.assertTrue(engine.circuit_breaker_tripped)
        self.assertIn("stall", (eval_s3.trigger_reason or "").lower())
        self.assertNotIn("2.5-year-old", eval_s3.interweave_or_grounding_prompt or "")
        self.assertNotIn("Bi-Tapp", eval_s3.interweave_or_grounding_prompt or "")

        # Case 2: Initial SUD=5, Round 1 drops to 4, Round 2=4, Round 3=4 -> only 2 stalled rounds so far!
        engine_drop = ProtocolEngine(
            adapter=self.adapter,
            safety_breaker=SafetyCircuitBreaker(stagnation_set_limit=3),
        )
        engine_drop.start_session(self.safe_target, self.safe_wot)
        engine_drop.execute_stimulation_set(self.fast_config, "Drop to 4", new_sud=4)
        engine_drop.execute_stimulation_set(self.fast_config, "Stuck 1 at 4", new_sud=4)
        _, eval_r3 = engine_drop.execute_stimulation_set(self.fast_config, "Stuck 2 at 4", new_sud=4)
        self.assertTrue(eval_r3.safe_to_proceed)
        # Round 4 stays at 4 -> 3 consecutive stalled rounds (R2, R3, R4) -> trips on Set 4
        _, eval_r4 = engine_drop.execute_stimulation_set(self.fast_config, "Stuck 3 at 4", new_sud=4)
        self.assertFalse(eval_r4.safe_to_proceed)

    def test_schema_validation_and_pre_session_guards(self) -> None:
        with self.assertRaises(ValueError):
            BilateralStimulationConfig(
                modality=ModalityType.TACTILE_BITAPP,
                speed_level=11,
                intensity_level=5,
                set_duration_seconds=30,
            )
        with self.assertRaises(ValueError):
            BilateralStimulationConfig(
                modality=ModalityType.TACTILE_BITAPP,
                speed_level=5,
                intensity_level=5,
                set_duration_seconds=30,
                provider_control_code="BAD!",
            )
        with self.assertRaises(ValueError):
            TargetMemoryNode(
                node_id="BAD",
                cluster_name="C",
                title="T",
                worst_image_cue="I",
                negative_cognition="N",
                positive_cognition="P",
                initial_voc=8,
                initial_sud=5,
            )
        with self.assertRaises(ValueError):
            WindowOfToleranceCheck(dissociation_score=11, emotional_overwhelm_score=2)

        breaker = SafetyCircuitBreaker()
        no_res_wot = WindowOfToleranceCheck(
            dissociation_score=1,
            emotional_overwhelm_score=2,
            safe_place_established=False,
        )
        self.assertFalse(breaker.evaluate_pre_session(self.safe_target, no_res_wot).safe_to_proceed)
        high_dissoc_wot = WindowOfToleranceCheck(
            dissociation_score=6,
            emotional_overwhelm_score=2,
        )
        self.assertFalse(breaker.evaluate_pre_session(self.safe_target, high_dissoc_wot).safe_to_proceed)

    def test_workspace_exporter_persists_locally_and_parses_oauth(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            oauth_file = os.path.join(tmpdir, "oauth.json")
            with open(oauth_file, "w", encoding="utf-8") as f:
                f.write(
                    '{"installed":{"client_id":"test-id.apps.googleusercontent.com",'
                    '"project_id":"test-proj","auth_uri":"https://accounts.google.com/o/oauth2/auth",'
                    '"token_uri":"https://oauth2.googleapis.com/token"}}'
                )
            exporter = GoogleWorkspaceSessionExporter(
                oauth_client_path=oauth_file,
                session_log_dir=os.path.join(tmpdir, "logs"),
            )
            meta = exporter.load_installed_oauth_metadata()
            self.assertIsNotNone(meta)
            self.assertEqual(meta["project_id"], "test-proj")

            engine = ProtocolEngine(adapter=AudioVisualSimulatedAdapter())
            engine.start_session(self.safe_target, self.safe_wot)
            summary = engine.complete_closure(self.slow_config, "Test closure")
            log_path = exporter.persist_session_summary(summary)
            self.assertTrue(os.path.isfile(log_path))

            # Missing OAuth file emits diagnostic to stderr and returns None
            missing_exporter = GoogleWorkspaceSessionExporter(
                oauth_client_path=os.path.join(tmpdir, "nonexistent.json"),
                session_log_dir=os.path.join(tmpdir, "logs"),
            )
            err_buf = io.StringIO()
            with contextlib.redirect_stderr(err_buf):
                self.assertIsNone(missing_exporter.load_installed_oauth_metadata())
            self.assertIn("[workspace_sync] Diagnostic:", err_buf.getvalue())


if __name__ == "__main__":
    unittest.main()
