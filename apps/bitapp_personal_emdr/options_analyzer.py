"""Cost, Frequency, and Modality Analyzer for Bi-Tapp Online Human vs Non-Human EMDR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class EMDROptionComparison:
    """Structured comparison entry for an online EMDR treatment option using Bi-Tapp."""

    option_id: str
    category: str  # "SOLO_FIRST_PRIMARY" | "NON_HUMAN" | "HUMAN_TELEHEALTH" | "HYBRID_STEPPED_CARE"
    name: str
    bi_tapp_integration: str
    monthly_cost_usd_range: tuple[int, int]
    per_session_cost_usd_range: tuple[int, int]
    recommended_frequency: str
    clinical_safety_tier: str
    best_for: str


def get_emdr_options_catalog() -> List[EMDROptionComparison]:
    """Returns the verified catalog of Online Non-Human and Online Human EMDR options."""
    return [
        EMDROptionComparison(
            option_id="OPT-SOLO-FIRST-STEPPED",
            category="SOLO_FIRST_PRIMARY",
            name="[SELECTED PRIMARY PLAN] Try Solo First (Weeks 1-4) -> Human Only If Stuck",
            bi_tapp_integration=(
                "Start 100% solo with Bi-Tapp app + this open-source app (Exact starting presets "
                "+ safe ranges). Escalate to a human therapist via 5-character remotEMDR code only "
                "if memories stay stuck after 3 rounds or hit Level 8+ auto-stop."
            ),
            monthly_cost_usd_range=(0, 0),
            per_session_cost_usd_range=(0, 0),
            recommended_frequency=(
                "Daily 10-15m calming/resourcing (Start Speed 2-3) + on-demand loop breaker + "
                "1x/week solo memory session (Start Speed 7, 35s rounds; 1-6 normal, 7 caution, "
                "8+ auto-stop)."
            ),
            clinical_safety_tier=(
                "TWO-STAGE SAFETY GATE (Levels 1-6 Normal, Level 7 Caution Prompt, Level 8+ Auto-Stop)"
            ),
            best_for=(
                "Zero-monthly-cost starting plan: break daily ex-girlfriend thought loops and "
                "process manageable memories solo first, reserving paid/EAP human therapy only "
                "for memories that refuse to budge."
            ),
        ),
        EMDROptionComparison(
            option_id="OPT-NONHUMAN-BITAPP-OPEN",
            category="NON_HUMAN",
            name="Bi-Tapp App + Custom Open-Source BLS Protocol Engine (Standalone)",
            bi_tapp_integration=(
                "Direct Bluetooth pairing to iOS/Android Bi-Tapp app; software guides 8-phase "
                "state machine, exact speed/intensity presets, and 3-set safety circuit breakers."
            ),
            monthly_cost_usd_range=(0, 0),
            per_session_cost_usd_range=(0, 0),
            recommended_frequency=(
                "Daily 10-15m resourcing (Speed 2-3) + on-demand rumination interruption + "
                "1x/week structured session (Levels 1-6 normal, Level 7 caution)."
            ),
            clinical_safety_tier="MEDIUM-HIGH (Warning at Level 7, Auto-Stop at Level 8+)",
            best_for=(
                "Acute breakup thought-loop interruption, Phase 2 Safe Place/Container RDI, "
                "and mild-to-moderate discrete breakup memories."
            ),
        ),
        EMDROptionComparison(
            option_id="OPT-NONHUMAN-VIRTUALEMDR",
            category="NON_HUMAN",
            name="VirtualEMDR / Commercial Self-Guided Web Program + Bi-Tapp",
            bi_tapp_integration=(
                "User mutes web visual/audio stimulus and manually runs Bi-Tapp tappers during "
                "timed web desensitization sets."
            ),
            monthly_cost_usd_range=(69, 79),
            per_session_cost_usd_range=(15, 20),
            recommended_frequency="1x/week reprocessing + 2-3x/week grounding.",
            clinical_safety_tier="LOW-MEDIUM (Static scripts; no dynamic attachment interweaves)",
            best_for="Structured web worksheets for single-incident mild stressors.",
        ),
        EMDROptionComparison(
            option_id="OPT-HUMAN-TELEHEALTH-REMOTEMDR",
            category="HUMAN_TELEHEALTH",
            name="EMDRIA-Certified Telehealth Therapist via remotEMDR + Bi-Tapp (Backup If Stuck)",
            bi_tapp_integration=(
                "Client enables 'Allow Provider Control' in Bi-Tapp app and shares the 5-character "
                "Provider Setup Code; therapist remotely controls tapper speed/intensity live."
            ),
            monthly_cost_usd_range=(0, 960),
            per_session_cost_usd_range=(0, 240),
            recommended_frequency="1x/week (60-90 min session) if solo memories stay stuck.",
            clinical_safety_tier="HIGH (Live clinical co-regulation & cognitive interweaves)",
            best_for=(
                "Memories that hit the Level 8+ auto-stop, stay stuck after 3 solo rounds, or "
                "deep ongoing grief around living apart from 3 children."
            ),
        ),
        EMDROptionComparison(
            option_id="OPT-HYBRID-STEPPED-CARE",
            category="HYBRID_STEPPED_CARE",
            name="Optional Phase-2 Escalation: Daily Solo Bi-Tapp + Weekly Human Telehealth",
            bi_tapp_integration=(
                "Local Bi-Tapp app + Custom Framework for daily loop-breaking/RDI; 5-character "
                "remotEMDR provider code for weekly human telehealth reprocessing if needed."
            ),
            monthly_cost_usd_range=(0, 240),
            per_session_cost_usd_range=(0, 60),
            recommended_frequency=(
                "Daily 10m resourcing + on-demand loop breaker + 1x/week 60-90m human session."
            ),
            clinical_safety_tier="OPTIMAL (Combines 24/7 somatic regulation with clinical safety)",
            best_for=(
                "Escalation path if Weeks 1-4 solo sessions leave high-pain core memories "
                "(Level 8+) unresolved."
            ),
        ),
    ]


def build_treatment_schedule_and_cost_report(
    include_wristbands: bool = True,
    include_wall_charger: bool = False,
    international_shipping: bool = False,
    telehealth_sessions_count: int = 0,
    per_session_copay_usd: int = 0,
) -> Dict[str, object]:
    """Calculates total hardware + treatment cost and weekly schedule parameters."""
    base_kit_usd = 277
    wristbands_usd = 20 if include_wristbands else 0
    charger_usd = 15 if include_wall_charger else 0
    shipping_usd = 50 if international_shipping else 12
    hardware_total_usd = base_kit_usd + wristbands_usd + charger_usd + shipping_usd
    therapy_total_usd = telehealth_sessions_count * per_session_copay_usd

    return {
        "primary_strategy": "Try Solo First (Weeks 1-4, $0 session cost); Human Therapist Only If Stuck",
        "hardware_kit_url": "https://bi-tapp.com/",
        "hardware_breakdown_usd": {
            "base_kit": base_kit_usd,
            "wristbands_pair": wristbands_usd,
            "wall_charger": charger_usd,
            "shipping_estimate": shipping_usd,
            "total_hardware_usd": hardware_total_usd,
        },
        "therapy_breakdown_usd": {
            "telehealth_sessions_count": telehealth_sessions_count,
            "per_session_copay_usd": per_session_copay_usd,
            "total_therapy_usd": therapy_total_usd,
            "custom_framework_subscription_usd": 0,
        },
        "grand_total_estimated_usd": hardware_total_usd + therapy_total_usd,
        "safety_gate_rules": {
            "normal_solo_levels": "1 to 6",
            "caution_warning_level": "7 (shows caution prompt, user chooses whether to continue)",
            "auto_stop_levels": "8 to 10 (automatically stops and switches to Speed 2 calming)",
            "stagnation_auto_stop": "3 rounds in a row with no drop in pain level",
        },
        "recommended_weekly_cadence": {
            "daily_resourcing_minutes": 15,
            "on_demand_loop_interruption_minutes": 10,
            "active_reprocessing_sessions_per_week": 1,
            "reprocessing_session_duration_minutes": 75,
            "mandatory_reconsolidation_rest_hours": 48,
        },
    }
