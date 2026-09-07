"""Fonte de captura via OpenCV (DirectShow/MSMF)."""

from __future__ import annotations

from typing import List, Optional, Tuple

import cv2
import numpy as np

from canon_webcam.capture.base import CaptureSource
from canon_webcam.domain.devices import CameraDevice


class OpenCVSource(CaptureSource):
    def __init__(self, device: CameraDevice, width: int = 1280, height: int = 720):
        self._device = device
        self._width = width
        self._height = height
        self._cap = None

    @property
    def device(self) -> CameraDevice:
        return self._device

    def _backend_order(self) -> List[int]:
        if self._device.backend_hint is not None:
            return [self._device.backend_hint, cv2.CAP_ANY]
        return [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]

    def open(self) -> bool:
        if self._cap is not None and self._cap.isOpened():
            return True

        for backend in self._backend_order():
            cap = None
            try:
                if backend == cv2.CAP_ANY:
                    cap = cv2.VideoCapture(self._device.index)
                else:
                    cap = cv2.VideoCapture(self._device.index, backend)
                if cap.isOpened():
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
                    self._cap = cap
                    return True
                if cap is not None:
                    cap.release()
            except Exception:
                if cap is not None:
                    cap.release()
        return False

    def read(self) -> Optional[np.ndarray]:
        if self._cap is None or not self._cap.isOpened():
            return None
        ret, frame = self._cap.read()
        return frame if ret else None

    def close(self) -> None:
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

    @property
    def is_open(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    @property
    def resolution(self) -> Optional[Tuple[int, int]]:
        if not self._cap or not self._cap.isOpened():
            return None
        w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (w, h)