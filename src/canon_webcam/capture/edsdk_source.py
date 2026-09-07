"""Fonte de captura via EDSDK (Live View da Canon)."""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from canon_webcam.capture.base import CaptureSource
from canon_webcam.domain.devices import CameraDevice
from canon_webcam.sdk.canon_edsdk import CanonEDSDK


class EdsdkSource(CaptureSource):
    def __init__(self, device: CameraDevice, dll_path: str = ""):
        self._device = device
        self._dll_path = dll_path
        self._sdk: Optional[CanonEDSDK] = None
        self._live_view_started = False

    @property
    def device(self) -> CameraDevice:
        return self._device

    @property
    def sdk(self) -> Optional[CanonEDSDK]:
        """SDK aberto (usado pelo painel de controles de câmera)."""
        return self._sdk

    def open(self) -> bool:
        if self._sdk is not None:
            self._sdk.initialize()
            if self._sdk.is_connected:
                return True

        sdk = CanonEDSDK(self._dll_path)
        sdk.initialize()
        sdk.connect(self._device.index)
        self._sdk = sdk

        try:
            sdk.start_live_view()
            self._live_view_started = True
        except Exception:
            self._live_view_started = False
        return True

    def read(self) -> Optional[np.ndarray]:
        if self._sdk is None or not self._sdk.is_connected:
            return None
        if not self._live_view_started:
            try:
                self._sdk.start_live_view()
                self._live_view_started = True
            except Exception:
                return None
        return self._sdk.capture_live_view_frame()

    def close(self) -> None:
        if self._sdk is not None:
            try:
                self._sdk.disconnect()
                self._sdk.terminate()
            except Exception:
                pass
            self._sdk = None
        self._live_view_started = False

    @property
    def is_open(self) -> bool:
        return self._sdk is not None and self._sdk.is_connected