"""Modelos de domínio: dispositivos de captura."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


class BackendKind(str, Enum):
    """Mecanismo de captura usado para obter frames da câmera."""

    EDSDK = "edsdk"
    OPENCV = "opencv"


@dataclass
class CameraDevice:
    """Descreve uma câmera/capturadora encontrada no scanner."""

    index: int
    backend: BackendKind
    name: str = "Unknown"
    detail: str = ""
    resolution: Optional[Tuple[int, int]] = None
    camera_ref: Optional[int] = field(default=None, repr=False)
    backend_hint: Optional[int] = field(default=None, repr=False)

    @property
    def label(self) -> str:
        parts = [self.name]
        if self.detail:
            parts.append(self.detail)
        if self.resolution:
            parts.append(f"{self.resolution[0]}x{self.resolution[1]}")
        return " ".join(parts)