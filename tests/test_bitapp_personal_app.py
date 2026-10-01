"""Unit tests for the Specific Bi-Tapp Personal EMDR Application (apps/bitapp_personal_emdr/)."""

from __future__ import annotations

import unittest

from apps.bitapp_personal_emdr.bitapp_presets import (
    BITAPP_LOOP_INTERRUPTER_PRESET,
    BITAPP_PHASE4_REPROCESSING_PRESET,
    create_remotemdr_telehealth_config,
)
from apps.bitapp_personal_emdr.cli import run_cli
from apps.bitapp_personal_emdr.clinical_packs import (
    get_breakup_rumination_target_pack,
    get_children_separation_rdi_pack,
)
from apps.bitapp_personal_emdr.options_analyzer import (
    build_treatment_schedule_and_cost_report,
    get_emdr_options_catalog,
)
from framework.bls_protocol_engine.adapters import BiTappCompanionAdapter
from framework.bls_protocol_engine.engine import ProtocolEngine
from framework.bls_protocol_engine.schemas import EMDRPhase, WindowOfToleranceCheck


class TestBiTappPersonalApplication(unittest.TestCase):
    """Verifies Bi-Tapp presets, breakup/children packs, cost analyzer, and CLI."""

    def test_bitapp_presets_and_remotemdr_provider_code(self) -> None:
        self.assertEqual(BITAPP_LOOP_INTERRUPTER_PRESET.speed_level, 2)
        self.assertEqual(BITAPP_LOOP_INTERRUPTER_PRESET.intensity_level, 3)
        self.assertEqual(BITAPP_PHASE4_REPROCESSING_PRESET.speed_level, 7)

        remote_cfg = create_remotemdr_telehealth_config("ab12c")
        self.assertEqual(remote_cfg.provider_control_code, "AB12C")

        adapter = BiTappCompanionAdapter()
        receipt = adapter.configure_and_prompt(remote_cfg)
        self.assertTrue(receipt.remote_bridge_active)
        self.assertIn("AB12C", receipt.user_action_instruction)

    def test_breakup_and_children_clinical_packs_safety_boundaries(self) -> None:
        breakup_pack = get_breakup_rumination_target_pack()
        self.assertEqual(len(breakup_pack), 3)
        # First two discrete breakup scenes are <= SUD 6 (eligible for guided self-session)
        self.assertLessEqual(breakup_pack[0].initial_sud, 6)
        self.assertFalse(breakup_pack[0].requires_human_clinician)
        # Deep touchstone attachment target requires human clinician
        self.assertTrue(breakup_pack[2].requires_human_clinician)

        kids_pack = get_children_separation_rdi_pack()
        self.assertEqual(len(kids_pack), 1)
        self.assertTrue(kids_pack[0].is_ongoing_stressor)
        self.assertTrue(kids_pack[0].requires_human_clinician)

        # Verify ongoing children separation stressor is gated to Phase 2 RDI in non-human mode
        engine = ProtocolEngine(adapter=BiTappCompanionAdapter())
        wot = WindowOfToleranceCheck(
            dissociation_score=0,
            emotional_overwhelm_score=2,
            human_clinician_present=False,
        )
        evaluation = engine.start_session(kids_pack[0], wot)
        self.assertFalse(evaluation.safe_to_proceed)
        self.assertEqual(evaluation.recommended_phase, EMDRPhase.PHASE_2_PREPARATION)
        self.assertTrue(evaluation.route_to_human_clinician)

    def test_options_and_cost_analyzer(self) -> None:
        catalog = get_emdr_options_catalog()
        self.assertGreaterEqual(len(catalog), 4)
        categories = {item.category for item in catalog}
        self.assertIn("NON_HUMAN", categories)
        self.assertIn("HUMAN_TELEHEALTH", categories)
        self.assertIn("HYBRID_STEPPED_CARE", categories)

        report = build_treatment_schedule_and_cost_report(
            include_wristbands=True,
            include_wall_charger=False,
            international_shipping=False,
            telehealth_sessions_count=8,
            per_session_copay_usd=0,
        )
        self.assertEqual(report["grand_total_estimated_usd"], 277 + 20 + 12)

    def test_cli_modes_return_zero(self) -> None:
        self.assertEqual(run_cli(["--mode", "summary"]), 0)
        self.assertEqual(run_cli(["--mode", "loop-interrupt"]), 0)
        self.assertEqual(run_cli(["--mode", "simulate-session"]), 0)


if __name__ == "__main__":
    unittest.main()
