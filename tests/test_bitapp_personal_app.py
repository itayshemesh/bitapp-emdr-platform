"""Unit tests for the Specific Bi-Tapp Personal EMDR Application (apps/bitapp_personal_emdr/)."""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
import unittest.mock

from apps.bitapp_personal_emdr.bitapp_presets import (
    BITAPP_CLOSURE_CONTAINMENT_PRESET,
    BITAPP_INSTALLATION_PRESET,
    BITAPP_LOOP_INTERRUPTER_PRESET,
    BITAPP_PHASE2_RDI_PRESET,
    BITAPP_PHASE4_REPROCESSING_PRESET,
    create_remotemdr_telehealth_config,
)
from apps.bitapp_personal_emdr.cli import _prompt_int, run_cli
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
    """Verifies Bi-Tapp presets (Exact Start + Range), clinical packs, cost analyzer, and CLI."""

    def test_bitapp_presets_exact_start_and_ranges(self) -> None:
        # Mode A: Start Speed 2, Int 3, 10m (600s) | Range Speed 1-3, Int 2-4, 5-15m (300-900s)
        self.assertEqual(BITAPP_LOOP_INTERRUPTER_PRESET.speed_level, 2)
        self.assertEqual(BITAPP_LOOP_INTERRUPTER_PRESET.speed_range, (1, 3))
        self.assertEqual(BITAPP_LOOP_INTERRUPTER_PRESET.intensity_level, 3)
        self.assertEqual(BITAPP_LOOP_INTERRUPTER_PRESET.intensity_range, (2, 4))
        self.assertEqual(BITAPP_LOOP_INTERRUPTER_PRESET.set_duration_seconds, 600)
        self.assertEqual(BITAPP_LOOP_INTERRUPTER_PRESET.duration_range_seconds, (300, 900))

        # Mode B: Start Speed 3, Int 3, 20s | Range Speed 2-4, Int 2-4, 15-20s
        self.assertEqual(BITAPP_PHASE2_RDI_PRESET.speed_level, 3)
        self.assertEqual(BITAPP_PHASE2_RDI_PRESET.speed_range, (2, 4))
        self.assertEqual(BITAPP_PHASE2_RDI_PRESET.intensity_level, 3)
        self.assertEqual(BITAPP_PHASE2_RDI_PRESET.intensity_range, (2, 4))
        self.assertEqual(BITAPP_PHASE2_RDI_PRESET.set_duration_seconds, 20)
        self.assertEqual(BITAPP_PHASE2_RDI_PRESET.duration_range_seconds, (15, 20))

        # Mode C: Start Speed 7, Int 6, 35s | Range Speed 6-8, Int 5-7, 30-45s
        self.assertEqual(BITAPP_PHASE4_REPROCESSING_PRESET.speed_level, 7)
        self.assertEqual(BITAPP_PHASE4_REPROCESSING_PRESET.speed_range, (6, 8))
        self.assertEqual(BITAPP_PHASE4_REPROCESSING_PRESET.intensity_level, 6)
        self.assertEqual(BITAPP_PHASE4_REPROCESSING_PRESET.intensity_range, (5, 7))
        self.assertEqual(BITAPP_PHASE4_REPROCESSING_PRESET.set_duration_seconds, 35)
        self.assertEqual(BITAPP_PHASE4_REPROCESSING_PRESET.duration_range_seconds, (30, 45))

        # Mode D1: Start Speed 4, Int 4, 25s | Range Speed 4-5, Int 3-4, 20-30s
        self.assertEqual(BITAPP_INSTALLATION_PRESET.speed_level, 4)
        self.assertEqual(BITAPP_INSTALLATION_PRESET.speed_range, (4, 5))
        self.assertEqual(BITAPP_INSTALLATION_PRESET.intensity_level, 4)
        self.assertEqual(BITAPP_INSTALLATION_PRESET.intensity_range, (3, 4))
        self.assertEqual(BITAPP_INSTALLATION_PRESET.set_duration_seconds, 25)
        self.assertEqual(BITAPP_INSTALLATION_PRESET.duration_range_seconds, (20, 30))

        # Mode D2: Start Speed 2, Int 3, 60s | Range Speed 1-3, Int 2-4, 60-120s
        self.assertEqual(BITAPP_CLOSURE_CONTAINMENT_PRESET.speed_level, 2)
        self.assertEqual(BITAPP_CLOSURE_CONTAINMENT_PRESET.speed_range, (1, 3))
        self.assertEqual(BITAPP_CLOSURE_CONTAINMENT_PRESET.intensity_level, 3)
        self.assertEqual(BITAPP_CLOSURE_CONTAINMENT_PRESET.intensity_range, (2, 4))
        self.assertEqual(BITAPP_CLOSURE_CONTAINMENT_PRESET.set_duration_seconds, 60)
        self.assertEqual(BITAPP_CLOSURE_CONTAINMENT_PRESET.duration_range_seconds, (60, 120))

        remote_cfg = create_remotemdr_telehealth_config("ab12c")
        self.assertEqual(remote_cfg.provider_control_code, "AB12C")

        adapter = BiTappCompanionAdapter()
        receipt = adapter.configure_and_prompt(remote_cfg)
        self.assertTrue(receipt.remote_bridge_active)
        self.assertIn("AB12C", receipt.user_action_instruction)
        self.assertIn("Comfortable Range:", receipt.user_action_instruction)

    def test_breakup_and_children_clinical_packs_safety_boundaries(self) -> None:
        breakup_pack = get_breakup_rumination_target_pack()
        self.assertEqual(len(breakup_pack), 4)
        self.assertLessEqual(breakup_pack[0].initial_sud, 6)
        self.assertFalse(breakup_pack[0].requires_human_clinician)
        self.assertEqual(breakup_pack[2].initial_sud, 7)
        self.assertFalse(breakup_pack[2].requires_human_clinician)
        self.assertTrue(breakup_pack[3].requires_human_clinician)

        kids_pack = get_children_separation_rdi_pack()
        self.assertEqual(len(kids_pack), 1)
        self.assertTrue(kids_pack[0].is_ongoing_stressor)
        self.assertTrue(kids_pack[0].requires_human_clinician)

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

    def test_options_and_cost_analyzer_solo_first_primary(self) -> None:
        catalog = get_emdr_options_catalog()
        self.assertGreaterEqual(len(catalog), 5)
        self.assertEqual(catalog[0].category, "SOLO_FIRST_PRIMARY")
        self.assertEqual(catalog[3].per_session_cost_usd_range, (0, 275))
        self.assertEqual(catalog[3].monthly_cost_usd_range, (0, 1100))

        report = build_treatment_schedule_and_cost_report(
            include_wristbands=True,
            include_wall_charger=False,
            international_shipping=False,
            telehealth_sessions_count=0,
            per_session_copay_usd=0,
        )
        self.assertEqual(report["grand_total_estimated_usd"], 277 + 20 + 12)
        self.assertIn("Try Solo First", str(report["primary_strategy"]))

    def test_prompt_int_diagnostics_and_clamping(self) -> None:
        err_buf = io.StringIO()
        with contextlib.redirect_stderr(err_buf):
            with unittest.mock.patch("builtins.input", side_effect=["abc", "-4", "25", ""]):
                self.assertEqual(_prompt_int("Pain: ", 5, 0, 10), 5)
                self.assertEqual(_prompt_int("Pain: ", 5, 0, 10), 0)
                self.assertEqual(_prompt_int("Pain: ", 5, 0, 10), 10)
                self.assertEqual(_prompt_int("Pain: ", 5, 0, 10), 5)
            with unittest.mock.patch("builtins.input", side_effect=EOFError):
                self.assertEqual(_prompt_int("Pain: ", 4, 0, 10), 4)
        stderr_text = err_buf.getvalue()
        self.assertIn("Non-integer input 'abc'", stderr_text)
        self.assertIn("clamped to 0", stderr_text)
        self.assertIn("clamped to 10", stderr_text)
        self.assertIn("EOF received", stderr_text)

    def test_cli_modes_and_interactive_branches_with_session_persistence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_buf = io.StringIO()
            err_buf = io.StringIO()
            with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(err_buf):
                self.assertEqual(
                    run_cli(["--mode", "summary", "--session-log-dir", tmpdir]), 0
                )
                self.assertEqual(
                    run_cli(["--mode", "loop-interrupt", "--session-log-dir", tmpdir]), 0
                )

                # Branch 1: Interactive happy path (SUD 6 -> 3 -> 0, VOC -> 7, persisted to JSONL)
                with unittest.mock.patch(
                    "builtins.input",
                    side_effect=[
                        "1",
                        "3",
                        "Memory feels further away",
                        "3",
                        "Chest feels lighter",
                        "0",
                        "7",
                    ],
                ):
                    self.assertEqual(
                        run_cli(["--mode", "interactive", "--session-log-dir", tmpdir]), 0
                    )

                # Branch 2: Interactive pre-session Auto-Stop (Target 4 requires clinician / SUD 8)
                with unittest.mock.patch("builtins.input", side_effect=["4", "3"]):
                    self.assertEqual(
                        run_cli(["--mode", "interactive", "--session-log-dir", tmpdir]), 0
                    )

                # Branch 3: Interactive Level-7 Caution declined by user ('n')
                with unittest.mock.patch("builtins.input", side_effect=["3", "3", "n"]):
                    self.assertEqual(
                        run_cli(["--mode", "interactive", "--session-log-dir", tmpdir]), 0
                    )

                # Branch 4: Interactive Level-7 Caution accepted ('y') -> mid-session spike to 8
                with unittest.mock.patch(
                    "builtins.input",
                    side_effect=["3", "3", "y", "Sudden wave of grief", "8"],
                ):
                    self.assertEqual(
                        run_cli(["--mode", "interactive", "--session-log-dir", tmpdir]), 0
                    )

                # Simulate-session mode also persists to sessions.jsonl
                self.assertEqual(
                    run_cli(["--mode", "simulate-session", "--session-log-dir", tmpdir]), 0
                )

            log_file = os.path.join(tmpdir, "sessions.jsonl")
            self.assertTrue(os.path.isfile(log_file))
            with open(log_file, "r", encoding="utf-8") as f:
                lines = [json.loads(line) for line in f if line.strip()]
            self.assertEqual(len(lines), 5)
            self.assertTrue(all(entry["closure_achieved"] for entry in lines))


if __name__ == "__main__":
    unittest.main()

