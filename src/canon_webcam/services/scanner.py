"""Scan de dispositivos de captura disponíveis."""

from __future__ import annotations

import time
from typing import List

import cv2

from canon_webcam.domain.devices import BackendKind, CameraDevice

BACKEND_NAMES = {cv2.CAP_MSMF: "MSMF", cv2.CAP_DSHOW: "DSHOW", cv2.CAP_ANY: "ANY"}
MAX_OPENCV_INDEX = 4


class CameraScanner:
    """Descobre webcams via OpenCV e (opcionalmente) câmeras Canon via EDSDK."""

    def __init__(self, include_edsdk: bool = False, edsdk_dll_path: str = ""):
        self._include_edsdk = include_edsdk
        self._edsdk_dll_path = edsdk_dll_path

    def scan(self) -> List[CameraDevice]:
        devices: List[CameraDevice] = []

        if self._include_edsdk:
            devices.extend(self._scan_edsdk())

        devices.extend(self._scan_opencv())
        return devices

    # ------------------------------------------------------------------
    def _scan_opencv(self) -> List[CameraDevice]:
        devices: List[CameraDevice] = []
        found: List[int] = []

        for i in range(MAX_OPENCV_INDEX):
            for backend in (cv2.CAP_MSMF, cv2.CAP_DSHOW):
                try:
                    cap = cv2.VideoCapture(i, backend)
                    if cap.isOpened():
                        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        backend_name = BACKEND_NAMES.get(backend, "?")
                        name = "Canon T5i (EOS Webcam Utility)" if i == 0 else f"Device {i}"
                        devices.append(CameraDevice(
                            index=i,
                            backend=BackendKind.OPENCV,
                            name=name,
                            detail=backend_name,
                            resolution=(w, h) if w and h else None,
                            backend_hint=backend,
                        ))
                        found.append(i)
                        cap.release()
                        break
                except Exception:
                    continue

        return devices

    def _scan_edsdk(self) -> List[CameraDevice]:
        try:
            from canon_webcam.sdk.canon_edsdk import CanonEDSDK

            sdk = CanonEDSDK(self._edsdk_dll_path)
            sdk.initialize()

            devices: List[CameraDevice] = []
            for attempt in range(5):
                cameras = sdk.get_camera_list()
                if cameras:
                    for i, cam in enumerate(cameras):
                        devices.append(CameraDevice(
                            index=i,
                            backend=BackendKind.EDSDK,
                            name=cam["name"],
                            detail=cam["body_id"],
                            camera_ref=cam["ref"],
                        ))
                    break
                print(f"[EDSDK] scan attempt {attempt + 1}: no cameras yet, retrying...")
                time.sleep(1.0)

            sdk.terminate()
            return devices
        except Exception as e:
            print(f"[Fallback] EDSDK not available: {e}")
            return []