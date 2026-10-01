"""Hardware and sensory modality adapters for Bilateral Stimulation (BLS)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

from framework.bls_protocol_engine.schemas import BilateralStimulationConfig, ModalityType


@dataclass(frozen=True)
class AdapterDispatchReceipt:
    """Structured receipt emitted when an adapter configures or runs a stimulation set."""

    modality: ModalityType
    speed_level: int
    intensity_level: int
    duration_seconds: int
    user_action_instruction: str
    remote_bridge_active: bool = False


class StimulationAdapter(ABC):
    """Abstract base class for hardware or software bilateral stimulation drivers."""

    @abstractmethod
    def configure_and_prompt(self, config: BilateralStimulationConfig) -> AdapterDispatchReceipt:
        """Configures the bilateral stimulation device/channel and returns instructions."""


class BiTappCompanionAdapter(StimulationAdapter):
    """Adapter for the Bi-Tapp Bluetooth tactile tappers (https://bi-tapp.com/).

    Supports both:
    1. Standalone Local App Control (user sets speed/intensity sliders in iOS/Android Bi-Tapp app).
    2. Remote Therapist Bridge (5-character Provider Setup Code linked to remotEMDR.com).
    """

    def configure_and_prompt(self, config: BilateralStimulationConfig) -> AdapterDispatchReceipt:
        if config.provider_control_code:
            instruction = (
                f"[Bi-Tapp Telehealth Mode] Open Bi-Tapp app -> Settings -> enable "
                f"'Allow Provider Control' and share 5-char code '{config.provider_control_code}' "
                f"with your therapist on remotEMDR (Target Speed: {config.speed_level}, "
                f"Intensity: {config.intensity_level}, Set: {config.set_duration_seconds}s)."
            )
            return AdapterDispatchReceipt(
                modality=ModalityType.TACTILE_BITAPP,
                speed_level=config.speed_level,
                intensity_level=config.intensity_level,
                duration_seconds=config.set_duration_seconds,
                user_action_instruction=instruction,
                remote_bridge_active=True,
            )

        instruction = (
            f"[Bi-Tapp Local Mode ({config.mode_label})] Ensure both Bi-Tapp tappers are paired "
            f"(blue LED flashing). In the Bi-Tapp mobile app, set Rate of Speed = "
            f"{config.speed_level}/10 and Rate of Intensity = {config.intensity_level}/10. "
            f"Run alternating tactile stimulation for {config.set_duration_seconds} seconds, "
            f"then tap Pause and take a slow breath."
        )
        return AdapterDispatchReceipt(
            modality=ModalityType.TACTILE_BITAPP,
            speed_level=config.speed_level,
            intensity_level=config.intensity_level,
            duration_seconds=config.set_duration_seconds,
            user_action_instruction=instruction,
            remote_bridge_active=False,
        )


class AudioVisualSimulatedAdapter(StimulationAdapter):
    """Fallback adapter for binaural audio or visual saccade stimulation."""

    def configure_and_prompt(self, config: BilateralStimulationConfig) -> AdapterDispatchReceipt:
        hz = round(0.4 + (config.speed_level * 0.18), 2)
        instruction = (
            f"[Audio/Visual BLS ({config.modality.value})] Running alternating bilateral pulse "
            f"at {hz} Hz (Speed {config.speed_level}/10, Intensity {config.intensity_level}/10) "
            f"for {config.set_duration_seconds} seconds."
        )
        return AdapterDispatchReceipt(
            modality=config.modality,
            speed_level=config.speed_level,
            intensity_level=config.intensity_level,
            duration_seconds=config.set_duration_seconds,
            user_action_instruction=instruction,
            remote_bridge_active=False,
        )
