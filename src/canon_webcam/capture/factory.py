"""Fábrica de fontes de captura a partir de um CameraDevice."""

from __future__ import annotations

from canon_webcam.capture.base import CaptureSource
from canon_webcam.capture.edsdk_source import EdsdkSource
from canon_webcam.capture.opencv_source import OpenCVSource
from canon_webcam.domain.devices import BackendKind, CameraDevice


def create_source(device: CameraDevice, dll_path: str = "") -> CaptureSource:
    if device.backend == BackendKind.EDSDK:
        return EdsdkSource(device, dll_path=dll_path)
    if device.backend == BackendKind.OPENCV:
        return OpenCVSource(device)
    raise ValueError(f"Backend desconhecido: {device.backend}")