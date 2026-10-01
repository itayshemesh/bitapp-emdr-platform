"""Specific Clinical Target Packs for 2.5-Year Breakup Rumination & 3-Children Separation."""

from __future__ import annotations

from typing import List

from framework.bls_protocol_engine.schemas import TargetMemoryNode


def get_breakup_rumination_target_pack() -> List[TargetMemoryNode]:
    """Returns the 3-Pronged / R-TEP Target Pack for 2.5-year ex-girlfriend looping thoughts."""
    return [
        TargetMemoryNode(
            node_id="BREAKUP-TRIGGER-01",
            cluster_name="2.5-Year Ex-Partner Breakup Rumination",
            title="Evening Quiet / Intrusive 'What If' Thought Loop",
            worst_image_cue="Checking phone or sitting in a quiet room replaying the final conversation",
            negative_cognition="I lost my chance at happiness and I cannot move on",
            positive_cognition="That chapter is over; I can build a meaningful present today",
            initial_voc=3,
            initial_sud=5,
            emotions=["longing", "anxiety", "regret"],
            somatic_location="solar plexus and throat",
            is_ongoing_stressor=False,
            requires_human_clinician=False,
        ),
        TargetMemoryNode(
            node_id="BREAKUP-SCENE-02",
            cluster_name="2.5-Year Ex-Partner Breakup Rumination",
            title="The Moment of Departure (2.5 Years Ago)",
            worst_image_cue="The exact moment she left and the realization the relationship was over",
            negative_cognition="I am replaceable and abandoned",
            positive_cognition="My worth is intact regardless of her choice; I survived and grew",
            initial_voc=2,
            initial_sud=6,
            emotions=["grief", "rejection", "helplessness"],
            somatic_location="heavy chest tightness",
            is_ongoing_stressor=False,
            requires_human_clinician=False,
        ),
        TargetMemoryNode(
            node_id="BREAKUP-CAUTION-02B",
            cluster_name="2.5-Year Ex-Partner Breakup Rumination",
            title="Sudden Anniversary / Reminder Wave (Level-7 Caution Gate Node)",
            worst_image_cue="Seeing an unexpected reminder of the relationship 2.5 years later",
            negative_cognition="I will never stop replaying what went wrong",
            positive_cognition="I can acknowledge the past pain and choose where my focus goes today",
            initial_voc=2,
            initial_sud=7,
            emotions=["ache", "frustration", "longing"],
            somatic_location="throat and upper chest",
            is_ongoing_stressor=False,
            requires_human_clinician=False,
        ),
        TargetMemoryNode(
            node_id="BREAKUP-TOUCHSTONE-03",
            cluster_name="2.5-Year Ex-Partner Breakup Rumination",
            title="Core Attachment Wound / High-Distress Abandonment Memory",
            worst_image_cue="Deepest wave of panic and aloneness when both family and relationship felt gone",
            negative_cognition="I am fundamentally alone",
            positive_cognition="I am connected, resilient, and capable of secure love",
            initial_voc=2,
            initial_sud=8,
            emotions=["deep grief", "abandonment panic"],
            somatic_location="pit of stomach and chest",
            is_ongoing_stressor=False,
            requires_human_clinician=True,
        ),
    ]


def get_children_separation_rdi_pack() -> List[TargetMemoryNode]:
    """Returns the Phase 2 RDI & Clinician-Assisted Pack for living apart from 3 children."""
    return [
        TargetMemoryNode(
            node_id="KIDS-RDI-ANCHOR-01",
            cluster_name="Parental Separation & Fatherhood Resilience (3 Children)",
            title="Fatherhood Connection Anchor (Phase 2 Resource Installation)",
            worst_image_cue="Transition moment after saying goodbye to the 3 kids",
            negative_cognition="Not living under the same roof means I am failing them",
            positive_cognition="I am their devoted, present father across every mile and every visit",
            initial_voc=4,
            initial_sud=7,
            emotions=["grief", "protective love", "guilt"],
            somatic_location="heart and shoulders",
            is_ongoing_stressor=True,
            requires_human_clinician=True,
        ),
    ]
