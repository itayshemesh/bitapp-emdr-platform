"""Cost, Frequency, and Modality Analyzer for Bi-Tapp Online Human vs Non-Human EMDR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class EMDROptionComparison:
    """Structured comparison entry for an online EMDR treatment option using Bi-Tapp."""

    option_id: str
    category: str  # "NON_HUMAN" | "HUMAN_TELEHEALTH" | "HYBRID_STEPPED_CARE"
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
            option_id="OPT-NONHUMAN-BITAPP-OPEN",
            category="NON_HUMAN",
            name="Bi-Tapp App + Custom Open-Source BLS Protocol Engine",
            bi_tapp_integration=(
                "Direct Bluetooth pairing to iOS/Android Bi-Tapp app; software guides 8-phase "
                "state machine, exact speed/intensity presets, and 3-set safety circuit breakers."
            ),
            monthly_cost_usd_range=(0, 0),
            per_session_cost_usd_range=(0, 0),
            recommended_frequency=(
                "Daily 10-15m resourcing (Speed 2-3) + on-demand rumination interruption + "
                "1x/week structured session for SUD <= 6 targets."
            ),
            clinical_safety_tier="MEDIUM (Enforces software circuit-breaker at SUD >= 7)",
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
            name="EMDRIA-Certified Telehealth Therapist via remotEMDR + Bi-Tapp",
            bi_tapp_integration=(
                "Client enables 'Allow Provider Control' in Bi-Tapp app and shares the 5-character "
                "Provider Setup Code; therapist remotely controls tapper speed/intensity live."
            ),
            monthly_cost_usd_range=(0, 960),
            per_session_cost_usd_range=(0, 240),
            recommended_frequency="1x/week (60-90 min session) for 6-12 weeks.",
            clinical_safety_tier="HIGH (Live clinical co-regulation & cognitive interweaves)",
            best_for=(
                "Core attachment wounds (SUD >= 7), deep breakup grief, and ongoing pain/guilt "
                "around living apart from 3 children."
            ),
        ),
        EMDROptionComparison(
            option_id="OPT-HYBRID-STEPPED-CARE",
            category="HYBRID_STEPPED_CARE",
            name="Hybrid Protocol: Daily Non-Human Bi-Tapp + Weekly Human Telehealth",
            bi_tapp_integration=(
                "Local Bi-Tapp app + Custom Framework for daily loop-breaking/RDI; 5-character "
                "remotEMDR provider code for weekly human telehealth reprocessing."
            ),
            monthly_cost_usd_range=(0, 240),
            per_session_cost_usd_range=(0, 60),
            recommended_frequency=(
                "Daily 10m resourcing + on-demand loop breaker + 1x/week 60-90m human session."
            ),
            clinical_safety_tier="OPTIMAL (Combines 24/7 somatic regulation with clinical safety)",
            best_for=(
                "Fastest, safest resolution of 2.5-year ex-partner rumination while building "
                "long-term resilience around living apart from 3 children."
            ),
        ),
    ]


def build_treatment_schedule_and_cost_report(
    include_wristbands: bool = True,
    include_wall_charger: bool = False,
    international_shipping: bool = False,
    telehealth_sessions_count: int = 8,
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
        "recommended_weekly_cadence": {
            "daily_resourcing_minutes": 15,
            "on_demand_loop_interruption_minutes": 10,
            "active_reprocessing_sessions_per_week": 1,
            "reprocessing_session_duration_minutes": 75,
            "mandatory_reconsolidation_rest_hours": 48,
        },
    }
