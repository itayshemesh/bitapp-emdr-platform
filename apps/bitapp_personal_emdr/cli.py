#!/usr/bin/env python3
"""Command-Line Interface for the Bi-Tapp Personal EMDR Treatment Companion."""

from __future__ import annotations

import argparse
from dataclasses import asdict
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


def _prompt_int(prompt_text: str, default_val: int, min_val: int, max_val: int) -> int:
    """Reads a bounded integer from stdin, falling back to default_val on EOF or empty input."""
    try:
        raw = input(prompt_text).strip()
    except EOFError:
        return default_val
    if not raw:
        return default_val
    try:
        parsed = int(raw)
    except ValueError:
        return default_val
    return max(min_val, min(max_val, parsed))


def run_cli(argv: Optional[List[str]] = None) -> int:
    """Runs the Bi-Tapp Personal EMDR CLI."""
    parser = argparse.ArgumentParser(
        description="Bi-Tapp EMDR Guided Protocol & Cost/Frequency Companion"
    )
    parser.add_argument(
        "--mode",
        choices=["summary", "loop-interrupt", "interactive", "simulate-session"],
        default="summary",
        help="Execution mode to run.",
    )
    args = parser.parse_args(argv)

    adapter = BiTappCompanionAdapter()

    if args.mode == "summary":
        report = build_treatment_schedule_and_cost_report()
        options = [o.name for o in get_emdr_options_catalog()]
        presets = {
            "mode_a_loop_interrupter": asdict(BITAPP_LOOP_INTERRUPTER_PRESET),
            "mode_b_phase2_rdi": asdict(BITAPP_PHASE2_RDI_PRESET),
            "mode_c_phase4_reprocessing": asdict(BITAPP_PHASE4_REPROCESSING_PRESET),
            "mode_d1_phase5_installation": asdict(BITAPP_INSTALLATION_PRESET),
            "mode_d2_phase7_closure": asdict(BITAPP_CLOSURE_CONTAINMENT_PRESET),
        }
        print(
            json.dumps(
                {
                    "status": "OK",
                    "options_evaluated": options,
                    "bitapp_mode_presets": presets,
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
        steps = [
            receipt.user_action_instruction,
            "Step 1: Turn on Bi-Tapp in your wristbands or pockets at Speed 2, Intensity 3 (10 mins / 600s; Range: Speed 1-3, Intensity 2-4, 5-15 mins / 300-900s).",
            "Step 2: Tell yourself: 'This is a 2.5-year-old memory firing, not an emergency today.'",
            "Step 3: Breathe in for 4 seconds, out for 6 seconds while feeling the gentle left-right pulse until the pain drops to 2 or below.",
        ]
        print("\n".join(steps))
        return 0

    if args.mode == "interactive":
        targets = get_breakup_rumination_target_pack()
        print("=== Bi-Tapp Interactive Solo EMDR Coach (Zero Website Registration Needed) ===")
        print("Phone Setup: Open the free Bi-Tapp app on your iPhone/Android and pair both tappers.")
        for idx, t in enumerate(targets, start=1):
            print(f"  [{idx}] {t.title} (Initial Pain/SUD: {t.initial_sud}/10)")
        choice = _prompt_int("Select target memory number [default=1]: ", 1, 1, len(targets))
        target = targets[choice - 1]
        overwhelm = _prompt_int(
            "Current emotional overwhelm before starting (0-10) [default=3]: ", 3, 0, 10
        )

        wot = WindowOfToleranceCheck(
            dissociation_score=1,
            emotional_overwhelm_score=overwhelm,
            safe_place_established=True,
            container_exercise_ready=True,
            human_clinician_present=False,
        )
        engine = ProtocolEngine(adapter=adapter)
        pre_eval = engine.start_session(target, wot)
        if not pre_eval.safe_to_proceed:
            print(f"[Auto-Stop Safety Gate] {pre_eval.trigger_reason}")
            print(f"Action: {pre_eval.interweave_or_grounding_prompt}")
            return 0

        if pre_eval.caution_warning:
            print(f"[Caution Warning] {pre_eval.caution_warning}")
            try:
                ans = input("Continue solo session? [y/N]: ").strip().lower()
            except EOFError:
                ans = "y"
            if ans not in ("y", "yes"):
                summary = engine.complete_closure(
                    BITAPP_CLOSURE_CONTAINMENT_PRESET,
                    note="User chose calming closure at Level-7 caution prompt.",
                )
                print(json.dumps({"session_id": summary.session_id, "closure_achieved": True}))
                return 0

        round_num = 1
        while True:
            mode_c_prompt = adapter.configure_and_prompt(BITAPP_PHASE4_REPROCESSING_PRESET)
            print(f"\n--- Round {round_num} ---")
            print(mode_c_prompt.user_action_instruction)
            try:
                obs = input("After 35s round, what do you notice now? ").strip() or "Shifted"
            except EOFError:
                obs = "Shifted"
            new_sud = _prompt_int("Current pain level (0-10) [default=0]: ", 0, 0, 10)
            _, step_eval = engine.execute_stimulation_set(
                bls_config=BITAPP_PHASE4_REPROCESSING_PRESET,
                post_set_observation=obs,
                new_sud=new_sud,
                new_voc=5,
            )
            if not step_eval.safe_to_proceed:
                print(f"[Auto-Stop Safety Gate] {step_eval.trigger_reason}")
                print(f"Action: {step_eval.interweave_or_grounding_prompt}")
                break
            if step_eval.caution_warning:
                print(f"[Caution Warning] {step_eval.caution_warning}")
            if new_sud <= 1:
                print("\nPain dropped to 0-1! Moving to Mode D1 (Lock In Positive Belief: Speed 4, Int 4, 25s)...")
                engine.execute_stimulation_set(
                    bls_config=BITAPP_INSTALLATION_PRESET,
                    post_set_observation="Locked in positive belief with clear body scan.",
                    new_sud=0,
                    new_voc=7,
                    somatic_tension_clear=True,
                )
                break
            round_num += 1

        summary = engine.complete_closure(
            BITAPP_CLOSURE_CONTAINMENT_PRESET,
            note="Interactive session closed with Mode D2 (Speed 2, Int 3, 60s).",
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
