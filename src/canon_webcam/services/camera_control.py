"""Controle de exposição e foco da câmera via EDSDK."""

from __future__ import annotations

from typing import Dict, List, Optional

from canon_webcam.domain.settings import EXPOSURE_SETTINGS, ConversionTable, ExposureSetting
from canon_webcam.sdk.canon_edsdk import CanonEDSDK
from canon_webcam.sdk.constants import kEdsEvfDriveLens_FAR1, kEdsEvfDriveLens_NEAR1


class CameraControl:
    """Abstrai leitura/escrita de ISO, Av, Tv e foco sobre o SDK."""

    def __init__(self, sdk: CanonEDSDK):
        self._sdk = sdk

    @property
    def sdk(self) -> CanonEDSDK:
        return self._sdk

    @property
    def available(self) -> bool:
        return self._sdk is not None and self._sdk.is_connected

    # ------------------------------------------------------------------
    # Valores
    # ------------------------------------------------------------------
    def current_raw(self, key: str) -> Optional[int]:
        setting = EXPOSURE_SETTINGS.get(key)
        if setting is None or not self.available:
            return None
        return self._sdk.get_property_u32(setting.property_id)

    def current_label(self, key: str) -> Optional[str]:
        setting = EXPOSURE_SETTINGS.get(key)
        if setting is None:
            return None
        raw = self.current_raw(key)
        if raw is None:
            return None
        return setting.table.label_for(raw) or f"0x{raw:04X}"

    def labels(self, key: str) -> List[str]:
        setting = EXPOSURE_SETTINGS.get(key)
        if setting is None:
            return []
        return setting.table.labels

    def set_by_label(self, key: str, label: str) -> int:
        setting = EXPOSURE_SETTINGS.get(key)
        if setting is None or not self.available:
            return 0x00000002
        code = setting.table.code_for(label)
        if code is None:
            return 0x00000002
        return self._sdk.set_property_u32(setting.property_id, code)

    def set_raw(self, key: str, raw: int) -> int:
        setting = EXPOSURE_SETTINGS.get(key)
        if setting is None or not self.available:
            return 0x00000002
        return self._sdk.set_property_u32(setting.property_id, raw)

    # ------------------------------------------------------------------
    # Foco
    # ------------------------------------------------------------------
    def focus_auto(self) -> int:
        if not self.available:
            return 0x00000002
        return self._sdk.auto_focus()

    def focus_near(self) -> int:
        if not self.available:
            return 0x00000002
        return self._sdk.drive_lens(kEdsEvfDriveLens_NEAR1)

    def focus_far(self) -> int:
        if not self.available:
            return 0x00000002
        return self._sdk.drive_lens(kEdsEvfDriveLens_FAR1)