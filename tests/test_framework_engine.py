"""Unit tests for the Generic Bilateral Stimulation Protocol Engine (framework/)."""

from __future__ import annotations

import os
import tempfile
import unittest

from framework.bls_protocol_engine.adapters import (
    AudioVisualSimulatedAdapter,
    BiTappCompanionAdapter,
)
from framework.bls_protocol_engine.engine import ProtocolEngine
from framework.bls_protocol_engine.safety import SafetyCircuitBreaker
from framework.bls_protocol_engine.schemas import (
    BilateralStimulationConfig,
    EMDRPhase,
    ModalityType,
    TargetMemoryNode,
    WindowOfToleranceCheck,
)
from framework.bls_protocol_engine.workspace_sync import GoogleWorkspaceSessionExporter


class TestGenericFrameworkEngine(unittest.TestCase):
    """Tests the domain-agnostic 8-phase protocol engine and safety circuit breakers."""

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
        )
        self.slow_config = BilateralStimulationConfig(
            modality=ModalityType.TACTILE_BITAPP,
            speed_level=2,
            intensity_level=3,
            set_duration_seconds=30,
        )

    def test_happy_path_desensitization_to_closure(self) -> None:
        engine = ProtocolEngine(adapter=self.adapter)
        eval_start = engine.start_session(self.safe_target, self.safe_wot)
        self.assertTrue(eval_start.safe_to_proceed)
        self.assertEqual(engine.current_phase, EMDRPhase.PHASE_3_ASSESSMENT)

        _, eval_s1 = engine.execute_stimulation_set(self.fast_config, "Shift 1", new_sud=3)
        self.assertTrue(eval_s1.safe_to_proceed)
        self.assertEqual(engine.current_phase, EMDRPhase.PHASE_4_DESENSITIZATION)

        _, eval_s2 = engine.execute_stimulation_set(self.fast_config, "Shift 2", new_sud=1)
        self.assertTrue(eval_s2.safe_to_proceed)
        self.assertEqual(engine.current_phase, EMDRPhase.PHASE_5_INSTALLATION)

        _, eval_s3 = engine.execute_stimulation_set(
            self.slow_config, "Installed", new_sud=0, new_voc=7, somatic_tension_clear=True
        )
        self.assertTrue(eval_s3.safe_to_proceed)
        self.assertTrue(engine.closure_achieved)

        summary = engine.complete_closure(self.slow_config, "Completed safely")
        self.assertEqual(summary.final_sud, 0)
        self.assertEqual(summary.final_voc, 7)
        self.assertFalse(summary.circuit_breaker_tripped)
        self.assertTrue(summary.closure_achieved)

    def test_stagnation_circuit_breaker_trips_after_3_flat_sets(self) -> None:
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
        self.assertIn("stagnation", (eval_s3.trigger_reason or "").lower())

    def test_high_sud_target_gated_in_non_human_mode(self) -> None:
        high_target = TargetMemoryNode(
            node_id="HIGH-SUD",
            cluster_name="Attachment",
            title="High Distress Scene",
            worst_image_cue="Cue",
            negative_cognition="NC",
            positive_cognition="PC",
            initial_voc=2,
            initial_sud=8,
        )
        engine = ProtocolEngine(adapter=self.adapter)
        eval_start = engine.start_session(high_target, self.safe_wot)
        self.assertFalse(eval_start.safe_to_proceed)
        self.assertTrue(eval_start.route_to_human_clinician)
        self.assertEqual(eval_start.recommended_phase, EMDRPhase.PHASE_2_PREPARATION)

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


if __name__ == "__main__":
    unittest.main()
