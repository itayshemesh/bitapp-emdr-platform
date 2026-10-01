#!/usr/bin/env python3
"""Command-Line Interface for the Bi-Tapp Personal EMDR Treatment Companion."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from apps.bitapp_personal_emdr.bitapp_presets import (
    BITAPP_CLOSURE_CONTAINMENT_PRESET,
    BITAPP_INSTALLATION_PRESET,
    BITAPP_LOOP_INTERRUPTER_PRESET,
    BITAPP_PHASE2_RDI_PRESET,
    BITAPP_PHASE4_REPROCESSING_PRESET,
)
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
from framework.bls_protocol_engine.schemas import WindowOfToleranceCheck


def run_cli(argv: Optional[List[str]] = None) -> int:
    """Runs the Bi-Tapp Personal EMDR CLI."""
    parser = argparse.ArgumentParser(
        description="Bi-Tapp EMDR Guided Protocol & Cost/Frequency Companion"
    )
    parser.add_argument(
        "--mode",
        choices=["summary", "loop-interrupt", "simulate-session"],
        default="summary",
        help="Execution mode to run.",
    )
    args = parser.parse_args(argv)

    adapter = BiTappCompanionAdapter()

    if args.mode == "summary":
        report = build_treatment_schedule_and_cost_report()
        options = [o.name for o in get_emdr_options_catalog()]
        print(
            json.dumps(
                {
                    "status": "OK",
                    "options_evaluated": options,
                    "cost_and_schedule_report": report,
                    "breakup_targets_count": len(get_breakup_rumination_target_pack()),
                    "children_rdi_targets_count": len(get_children_separation_rdi_pack()),
                },
                indent=2,
            )
        )
        return 0

    if args.mode == "loop-interrupt":
        receipt = adapter.configure_and_prompt(BITAPP_LOOP_INTERRUPTER_PRESET)
        print(receipt.user_action_instruction)
        return 0

    if args.mode == "simulate-session":
        target = get_breakup_rumination_target_pack()[0]
        wot = WindowOfToleranceCheck(
            dissociation_score=1,
            emotional_overwhelm_score=3,
            safe_place_established=True,
            container_exercise_ready=True,
            human_clinician_present=False,
        )
        engine = ProtocolEngine(adapter=adapter)
        pre_eval = engine.start_session(target, wot)
        if not pre_eval.safe_to_proceed:
            sys.stderr.write(f"[cli] Session gated to Phase 2: {pre_eval.trigger_reason}\n")
            return 1

        for new_sud in (4, 2, 1):
            engine.execute_stimulation_set(
                bls_config=BITAPP_PHASE4_REPROCESSING_PRESET,
                post_set_observation=f"Associative shift; SUD dropped to {new_sud}",
                new_sud=new_sud,
                new_voc=5,
            )
        engine.execute_stimulation_set(
            bls_config=BITAPP_INSTALLATION_PRESET,
            post_set_observation="Positive cognition feels true today.",
            new_sud=0,
            new_voc=7,
            somatic_tension_clear=True,
        )
        summary = engine.complete_closure(
            BITAPP_CLOSURE_CONTAINMENT_PRESET,
            note="Target resolved to SUD=0, VOC=7 with clear body scan.",
        )
        print(
            json.dumps(
                {
                    "session_id": summary.session_id,
                    "target_node_id": summary.target_node_id,
                    "initial_sud": summary.initial_sud,
                    "final_sud": summary.final_sud,
                    "final_voc": summary.final_voc,
                    "closure_achieved": summary.closure_achieved,
                },
                indent=2,
            )
        )
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
