"""Saída via pyvirtualcam (OBS Virtual Camera)."""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

from canon_webcam.output.base import VideoOutput

try:
    import pyvirtualcam
    HAS_PYVIRTUALCAM = True
except ImportError:
    HAS_PYVIRTUALCAM = False


class VirtualWebcam(VideoOutput):
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30):
        self._width = width
        self._height = height
        self._fps = fps
        self._cam = None
        self._active = False
        self._backend = None

    def start(self, device: Optional[str] = None) -> bool:
        if not HAS_PYVIRTUALCAM:
            raise RuntimeError(
                "pyvirtualcam não instalado. Instale com: pip install pyvirtualcam\n"
                "Também é necessário o OBS Virtual Camera ou driver similar."
            )

        try:
            self._cam = pyvirtualcam.Camera(
                width=self._width,
                height=self._height,
                fps=self._fps,
                device=device,
            )
            self._active = True
            self._backend = self._cam.backend
            print(f"[VirtualCam] Started: {self._cam.device} ({self._backend})")
            return True
        except Exception as e:
            print(f"[VirtualCam] Failed to start: {e}")
            self._active = False
            return False

    def send(self, frame: np.ndarray) -> bool:
        if not self._active or self._cam is None:
            return False

        try:
            if frame is None:
                return False

            if frame.shape[1] != self._width or frame.shape[0] != self._height:
                frame = cv2.resize(frame, (self._width, self._height))

            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self._cam.send(rgb_frame)
            self._cam.sleep_until_next_frame()
            return True

        except Exception as e:
            print(f"[VirtualCam] Send error: {e}")
            return False

    def stop(self) -> None:
        if self._cam is not None:
            try:
                self._cam.close()
            except Exception:
                pass
            self._cam = None
        self._active = False
        print("[VirtualCam] Stopped")

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def backend_name(self) -> str:
        return self._backend or "None"

    @classmethod
    def available(cls) -> bool:
        return HAS_PYVIRTUALCAM

    @staticmethod
    def list_devices():
        if not HAS_PYVIRTUALCAM:
            return []
        try:
            return pyvirtualcam.device_list()
        except Exception:
            return []